from django.urls import path
from .views import PatientListCreateView, PatientDetailView

from . import template_view

urlpatterns = [
    path('api/v1/patients/', PatientListCreateView.as_view(), name='patient-list'),
    path('api/v1/patients/<int:pk>/', PatientDetailView.as_view(), name='patient-detail'),

    path('patients/', template_view.patient_list, name='patient_list'),
    path('patients/new/', template_view.patient_register, name='patient_register'),
    path('physician/', template_view.physician_lab_page, name='physician_lab_page'),
    path('physician/orders/', template_view.physician_lab_page, name='physician_lab_orders'),
]
