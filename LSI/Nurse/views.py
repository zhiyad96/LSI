from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from LabTechnician.models import AssayMaster, OrderTransaction, Results
from Physician.models import PatientMaster
from accounts.models import User


class IsNurseOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in [User.Roles.NURSE, User.Roles.PHYSICIAN, User.Roles.ADMIN]


class NursePatientLookupAPIView(APIView):
    permission_classes = [IsNurseOrAdmin]

    def get(self, request):
        search = request.query_params.get("search", "").strip()
        queryset = PatientMaster.objects.all().order_by("patient_name")

        if search:
            queryset = queryset.filter(
                Q(mrn__icontains=search) | Q(patient_name__icontains=search)
            )

        patients = queryset[:50]
        data = [
            {
                "id": patient.id,
                "mrn": patient.mrn,
                "patient_name": patient.patient_name,
                "age": patient.age,
                "gender": patient.gender,
                "status": patient.status,
            }
            for patient in patients
        ]
        return Response({"success": True, "patients": data}, status=status.HTTP_200_OK)


class NurseAssayLookupAPIView(APIView):
    permission_classes = [IsNurseOrAdmin]

    def get(self, request):
        search = request.query_params.get("search", "").strip()
        queryset = (
            AssayMaster.objects.select_related("menu")
            .filter(status="Active")
            .order_by("assay_name")
        )

        if search:
            queryset = queryset.filter(
                Q(assay_code__icontains=search) | Q(assay_name__icontains=search)
            )

        assays = queryset[:100]
        data = [
            {
                "id": assay.id,
                "assay_code": assay.assay_code,
                "assay_name": assay.assay_name,
                "menu_name": assay.menu.menu_name,
                "sample_type": assay.sample_type,
                "tat_hours": assay.tat_hours,
            }
            for assay in assays
        ]
        return Response({"success": True, "assays": data}, status=status.HTTP_200_OK)


class NurseOrderCreateAPIView(APIView):
    permission_classes = [IsNurseOrAdmin]

    def post(self, request):
        patient_id = request.data.get("patient_id")
        assay_ids = request.data.get("assays", [])
        notes = request.data.get("notes", "")

        if not patient_id:
            return Response(
                {"success": False, "message": "patient_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(assay_ids, list) or not assay_ids:
            return Response(
                {"success": False, "message": "assays must be a non-empty array."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            patient = PatientMaster.objects.get(id=patient_id)
        except PatientMaster.DoesNotExist:
            return Response(
                {"success": False, "message": "Patient not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        selected_assays = AssayMaster.objects.filter(id__in=assay_ids, status="Active")
        if selected_assays.count() != len(set(assay_ids)):
            return Response(
                {
                    "success": False,
                    "message": "One or more selected assays are invalid or inactive.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        profile = getattr(request.user, "user_master", None)
        if not profile:
            return Response(
                {"success": False, "message": "User profile not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        last_order = OrderTransaction.objects.order_by("id").last()
        next_id = last_order.id + 1 if last_order else 1
        order_no = f"ORD-{timezone.now().year}{str(next_id).zfill(4)}"

        with transaction.atomic():
            order = OrderTransaction.objects.create(
                order_no=order_no,
                patient=patient,
                ordered_by=profile,
                ordered_at=timezone.now(),
                order_status=OrderTransaction.Status.ORDERED,
                notes=notes,
            )

            for assay in selected_assays:
                Results.objects.create(
                    order=order,
                    assay=assay,
                    result_value="",
                    entered_by=profile,
                    entered_at=timezone.now(),
                )

        return Response(
            {
                "success": True,
                "message": "Lab order placed successfully.",
                "order": {
                    "id": order.id,
                    "order_no": order.order_no,
                    "patient_name": patient.patient_name,
                    "patient_mrn": patient.mrn,
                    "order_status": order.get_order_status_display(),
                    "ordered_at": order.ordered_at,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class NurseCompletedReportsAPIView(APIView):
    permission_classes = [IsNurseOrAdmin]

    def get(self, request):
        search = request.query_params.get("search", "").strip()
        queryset = (
            OrderTransaction.objects.select_related("patient")
            .prefetch_related("results")
            .filter(order_status=OrderTransaction.Status.COMPLETED)
            .order_by("-updated_at")
        )

        if search:
            queryset = queryset.filter(
                Q(order_no__icontains=search)
                | Q(patient__patient_name__icontains=search)
                | Q(patient__mrn__icontains=search)
            )

        reports = queryset[:100]
        data = [
            {
                "id": report.id,
                "order_no": report.order_no,
                "patient_name": report.patient.patient_name,
                "patient_mrn": report.patient.mrn,
                "ordered_at": report.ordered_at,
                "completed_at": report.updated_at,
                "tests_count": report.results.count(),
            }
            for report in reports
        ]
        return Response({"success": True, "reports": data}, status=status.HTTP_200_OK)


class NurseReportDetailAPIView(APIView):
    permission_classes = [IsNurseOrAdmin]

    def get(self, request, order_id):
        try:
            order = (
                OrderTransaction.objects.select_related("patient", "ordered_by")
                .prefetch_related("results__assay")
                .get(id=order_id, order_status=OrderTransaction.Status.COMPLETED)
            )
        except OrderTransaction.DoesNotExist:
            return Response(
                {"success": False, "message": "Completed report not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = {
            "id": order.id,
            "order_no": order.order_no,
            "ordered_at": order.ordered_at,
            "completed_at": order.updated_at,
            "notes": order.notes,
            "patient": {
                "id": order.patient.id,
                "mrn": order.patient.mrn,
                "patient_name": order.patient.patient_name,
                "age": order.patient.age,
                "gender": order.patient.gender,
            },
            "results": [
                {
                    "id": result.id,
                    "assay_code": result.assay.assay_code,
                    "assay_name": result.assay.assay_name,
                    "result_value": result.result_value,
                    "unit": result.unit or result.assay.unit,
                    "normal_range": result.normal_range or result.assay.normal_range,
                    "flag": result.flag,
                    "remarks": result.remarks,
                }
                for result in order.results.all()
            ],
        }

        return Response({"success": True, "report": data}, status=status.HTTP_200_OK)
