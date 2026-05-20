from django.urls import path
from admin import views
from admin import template_view

app_name = 'custom_admin'

urlpatterns = [
    # Template View
    path('dashboard/', template_view.dashboard_page, name='dashboard'),

    # REST API for users
    path('api/users/', views.UserListCreateAPIView.as_view(), name='api_users'),
    path('api/users/<int:pk>/', views.UserDetailAPIView.as_view(), name='api_user_detail'),
    path('api/profile/', views.AdminProfileAPIView.as_view(), name='api_profile'),
    path('api/user-masters/', views.UserMasterListCreateAPIView.as_view(), name='api_user_master_list'),
    path('api/user-masters/<int:pk>/', views.UserMasterDetailAPIView.as_view(), name='api_user_master_detail'),
    path('api/user-access/', views.UserAccessMasterListCreateAPIView.as_view(), name='api_user_access_list'),
    path('api/user-access/<int:pk>/', views.UserAccessMasterDetailAPIView.as_view(), name='api_user_access_detail'),
]
