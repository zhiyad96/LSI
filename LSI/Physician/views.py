from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from .models import PatientMaster
from .serializers import PatientSerializer
from accounts.models import User

class IsAdminPhysicianOrNurse(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in [User.Roles.ADMIN, User.Roles.PHYSICIAN, User.Roles.NURSE]

class PatientListCreateView(APIView):
    permission_classes = [IsAdminPhysicianOrNurse]

    def get_queryset(self):
        qs = PatientMaster.objects.all().order_by('-created_at')
        search = self.request.query_params.get('search', None)
        if search:
            qs = qs.filter(Q(mrn__icontains=search) | Q(patient_name__icontains=search))
        return qs

    def get(self, request):
        patients = self.get_queryset()
        serializer = PatientSerializer(patients, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatientDetailView(APIView):
    permission_classes = [IsAdminPhysicianOrNurse]

    def get_object(self, pk):
        try:
            return PatientMaster.objects.get(pk=pk)
        except PatientMaster.DoesNotExist:
            return None

    def get(self, request, pk):
        patient = self.get_object(pk)
        if not patient:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PatientSerializer(patient)
        return Response(serializer.data)

    def put(self, request, pk):
        patient = self.get_object(pk)
        if not patient:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PatientSerializer(patient, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        patient = self.get_object(pk)
        if not patient:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PatientSerializer(patient, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        patient = self.get_object(pk)
        if not patient:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)
        patient.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
