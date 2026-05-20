from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("The given username must be set")
        username = self.model.normalize_username(username)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractUser):
    objects = CustomUserManager()
    class Roles(models.TextChoices):
        ADMIN          = "ADMIN",          "Admin"
        PHYSICIAN      = "PHYSICIAN",      "Physician"
        NURSE          = "NURSE",          "Nurse"
        PHLEBOTOMIST   = "PHLEBOTOMIST",   "Phlebotomist"
        LAB_TECHNICIAN = "LAB_TECHNICIAN", "Lab Technician"
    email =models.EmailField(unique=True,null=True,blank=True) 
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.NURSE,)
    USERNAME_FIELD  = "username"
    REQUIRED_FIELDS = []    

    class Meta:
        db_table = "auth_user"
        
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class UserMaster(models.Model):
    auth_user   = models.OneToOneField(User, on_delete=models.CASCADE, related_name="user_master")
    employee_id = models.CharField(max_length=20, unique=True)
    full_name   = models.CharField(max_length=150)
    designation = models.CharField(max_length=80)
    department  = models.CharField(max_length=80, null=True, blank=True)
    phone       = models.CharField(max_length=20, null=True, blank=True)
    status      = models.CharField(max_length=10, default="Active")
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_master"

    def __str__(self):
        return f"{self.full_name} ({self.employee_id})"


class UserAccessMaster(models.Model):
    role_name = models.CharField(max_length=50)
    module_name = models.CharField(max_length=80)
    can_view = models.BooleanField(default=False)
    can_create = models.BooleanField(default=False)
    can_edit = models.BooleanField(default=False)
    can_delete = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_access_master"

    def __str__(self):
        return f"{self.role_name} - {self.module_name}"
