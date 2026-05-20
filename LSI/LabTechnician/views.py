from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import TestMenuMaster, AssayMaster, OrderTransaction, Results
from .serializers import TestMenuSerializer, AssaySerializer, OrderTransactionSerializer
from accounts.models import User

# --- PERMISSIONS ---
class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == User.Roles.ADMIN

class IsAdminPhysicianOrNurse(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in [User.Roles.ADMIN, User.Roles.PHYSICIAN, User.Roles.NURSE]

# --- TEST MENU VIEWS ---

class TestMenuListCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        menus = TestMenuMaster.objects.all().order_by('menu_name')
        serializer = TestMenuSerializer(menus, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TestMenuSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TestMenuDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return TestMenuMaster.objects.get(pk=pk)
        except TestMenuMaster.DoesNotExist:
            return None

    def get(self, request, pk):
        menu = self.get_object(pk)
        if not menu:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TestMenuSerializer(menu)
        return Response(serializer.data)

    def put(self, request, pk):
        menu = self.get_object(pk)
        if not menu:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TestMenuSerializer(menu, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        menu = self.get_object(pk)
        if not menu:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TestMenuSerializer(menu, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        menu = self.get_object(pk)
        if not menu:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        menu.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# --- ASSAY VIEWS ---

class AssayListCreateView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        qs = AssayMaster.objects.select_related('menu').all().order_by('assay_name')
        search = self.request.query_params.get('search', None)
        menu_id = self.request.query_params.get('menu', None)
        if search:
            qs = qs.filter(Q(assay_code__icontains=search) | Q(assay_name__icontains=search))
        if menu_id:
            qs = qs.filter(menu_id=menu_id)
        return qs

    def get(self, request):
        assays = self.get_queryset()
        serializer = AssaySerializer(assays, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AssaySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AssayDetailView(APIView):
    permission_classes = [IsAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return AssayMaster.objects.select_related('menu').get(pk=pk)
        except AssayMaster.DoesNotExist:
            return None

    def get(self, request, pk):
        assay = self.get_object(pk)
        if not assay:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AssaySerializer(assay)
        return Response(serializer.data)

    def put(self, request, pk):
        assay = self.get_object(pk)
        if not assay:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AssaySerializer(assay, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        assay = self.get_object(pk)
        if not assay:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = AssaySerializer(assay, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        assay = self.get_object(pk)
        if not assay:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        assay.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# --- ORDER VIEWS ---

class OrderListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = OrderTransaction.objects.select_related('patient', 'ordered_by', 'collected_by').prefetch_related('results', 'results__assay').all().order_by('-ordered_at')
        status_filter = self.request.query_params.get('status', None)
        patient_id = self.request.query_params.get('patient', None)
        date = self.request.query_params.get('date', None)

        if status_filter:
            qs = qs.filter(order_status=status_filter)
        if patient_id:
            qs = qs.filter(patient_id=patient_id)
        if date:
            qs = qs.filter(ordered_at__date=date)
        return qs

    def get(self, request):
        orders = self.get_queryset()
        serializer = OrderTransactionSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        if request.user.role not in [User.Roles.ADMIN, User.Roles.PHYSICIAN, User.Roles.NURSE]:
            return Response({"message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        data = request.data
        patient_id = data.get('patient_id')
        notes = data.get('notes', '')
        assay_ids = data.get('assays', [])

        if not patient_id or not assay_ids:
            return Response({"message": "patient_id and assays array are required."}, status=status.HTTP_400_BAD_REQUEST)

        last_order = OrderTransaction.objects.order_by('id').last()
        next_id = last_order.id + 1 if last_order else 1
        order_no = f"ORD-{timezone.now().year}{str(next_id).zfill(4)}"

        profile = getattr(request.user, 'user_master', None)
        if not profile:
            return Response({"message": "User profile not found"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order = OrderTransaction.objects.create(
                order_no=order_no,
                patient_id=patient_id,
                ordered_by=profile,
                ordered_at=timezone.now(),
                order_status=OrderTransaction.Status.ORDERED,
                notes=notes
            )
            for a_id in assay_ids:
                Results.objects.create(
                    order=order,
                    assay_id=a_id,
                    result_value="",
                    entered_by=profile,
                    entered_at=timezone.now()
                )

        serializer = OrderTransactionSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class OrderDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return OrderTransaction.objects.select_related('patient', 'ordered_by', 'collected_by').prefetch_related('results', 'results__assay').get(pk=pk)
        except OrderTransaction.DoesNotExist:
            return None

    def get(self, request, pk):
        order = self.get_object(pk)
        if not order:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderTransactionSerializer(order)
        return Response(serializer.data)

    def put(self, request, pk):
        order = self.get_object(pk)
        if not order:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderTransactionSerializer(order, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        order = self.get_object(pk)
        if not order:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = OrderTransactionSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        order = self.get_object(pk)
        if not order:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class OrderCollectView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        if request.user.role not in [User.Roles.ADMIN, User.Roles.PHLEBOTOMIST]:
            return Response({"message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        try:
            order = OrderTransaction.objects.get(pk=pk)
        except OrderTransaction.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if order.order_status != OrderTransaction.Status.ORDERED:
            return Response({"message": "Order must be in Ordered status to collect."}, status=status.HTTP_400_BAD_REQUEST)

        profile = getattr(request.user, 'user_master', None)
        order.order_status = OrderTransaction.Status.COLLECTED
        order.collected_by = profile
        order.collected_at = timezone.now()
        order.save()
        return Response({"message": "Sample collected."})

class OrderStatusUpdateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        if request.user.role not in [User.Roles.ADMIN, User.Roles.PHLEBOTOMIST]:
            return Response({"message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        try:
            order = OrderTransaction.objects.get(pk=pk)
        except OrderTransaction.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        status_value = request.data.get('order_status')
        notes = request.data.get('notes')

        if status_value is None and notes is None:
            return Response({"message": "Nothing to update."}, status=status.HTTP_400_BAD_REQUEST)

        updated = False
        profile = getattr(request.user, 'user_master', None)

        if status_value is not None:
            try:
                status_value = int(status_value)
            except (TypeError, ValueError):
                return Response({"message": "Invalid status value."}, status=status.HTTP_400_BAD_REQUEST)

            if status_value == OrderTransaction.Status.COLLECTED:
                if order.order_status != OrderTransaction.Status.ORDERED:
                    return Response({"message": "Order must be Ordered before it can be marked Collected."}, status=status.HTTP_400_BAD_REQUEST)
                order.order_status = OrderTransaction.Status.COLLECTED
                order.collected_by = profile
                order.collected_at = timezone.now()
                updated = True
            elif status_value == order.order_status:
                updated = True
            else:
                return Response({"message": "Invalid status transition for phlebotomist."}, status=status.HTTP_400_BAD_REQUEST)

        if notes is not None:
            order.notes = notes
            updated = True

        if updated:
            order.save()
            return Response({"message": "Order updated successfully."})

        return Response({"message": "No changes applied."}, status=status.HTTP_400_BAD_REQUEST)

class OrderReceiveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        if request.user.role not in [User.Roles.ADMIN, User.Roles.LAB_TECHNICIAN]:
            return Response({"message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        try:
            order = OrderTransaction.objects.get(pk=pk)
        except OrderTransaction.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if order.order_status != OrderTransaction.Status.COLLECTED:
            return Response({"message": "Order must be Collected before receiving."}, status=status.HTTP_400_BAD_REQUEST)

        profile = getattr(request.user, 'user_master', None)
        order.order_status = OrderTransaction.Status.IN_LAB
        order.received_by = profile
        order.received_at = timezone.now()
        order.save()
        return Response({"message": "Sample received in lab."})

class OrderResultsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        if request.user.role not in [User.Roles.ADMIN, User.Roles.LAB_TECHNICIAN]:
            return Response({"message": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

        try:
            order = OrderTransaction.objects.get(pk=pk)
        except OrderTransaction.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if order.order_status not in [OrderTransaction.Status.IN_LAB, OrderTransaction.Status.COMPLETED]:
            return Response({"message": "Order must be In-Lab to enter results."}, status=status.HTTP_400_BAD_REQUEST)

        results_data = request.data.get('results', [])
        profile = getattr(request.user, 'user_master', None)

        with transaction.atomic():
            for rd in results_data:
                res = Results.objects.get(id=rd['result_id'], order=order)
                res.result_value = rd.get('value', res.result_value)
                res.flag = rd.get('flag', res.flag)
                res.remarks = rd.get('remarks', res.remarks)
                res.entered_by = profile
                res.entered_at = timezone.now()
                res.save()

            order.order_status = OrderTransaction.Status.COMPLETED
            order.save()

        return Response({"message": "Results saved and order completed."})

class OrderReportView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            order = OrderTransaction.objects.select_related('patient', 'ordered_by', 'collected_by').prefetch_related('results', 'results__assay').get(pk=pk)
        except OrderTransaction.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if order.order_status != OrderTransaction.Status.COMPLETED:
            return Response({"message": "Report is not available. Order must be Completed."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = OrderTransactionSerializer(order)
        return Response({"success": True, "report": serializer.data})
