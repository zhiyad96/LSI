from django.db import transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User, UserMaster, UserAccessMaster
from accounts.serializers import RegisterSerializer, UserMasterSerializer, UserAccessMasterSerializer

class UserListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != User.Roles.ADMIN:
            return Response({"success": False, "message": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
            
        users = User.objects.select_related('user_master').all()
        data = []
        for u in users:
            profile = getattr(u, "user_master", None)
            data.append({
                "id": u.id,
                "username": u.username,
                "role": u.role,
                "role_display": u.get_role_display(),
                "is_active": u.is_active,
                "employee_id": profile.employee_id if profile else None,
                "full_name": profile.full_name if profile else None,
                "designation": profile.designation if profile else None,
                "department": profile.department if profile else None,
                "phone": profile.phone if profile else None,
            })
        return Response({"success": True, "users": data}, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.role != User.Roles.ADMIN:
            return Response({"success": False, "message": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        profile = getattr(user, "user_master", None)
        return Response({
            "success": True, 
            "message": "User created successfully.",
            "user": {
                "id": user.id,
                "username": user.username,
                "role": user.role,
                "role_display": user.get_role_display(),
                "is_active": user.is_active,
                "employee_id": profile.employee_id if profile else None,
                "full_name": profile.full_name if profile else None,
                "designation": profile.designation if profile else None,
                "department": profile.department if profile else None,
                "phone": profile.phone if profile else None,
            }
        }, status=status.HTTP_201_CREATED)

class UserDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        if request.user.role != User.Roles.ADMIN:
            return Response({"success": False, "message": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"success": False, "message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            
        data = request.data
        profile = getattr(user, "user_master", None)
        
        with transaction.atomic():
            # Update user fields
            if 'role' in data:
                user.role = data['role']
            if 'is_active' in data:
                is_active = data['is_active']
                if isinstance(is_active, str):
                    is_active = is_active.lower() == 'true'
                user.is_active = is_active
                
            if 'password' in data and data['password']:
                user.set_password(data['password'])
                
            user.save()
            
            # Update profile fields
            if profile:
                if 'full_name' in data: profile.full_name = data['full_name']
                if 'designation' in data: profile.designation = data['designation']
                if 'department' in data: profile.department = data['department']
                if 'phone' in data: profile.phone = data['phone']
                profile.save()
                
        return Response({"success": True, "message": "User updated successfully."}, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        if request.user.role != User.Roles.ADMIN:
            return Response({"success": False, "message": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
            
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"success": False, "message": "User not found."}, status=status.HTTP_404_NOT_FOUND)
            
        if user == request.user:
            return Response({"success": False, "message": "You cannot delete yourself."}, status=status.HTTP_400_BAD_REQUEST)
            
        user.delete()
        return Response({"success": True, "message": "User deleted successfully."}, status=status.HTTP_200_OK)


class AdminProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != User.Roles.ADMIN:
            return Response({"success": False, "message": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)

        profile = getattr(request.user, "user_master", None)
        return Response({
            "success": True,
            "user": {
                "id": request.user.id,
                "username": request.user.username,
                "role": request.user.role,
                "role_display": request.user.get_role_display(),
                "is_active": request.user.is_active,
                "employee_id": profile.employee_id if profile else None,
                "full_name": profile.full_name if profile else None,
                "designation": profile.designation if profile else None,
                "department": profile.department if profile else None,
                "phone": profile.phone if profile else None,
            }
        }, status=status.HTTP_200_OK)

    def put(self, request):
        if request.user.role != User.Roles.ADMIN:
            return Response({"success": False, "message": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)

        user = request.user
        data = request.data
        profile = getattr(user, "user_master", None)

        if "username" in data:
            username = data["username"].strip().lower()
            if username and User.objects.filter(username__iexact=username).exclude(pk=user.pk).exists():
                return Response({"success": False, "message": "Username already exists."}, status=status.HTTP_400_BAD_REQUEST)
            user.username = username

        if "password" in data and data["password"]:
            user.set_password(data["password"])

        if "is_active" in data:
            is_active = data["is_active"]
            if isinstance(is_active, str):
                is_active = is_active.lower() == "true"
            user.is_active = is_active

        user.save()

        if profile:
            if "full_name" in data:
                profile.full_name = data["full_name"]
            if "designation" in data:
                profile.designation = data["designation"]
            if "department" in data:
                profile.department = data["department"]
            if "phone" in data:
                profile.phone = data["phone"]
            profile.save()

        return Response({"success": True, "message": "Profile updated successfully."}, status=status.HTTP_200_OK)


class UserMasterListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != User.Roles.ADMIN:
            return Response({"success": False, "message": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
        profiles = UserMaster.objects.select_related('auth_user').all().order_by('-created_at')
        serializer = UserMasterSerializer(profiles, many=True)
        return Response({"success": True, "profiles": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.role != User.Roles.ADMIN:
            return Response({"success": False, "message": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserMasterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "profile": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserMasterDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return UserMaster.objects.select_related('auth_user').get(pk=pk)
        except UserMaster.DoesNotExist:
            return None

    def get(self, request, pk):
        if request.user.role != User.Roles.ADMIN:
            return Response({"success": False, "message": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
        profile = self.get_object(pk)
        if not profile:
            return Response({"success": False, "message": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserMasterSerializer(profile)
        return Response({"success": True, "profile": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        if request.user.role != User.Roles.ADMIN:
            return Response({"success": False, "message": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
        profile = self.get_object(pk)
        if not profile:
            return Response({"success": False, "message": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserMasterSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "profile": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user.role != User.Roles.ADMIN:
            return Response({"success": False, "message": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
        profile = self.get_object(pk)
        if not profile:
            return Response({"success": False, "message": "Profile not found."}, status=status.HTTP_404_NOT_FOUND)
        profile.delete()
        return Response({"success": True, "message": "Profile deleted."}, status=status.HTTP_200_OK)


class UserAccessMasterListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != User.Roles.ADMIN:
            return Response({"success": False, "message": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
        access_entries = UserAccessMaster.objects.all().order_by('-created_at')
        serializer = UserAccessMasterSerializer(access_entries, many=True)
        return Response({"success": True, "access_entries": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        if request.user.role != User.Roles.ADMIN:
            return Response({"success": False, "message": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
        serializer = UserAccessMasterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "access_entry": serializer.data}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class UserAccessMasterDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return UserAccessMaster.objects.get(pk=pk)
        except UserAccessMaster.DoesNotExist:
            return None

    def get(self, request, pk):
        if request.user.role != User.Roles.ADMIN:
            return Response({"success": False, "message": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
        entry = self.get_object(pk)
        if not entry:
            return Response({"success": False, "message": "Entry not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserAccessMasterSerializer(entry)
        return Response({"success": True, "access_entry": serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        if request.user.role != User.Roles.ADMIN:
            return Response({"success": False, "message": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
        entry = self.get_object(pk)
        if not entry:
            return Response({"success": False, "message": "Entry not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = UserAccessMasterSerializer(entry, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success": True, "access_entry": serializer.data}, status=status.HTTP_200_OK)
        return Response({"success": False, "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user.role != User.Roles.ADMIN:
            return Response({"success": False, "message": "Unauthorized."}, status=status.HTTP_403_FORBIDDEN)
        entry = self.get_object(pk)
        if not entry:
            return Response({"success": False, "message": "Entry not found."}, status=status.HTTP_404_NOT_FOUND)
        entry.delete()
        return Response({"success": True, "message": "Entry deleted."}, status=status.HTTP_200_OK)
