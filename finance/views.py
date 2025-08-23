from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.db import transaction, DatabaseError
from .forms import (InvoiceForm, PaymentForm, InvoiceItemForm,
                    FeeCategoryForm, FeeStructureForm)
from .models import (SchoolInvoice, InvoiceItem, 
                     Payment, FeeStructure, FeeCategory)
from student.models import Student
from main.models import AcademicSession


def finance_dashboard(request):
    # 1. Get all students and invoices to display in dashboard
    students = Student.objects.all() 
    invoices = SchoolInvoice.objects.all()
    payments = Payment.objects.all() 
    category = FeeCategory.objects.all()
    category_form = FeeCategoryForm()
    fee_structure_form = FeeStructureForm()
    fee_structure = FeeStructure.objects.all()
   
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
        'fee_structure_form':fee_structure_form,
        "structures":fee_structure,
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



def fee_structures_view(request):
    structures = FeeStructure.objects.select_related("school_class", "session", "category").all()
    form = FeeStructureForm()
    return render(request, "finance/fee_structures.html", {
        "structures": structures,
        "form": form,
    })

def create_fee_structure(request):
    if request.method == "POST":
        form = FeeStructureForm(request.POST)
        if form.is_valid():
            structure = form.save()
            html = render_to_string("finance/partials/fee_structure_row.html", {"fs": structure})
            return HttpResponse(html)
        return HttpResponse("Invalid data", status=400)

def edit_fee_structure(request, pk):
    fs = get_object_or_404(FeeStructure, pk=pk)
    if request.method == "POST":
        form = FeeStructureForm(request.POST, instance=fs)
        if form.is_valid():
            fs = form.save()
            html = render_to_string("finance/partials/fee_structure_row.html", {"fs": fs},request=request)
            return HttpResponse(html)
        return HttpResponse("Invalid data", status=400)

    form = FeeStructureForm(instance=fs)
    html = render_to_string("finance/partials/fee_structure_edit.html", {"form": form, "fs": fs},request=request)
    return HttpResponse(html)

def delete_fee_structure(request, pk):
    fs = get_object_or_404(FeeStructure, pk=pk)
    fs.delete()
    return HttpResponse("")  # HTMX will remove the row


def send_invoice(request, fs_id):
    """
    Generate invoices for all students in the class/session/term
    of this FeeStructure row.
    """
    fs = get_object_or_404(FeeStructure, id=fs_id)

    # 1. Get students in this class
    students = Student.objects.filter(
    myclasses__student_class=fs.school_class,
    myclasses__current_class=True
    )

    # 2. Get all fee structures for same class/session/term
    fee_structures = FeeStructure.objects.filter(
        school_class=fs.school_class,
        session=fs.session,
        term=fs.term
    ).select_related("category")

    invoices_created = []
    errors = []

    try:
        with transaction.atomic():
            for student in students:
                # avoid duplicate invoice
                if SchoolInvoice.objects.filter(student=student, session=fs.session, term=fs.term).exists():
                    errors.append(f"Invoice already exists for {student}")
                    continue
                
                now = timezone.now()
                invoice_number = f"INV-{now.year}-{int(now.timestamp() * 1_000_000)}"

                invoice = SchoolInvoice.objects.create(
                    student=student,
                    invoice_number=invoice_number,
                    session=fs.session,
                    term=fs.term,
                    issue_date=timezone.now(),
                    due_date=timezone.now() + timezone.timedelta(days=14)
                )

                items = [
                    InvoiceItem(
                        invoice=invoice,
                        category=struct.category,
                        description=struct.category.name,
                        amount=struct.amount
                    )
                    for struct in fee_structures
                ]
                InvoiceItem.objects.bulk_create(items)

                invoices_created.append(invoice_number)

        return JsonResponse({
            "status": "success",
            "message": f"{len(invoices_created)} invoices created.",
            "invoices": invoices_created,
            "errors": errors
        }, status=201)

    except DatabaseError as e:
        return JsonResponse({
            "status": "error",
            "message": "Invoice creation failed.",
            "details": str(e)
        }, status=500)

    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": "An unexpected error occurred.",
            "details": str(e)
        }, status=500)
