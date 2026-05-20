from django.shortcuts import render
from accounts.authentication import jwt_user_passes_test
from accounts.models import User

def physician_staff_check(user):
    return user.is_authenticated and user.role in [
        User.Roles.ADMIN,
        User.Roles.PHYSICIAN,
        User.Roles.NURSE,
    ]

@jwt_user_passes_test(physician_staff_check, login_url='/login/')
def patient_list(request):
    return render(request, 'patient_list.html')

@jwt_user_passes_test(physician_staff_check, login_url='/login/')
def patient_register(request):
    return render(request, 'patient_register.html')

@jwt_user_passes_test(physician_staff_check, login_url='/login/')
def physician_lab_page(request):
    return render(request, 'physician_lab_orders.html')
