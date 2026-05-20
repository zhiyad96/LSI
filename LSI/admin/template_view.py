from django.shortcuts import render
from accounts.authentication import jwt_user_passes_test
from accounts.models import User


def admin_user_check(user):
    return user.is_authenticated and user.role == User.Roles.ADMIN

@jwt_user_passes_test(admin_user_check, login_url='/login/')
def dashboard_page(request):
    """Render the Admin Dashboard."""
    return render(request, 'admin_dashboard.html')
