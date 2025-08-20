from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from .forms import InvoiceForm, PaymentForm, InvoiceItemForm, FeeCategoryForm
from .models import SchoolInvoice, InvoiceItem, Payment, FeeStructure, FeeCategory
from student.models import Student
from main.models import AcademicSession


def finance_dashboard(request):
    # 1. Get all students and invoices to display in dashboard
    students = Student.objects.all() 
    invoices = SchoolInvoice.objects.all()
    payments = Payment.objects.all()
    category_form = FeeCategoryForm()
    category = FeeCategory.objects.all()
    payment_form = PaymentForm()
    invoice_form = InvoiceForm(request.POST)
   
    context = {
        "students": students,
        "invoices": invoices,
        "payments": payments,
        "invoice_form": invoice_form,
        "payment_form": payment_form,
        "categories":category,
        "category_form": category_form,
    }
    return render(request, "finance/finance_dashboard.html", context)

def category_row(request, pk):
    category = get_object_or_404(FeeCategory, pk=pk)
    html = render_to_string("finance/partials/category_row.html", {"cat": category})
    return HttpResponse(html)

def create_category(request):
    if request.method == "POST":
        form = FeeCategoryForm(request.POST)
        if form.is_valid():
            category = form.save()
            html = render_to_string("finance/partials/category_row.html", {"cat": category})
            return HttpResponse(html)  # HTMX swaps this into table
        return JsonResponse({"error": "Invalid data"}, status=400)

def edit_category(request, pk):
    category = get_object_or_404(FeeCategory, pk=pk)
    if request.method == "GET":
        form = FeeCategoryForm(instance=category)
        return render(request, "finance/partials/category_edit_form.html", {"form": form, "cat": category})

    elif request.method == "POST":
        form = FeeCategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save()
            html = render_to_string("finance/partials/category_row.html", {"cat": category})
            return HttpResponse(html)
        return JsonResponse({"error": "Invalid data"}, status=400)

def delete_category(request, pk):
    category = get_object_or_404(FeeCategory, pk=pk)
    category.delete()
    return HttpResponse("")  # removes row
