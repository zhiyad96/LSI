from django.urls import path
from accounts import views
from accounts import templates_view

app_name = 'accounts'

urlpatterns = [
    path('',                 templates_view.home_redirect,       name='home'),
    # ── ===============Template Pages ────────────────────────────────────────────
    path('login/',           templates_view.login_page,         name='login'),
    path('logout/',          templates_view.logout_page,        name='logout'),
    path('register/',        templates_view.register_page,      name='register'),
    path('change-password/', templates_view.change_password_page, name='change_password'),

    # ── ============REST API ───────────────────────────────────────────────────────
    path('api/login/',           views.LoginView.as_view(),          name='api_login'),
    path('api/register/',        views.RegisterView.as_view(),       name='api_register'),
    path('api/logout/',          views.LogoutView.as_view(),         name='api_logout'),
    path('api/token/refresh/',   views.TokenRefreshView.as_view(),   name='api_token_refresh'),
    path('api/change-password/', views.ChangePasswordView.as_view(), name='api_change_password'),
    path('api/me/',              views.MeView.as_view(),             name='api_me'),
]