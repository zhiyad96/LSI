from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from .serializers import ChangePasswordSerializer, LoginSerializer, RegisterSerializer


# ── Helpers ────────────────────────────────────────────────────────────────────

def _set_auth_cookies(response, access_token, refresh_token):
    """Set JWT tokens as HTTP-only cookies."""
    jwt_settings = settings.SIMPLE_JWT

    response.set_cookie(
        key      = jwt_settings.get("AUTH_COOKIE", "access_token"),
        value    = access_token,
        httponly = jwt_settings.get("AUTH_COOKIE_HTTP_ONLY", True),
        secure   = jwt_settings.get("AUTH_COOKIE_SECURE",    False),
        samesite = jwt_settings.get("AUTH_COOKIE_SAMESITE",  "Lax"),
        max_age  = int(jwt_settings["ACCESS_TOKEN_LIFETIME"].total_seconds()),
    )
    response.set_cookie(
        key      = jwt_settings.get("AUTH_COOKIE_REFRESH", "refresh_token"),
        value    = refresh_token,
        httponly = True,
        secure   = jwt_settings.get("AUTH_COOKIE_SECURE",   False),
        samesite = jwt_settings.get("AUTH_COOKIE_SAMESITE", "Lax"),
        max_age  = int(jwt_settings["REFRESH_TOKEN_LIFETIME"].total_seconds()),
    )


def _clear_auth_cookies(response):
    """Delete JWT cookies on logout."""
    jwt_settings = settings.SIMPLE_JWT
    response.delete_cookie(jwt_settings.get("AUTH_COOKIE",         "access_token"))
    response.delete_cookie(jwt_settings.get("AUTH_COOKIE_REFRESH", "refresh_token"))


def _build_user_payload(user):
    """Return a safe dict of user info to send in the response body."""
    profile = getattr(user, "user_master", None)
    return {
        "id":          user.id,
        "username":    user.username,
        "role":        user.role,
        "role_display": user.get_role_display(),
        "employee_id": profile.employee_id if profile else None,
        "full_name":   profile.full_name   if profile else None,
        "designation": profile.designation if profile else None,
        "department":  profile.department  if profile else None,
    }


# ── Register ───────────────────────────────────────────────────────────────────

class RegisterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != User.Roles.ADMIN:
            return Response(
                {"success": False, "message": "Only admin users may register new accounts."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = serializer.save()

        response = Response(
            {
                "success": True,
                "message": "Account created successfully.",
                "user":    _build_user_payload(user),
            },
            status=status.HTTP_201_CREATED,
        )
        return response


# ── Login ──────────────────────────────────────────────────────────────────────

class LoginView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """Return login page (template rendering handled by Django template view)."""
        if request.user.is_authenticated:
            return Response(
                {"message": "Already logged in.", "user": _build_user_payload(request.user)},
                status=status.HTTP_200_OK,
            )
        return Response(
            {"message": "Please log in."},
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user          = serializer.validated_data["user"]
        refresh       = RefreshToken.for_user(user)
        access_token  = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response(
            {
                "success": True,
                "message": "Login successful.",
                "user":    _build_user_payload(user),
            },
            status=status.HTTP_200_OK,
        )
        _set_auth_cookies(response, access_token, refresh_token)
        return response


# ── Logout ─────────────────────────────────────────────────────────────────────

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.COOKIES.get(
            settings.SIMPLE_JWT.get("AUTH_COOKIE_REFRESH", "refresh_token")
        )

        response = Response(
            {"success": True, "message": "Logged out successfully."},
            status=status.HTTP_200_OK,
        )

        # Blacklist the refresh token so it cannot be reused
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError:
                # Already expired or invalid — still clear cookies
                pass

        _clear_auth_cookies(response)
        return response


# ── Refresh Token ──────────────────────────────────────────────────────────────

class TokenRefreshView(APIView):
    """
    Silent token refresh — called automatically by the frontend
    before the access token expires.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get(
            settings.SIMPLE_JWT.get("AUTH_COOKIE_REFRESH", "refresh_token")
        )

        if not refresh_token:
            return Response(
                {"success": False, "message": "No refresh token found."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh      = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
        except TokenError as e:
            return Response(
                {"success": False, "message": "Session expired. Please log in again."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = Response(
            {"success": True, "message": "Token refreshed."},
            status=status.HTTP_200_OK,
        )
        jwt_settings = settings.SIMPLE_JWT
        response.set_cookie(
            key      = jwt_settings.get("AUTH_COOKIE", "access_token"),
            value    = access_token,
            httponly = jwt_settings.get("AUTH_COOKIE_HTTP_ONLY", True),
            secure   = jwt_settings.get("AUTH_COOKIE_SECURE",    False),
            samesite = jwt_settings.get("AUTH_COOKIE_SAMESITE",  "Lax"),
            max_age  = int(jwt_settings["ACCESS_TOKEN_LIFETIME"].total_seconds()),
        )
        return response


# ── Change Password ────────────────────────────────────────────────────────────

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.role != User.Roles.ADMIN:
            return Response(
                {"success": False, "message": "Only admin users may change password."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ChangePasswordSerializer(
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(
                {"success": False, "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer.save()

        # Invalidate existing tokens — force re-login after password change
        response = Response(
            {"success": True, "message": "Password changed. Please log in again."},
            status=status.HTTP_200_OK,
        )
        _clear_auth_cookies(response)
        return response


# ── Me (current user info) ─────────────────────────────────────────────────────

class MeView(APIView):
    """Returns the currently authenticated user's profile."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {"success": True, "user": _build_user_payload(request.user)},
            status=status.HTTP_200_OK,
        )