from django.shortcuts import render
from django.db.models import Sum
from .models import StudentSchoolFees
from student.models import Student
from school_admin.models import SchoolClass

def finance_dashboard(request):
    class_filter = request.GET.get("class")
    all_classes = SchoolClass.objects.all()
    all_students = Student.objects.all()

    if class_filter:
        all_students = all_students.filter(student_class__id=class_filter)

    # Get students who paid
    paid_fees = StudentSchoolFees.objects.filter(completed=True)
    paid_student_ids = paid_fees.values_list("student_id", flat=True).distinct()

    # Unpaid students
    unpaid_students = all_students.exclude(id__in=paid_student_ids)

    # Total amount collected
    total_collected = paid_fees.aggregate(Sum("price"))["price__sum"] or 0

    context = {
        "classes": all_classes,
        "selected_class": int(class_filter) if class_filter else None,
        "total_students": all_students.count(),
        "students_paid": paid_student_ids.count(),
        "students_unpaid": unpaid_students.count(),
        "unpaid_students": unpaid_students,
        "total_collected": total_collected,
    }
    return render(request, "finance/finance_dashboard.html", context)
