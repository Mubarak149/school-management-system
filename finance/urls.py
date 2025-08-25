from django.urls import path
from .views import *

urlpatterns = [
    path("dashboard/", finance_dashboard, name="finance_dashboard"),

    # Category CRUD
    path("categories/create/", create_category, name="create_category"),
    path("categories/<int:pk>/edit/", edit_category, name="edit_category"),
    path("categories/<int:pk>/delete/", delete_category, name="delete_category"),
    path("categories/<int:pk>/row/", category_row, name="category_row"),
    
    #Fee structure CRUD
    path("fee-structures/", fee_structures_view, name="fee_structures"),
    path("fee-structures/create/", create_fee_structure, name="create_fee_structure"),
    path("fee-structures/<int:pk>/edit/", edit_fee_structure, name="edit_fee_structure"),
    path("fee-structures/<int:pk>/delete/", delete_fee_structure, name="delete_fee_structure"),
    #Invoice
    path("send-invoice/<int:fs_id>/", send_invoice, name="send_invoice"),
    
    #payment
    path("create/payment/", create_payment, name="create_payment"),
]
