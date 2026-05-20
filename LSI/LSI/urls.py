from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("admin.urls", namespace="custom_admin")),
    path("", include("Physician.urls")),
    path("", include("LabTechnician.urls")),
    path("", include("Phlebotomist.urls")),
    path("", include("Nurse.urls")),
    path("", include("accounts.urls")), 
]
