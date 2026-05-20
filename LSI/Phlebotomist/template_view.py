from django.shortcuts import render
from accounts.authentication import jwt_user_passes_test
from accounts.models import User


def phlebotomist_user_check(user):
    return user.is_authenticated and user.role in [User.Roles.PHLEBOTOMIST, User.Roles.ADMIN]

@jwt_user_passes_test(phlebotomist_user_check, login_url='/login/')
def phlebotomist_worklist(request):
    return render(request, 'phlebotomist_worklist.html')
