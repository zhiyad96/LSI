from django.urls import path
from .views import (
    TestMenuListCreateView, TestMenuDetailView,
    AssayListCreateView, AssayDetailView,
    OrderListCreateView, OrderDetailView,
    OrderCollectView, OrderStatusUpdateView, OrderReceiveView, OrderResultsView, OrderReportView
)
from . import template_view

urlpatterns = [
    path('technician/', template_view.technician_dashboard, name='technician_dashboard'),

    # Test Menu endpoints
    path('api/v1/tests/menus/', TestMenuListCreateView.as_view(), name='testmenu-list'),
    path('api/v1/tests/menus/<int:pk>/', TestMenuDetailView.as_view(), name='testmenu-detail'),
    
    # Assay endpoints
    path('api/v1/tests/assays/', AssayListCreateView.as_view(), name='assay-list'),
    path('api/v1/tests/assays/<int:pk>/', AssayDetailView.as_view(), name='assay-detail'),
    
    # Order endpoints
    path('api/v1/orders/', OrderListCreateView.as_view(), name='order-list'),
    path('api/v1/orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('api/v1/orders/<int:pk>/collect/', OrderCollectView.as_view(), name='order-collect'),
    path('api/v1/orders/<int:pk>/status/', OrderStatusUpdateView.as_view(), name='order-status-update'),
    path('api/v1/orders/<int:pk>/receive/', OrderReceiveView.as_view(), name='order-receive'),
    path('api/v1/orders/<int:pk>/results/', OrderResultsView.as_view(), name='order-results'),
    path('api/v1/orders/<int:pk>/report/', OrderReportView.as_view(), name='order-report'),
]
