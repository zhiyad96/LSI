from django.shortcuts import render, redirect
from django.conf import settings
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.authentication import CookieJWTAuthentication
from accounts.models import User


def _get_refresh_cookie_name():
    return settings.SIMPLE_JWT.get('AUTH_COOKIE_REFRESH', 'refresh_token')


def _set_access_cookie(response, access_token):
    jwt_settings = settings.SIMPLE_JWT
    response.set_cookie(
        key=jwt_settings.get('AUTH_COOKIE', 'access_token'),
        value=access_token,
        httponly=jwt_settings.get('AUTH_COOKIE_HTTP_ONLY', True),
        secure=jwt_settings.get('AUTH_COOKIE_SECURE', False),
        samesite=jwt_settings.get('AUTH_COOKIE_SAMESITE', 'Lax'),
        max_age=int(jwt_settings['ACCESS_TOKEN_LIFETIME'].total_seconds()),
    )


def _get_default_redirect_name(user):
    role = getattr(user, 'role', None)
    if role == User.Roles.ADMIN:
        return 'custom_admin:dashboard'
    if role in [User.Roles.PHYSICIAN, User.Roles.NURSE]:
        return 'patient_list'
    if role == User.Roles.PHLEBOTOMIST:
        return 'phlebotomist_worklist'
    if role == User.Roles.LAB_TECHNICIAN:
        return 'technician_dashboard'
    return 'accounts:login'


def _authenticate_from_cookie(request):
    auth = CookieJWTAuthentication()

    if request.user.is_authenticated:
        return request.user, None

    try:
        auth_result = auth.authenticate(request)
    except TokenError:
        auth_result = None

    if auth_result:
        user, _ = auth_result
        return user, None

    refresh_token = request.COOKIES.get(_get_refresh_cookie_name())
    if not refresh_token:
        return None, None

    try:
        refresh = RefreshToken(refresh_token)
    except TokenError:
        return None, None

    access_token = str(refresh.access_token)
    user = auth.get_user(refresh.access_token)
    return user, access_token


def _redirect_authenticated(request):
    user, access_token = _authenticate_from_cookie(request)
    if user is None:
        return None

    redirect_name = _get_default_redirect_name(user)
    response = redirect(redirect_name)
    if access_token is not None:
        _set_access_cookie(response, access_token)
    return response


def home_redirect(request):
    redirect_response = _redirect_authenticated(request)
    if redirect_response:
        return redirect_response
    return redirect('accounts:login')


def login_page(request):
    """Just render the login page. API handles the actual login."""
    redirect_response = _redirect_authenticated(request)
    if redirect_response:
        return redirect_response
    return render(request, 'login.html')


def register_page(request):
    """Render the register page only for admin users."""
    user, access_token = _authenticate_from_cookie(request)
    if user is None:
        return redirect('accounts:login')

    if user.role != User.Roles.ADMIN:
        return redirect(_get_default_redirect_name(user))

    response = render(request, 'register.html', {
        'roles': User.Roles.choices,
    })
    if access_token is not None:
        _set_access_cookie(response, access_token)
    return response


def logout_page(request):
    """Clear cookies and redirect."""
    jwt = settings.SIMPLE_JWT
    response = redirect('accounts:login')
    response.delete_cookie(jwt.get('AUTH_COOKIE', 'access_token'))
    response.delete_cookie(jwt.get('AUTH_COOKIE_REFRESH', 'refresh_token'))
    return response


def change_password_page(request):
    user, access_token = _authenticate_from_cookie(request)
    if user is None:
        return redirect('accounts:login')

    if user.role != User.Roles.ADMIN:
        return redirect(_get_default_redirect_name(user))

    response = render(request, 'accounts/change_password.html')
    if access_token is not None:
        _set_access_cookie(response, access_token)
    return response