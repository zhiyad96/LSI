from django.urls import path
from . import template_view

urlpatterns = [
    path('phlebotomist/', template_view.phlebotomist_worklist, name='phlebotomist_worklist'),
]
