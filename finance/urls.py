from django.urls import path
from .views import finance_dashboard

urlpatterns = [
    path("dashboard/", finance_dashboard, name="finance_dashboard"),
]
