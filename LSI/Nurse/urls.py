from django.urls import path

from . import template_view, views

urlpatterns = [
    #   ===== template =======
    path("nurse/", template_view.nurse_lab_page, name="nurse_lab_page"),
    path("orders/new/", template_view.nurse_lab_page, name="nurse_order_entry"),
    
    # ======= re st api view ========
    
    path("api/v1/nurse/patients/", views.NursePatientLookupAPIView.as_view(), name="nurse_patients_api"),
    path("api/v1/nurse/assays/", views.NurseAssayLookupAPIView.as_view(), name="nurse_assays_api"),
    path("api/v1/nurse/orders/", views.NurseOrderCreateAPIView.as_view(), name="nurse_orders_api"),
    path("api/v1/nurse/reports/", views.NurseCompletedReportsAPIView.as_view(), name="nurse_reports_api"),
    path("api/v1/nurse/reports/<int:order_id>/", views.NurseReportDetailAPIView.as_view(), name="nurse_report_detail_api"),
]
