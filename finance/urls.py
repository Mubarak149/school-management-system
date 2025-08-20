from django.urls import path
from .views import *

urlpatterns = [
    path("dashboard/", finance_dashboard, name="finance_dashboard"),

    # Category CRUD
    path("create-category/", create_category, name="create_category"),
    path("categories/<int:pk>/edit/", edit_category, name="edit_category"),
    path("categories/<int:pk>/delete/", delete_category, name="delete_category"),

    # ✅ Add this
    path("categories/<int:pk>/row/", category_row, name="category_row"),
]
