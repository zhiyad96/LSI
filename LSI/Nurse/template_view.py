from django.shortcuts import render
from accounts.authentication import jwt_user_passes_test
from accounts.models import User


def nurse_user_check(user):
    return user.is_authenticated and user.role in [User.Roles.NURSE, User.Roles.ADMIN]

@jwt_user_passes_test(nurse_user_check, login_url='/login/')
def nurse_lab_page(request):
    return render(request, "nurse_lab_orders.html")
