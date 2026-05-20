from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

# pyrefly: ignore [missing-import]
from .models import User, UserMaster, UserAccessMaster


# ──===================== Register Serializer ────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    password         = serializers.CharField(write_only=True,min_length=8,validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, min_length=8)
    employee_id  = serializers.CharField(max_length=20)
    full_name    = serializers.CharField(max_length=150)
    designation  = serializers.CharField(max_length=80)
    department   = serializers.CharField(max_length=80, required=False, allow_blank=True)
    phone        = serializers.CharField(max_length=20,  required=False, allow_blank=True)

    class Meta:
        model  = User
        fields = [
            "username",
            "password",
            "confirm_password",
            "role",
            "employee_id",
            "full_name",
            "designation",
            "department",
            "phone",
        ]

    # ──============== Field-level validations ───────────────────────────────

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value.lower()  

    def validate_employee_id(self, value):
        if UserMaster.objects.filter(employee_id=value).exists():
            raise serializers.ValidationError("Employee ID already exists.")
        return value

    # ──=================== Object-level validation ────────────────────────────────

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs

    # ──====================== Create ────────────────────────────────────────────────

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop("confirm_password")
        employee_id = validated_data.pop("employee_id")
        full_name   = validated_data.pop("full_name")
        designation = validated_data.pop("designation")
        department  = validated_data.pop("department", None) or None
        phone       = validated_data.pop("phone",       None) or None
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            role=validated_data["role"],
        )

        # Create linked profile
        UserMaster.objects.create(
            auth_user   = user,
            employee_id = employee_id,
            full_name   = full_name,
            designation = designation,
            department  = department,
            phone       = phone,
        )

        return user


# ── Login Serializer ───────────────────────────────────────────────────────────

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username", "").lower()   # match lowercase storage
        password = attrs.get("password")

        # authenticate() internally calls check_password() — verifies the hash
        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError(
                {"non_field_errors": "Invalid username or password."}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"non_field_errors": "Your account has been deactivated."}
            )

        attrs["user"] = user
        return attrs


# ── Change Password Serializer ─────────────────────────────────────────────────

class ChangePasswordSerializer(serializers.Serializer):
    old_password     = serializers.CharField(write_only=True)
    new_password     = serializers.CharField(write_only=True, min_length=8, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):           # check_password() verifies the hash
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        if attrs["old_password"] == attrs["new_password"]:
            raise serializers.ValidationError({"new_password": "New password must differ from the current one."})
        return attrs

    def save(self, **kwargs):
        user = self.context["request"].user
        user.set_password(self.validated_data["new_password"])   # hashes the new password
        user.save()
        return user


class UserMasterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='auth_user.username', read_only=True)
    role = serializers.CharField(source='auth_user.role', read_only=True)
    auth_user_id = serializers.IntegerField(write_only=True, required=True)

    class Meta:
        model = UserMaster
        fields = [
            'id',
            'auth_user_id',
            'username',
            'role',
            'employee_id',
            'full_name',
            'designation',
            'department',
            'phone',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'username', 'role', 'created_at', 'updated_at']

    def validate_auth_user_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError('User does not exist.')
        if UserMaster.objects.filter(auth_user_id=value).exists():
            raise serializers.ValidationError('Profile for this user already exists.')
        return value

    def create(self, validated_data):
        auth_user_id = validated_data.pop('auth_user_id')
        auth_user = User.objects.get(id=auth_user_id)
        return UserMaster.objects.create(auth_user=auth_user, **validated_data)

    def update(self, instance, validated_data):
        validated_data.pop('auth_user_id', None)
        return super().update(instance, validated_data)


class UserAccessMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccessMaster
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
