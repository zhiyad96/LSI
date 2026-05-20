from functools import wraps

from django.conf import settings
from django.shortcuts import redirect
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken


class CookieJWTAuthentication(JWTAuthentication):
    """
    Reads the JWT access token from an HTTP-only cookie
    instead of the Authorization header.
    """
    def authenticate(self, request):
        jwt_settings = settings.SIMPLE_JWT
        cookie_name = jwt_settings.get("AUTH_COOKIE", "access_token")
        raw_token = request.COOKIES.get(cookie_name)

        if raw_token is None:
            return None
        validated_token = self.get_validated_token(raw_token)
        return self.get_user(validated_token), validated_token

    # ======================   for reffresh token =================

def _get_refresh_cookie_name():
    return settings.SIMPLE_JWT.get("AUTH_COOKIE_REFRESH", "refresh_token")

            # ====================== tokens store in cookies =====================

def _set_access_cookie(response, access_token):
    jwt_settings = settings.SIMPLE_JWT
    response.set_cookie(
        key=jwt_settings.get("AUTH_COOKIE", "access_token"),
        value=access_token,
        httponly=jwt_settings.get("AUTH_COOKIE_HTTP_ONLY", True),
        secure=jwt_settings.get("AUTH_COOKIE_SECURE", False),
        samesite=jwt_settings.get("AUTH_COOKIE_SAMESITE", "Lax"),
        max_age=int(jwt_settings["ACCESS_TOKEN_LIFETIME"].total_seconds()),
    )

        # ======================is token checking==============

def _authenticate_request_from_cookie(request):
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

        # ============================= for login ==========================

def jwt_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        user, access_token = _authenticate_request_from_cookie(request)
        if user is None:
            return redirect('accounts:login')
        request.user = user
        response = view_func(request, *args, **kwargs)
        if access_token is not None:
            _set_access_cookie(response, access_token)
        return response
    return wrapper

        # ==================== if user  checking =================

def jwt_user_passes_test(test_func, login_url='accounts:login'):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            user, access_token = _authenticate_request_from_cookie(request)
            if user is None or not test_func(user):
                return redirect(login_url)
            request.user = user
            response = view_func(request, *args, **kwargs)
            if access_token is not None:
                _set_access_cookie(response, access_token)
            return response
        return wrapper
    return decorator
