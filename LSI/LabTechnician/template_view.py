from django.shortcuts import render
from accounts.authentication import jwt_user_passes_test
from accounts.models import User


def labtechnician_user_check(user):
    return user.is_authenticated and user.role in [User.Roles.LAB_TECHNICIAN, User.Roles.ADMIN]


@jwt_user_passes_test(labtechnician_user_check, login_url='/login/')
def technician_dashboard(request):
    return render(request, 'labtechnician_dashboard.html')
