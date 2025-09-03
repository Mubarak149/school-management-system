from django.urls import path
from .views import *

urlpatterns = [
    path("dashboard/", finance_dashboard, name="finance_dashboard"),

    # Category CRUD
    path("categories/create/", create_category, name="create_category"),
    path("categories/<int:pk>/edit/", edit_category, name="edit_category"),
    path("categories/<int:pk>/delete/", delete_category, name="delete_category"),
    path("categories/<int:pk>/row/", category_row, name="category_row"),
    path("fee_category_dropdown/", fee_category_dropdown ,name="fee_category_dropdown"),
    
    #Fee structure CRUD
    path("fee-structures/", fee_structures_view, name="fee_structures"),
    path("fee-structures/create/", create_fee_structure, name="create_fee_structure"),
    path("fee-structures/<int:pk>/edit/", edit_fee_structure, name="edit_fee_structure"),
    path("cancel_fee-structures/<int:pk>/", cancel_edit_fee_structure, name="cancel_edit_fee_structure"),
    path("fee-structures/page/<int:page>/", fee_structure_page, name="fee_structure_page"),
    path("fee-structures/<int:pk>/delete/", delete_fee_structure, name="delete_fee_structure"),
    path("fee-structure/<int:fs_id>/invoices/", fee_structure_invoices, name="fee_structure_invoices"),
    path("fee-structure/<int:fs_id>/invoices/pdf/", export_invoices_pdf, name="export_invoices_pdf"),
    path("fee-structure/<int:fs_id>/invoices/word/", export_invoices_word, name="export_invoices_word"),
    path("fee-structure/<int:fs_id>/invoices/excel/", export_invoices_excel, name="export_invoices_excel"),

    #Invoice
    path("send-invoice/<int:fs_id>/", send_invoice, name="send_invoice"),
    path("invoices/page/<int:page>/", invoice_page, name="invoice_page"),
    path("invoice/<int:pk>/", invoice_detail, name="invoice_detail"),
    path("invoice/<int:pk>/pdf/", invoice_detail_pdf, name="invoice_detail_pdf"),
    path("invoice/<int:pk>/word/", invoice_detail_word, name="invoice_detail_word"),
    #payment
    path("create/payment/", create_payment, name="create_payment"),
    path("invoice/<int:invoice_id>/pay/", invoice_payment, name="invoice_payment"),
    path("payments/page/<int:page>/", payment_page, name="payment_page"),
    path("receipt/<int:invoice_id>/", generate_receipt, name="generate_receipt"),

    
    
]
