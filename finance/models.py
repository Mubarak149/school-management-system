from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from student.models import Student
from school_admin.models import SchoolClass
from main.models import AcademicSession


class FeeCategory(models.Model):
    """Categories of fees (Tuition, Exam, Uniform, Transport, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class FeeStructure(models.Model):
    """
    Defines how much each class/session/term pays for a fee category.
    Example: SS1 Science - Tuition - ₦50,000
    """
    TERM_CHOICES = [
        ("1st", "First Term"),
        ("2nd", "Second Term"),
        ("3rd", "Third Term"),
    ]

    school_class = models.ForeignKey(SchoolClass, on_delete=models.CASCADE, related_name="fee_structures")
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    term = models.CharField(max_length=10, choices=TERM_CHOICES)
    category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ("school_class", "session", "term", "category")

    def __str__(self):
        return f"{self.school_class} - {self.category.name} - {self.amount} ({self.term}, {self.session.name})"


class SchoolInvoice(models.Model):
    STATUS_CHOICES = [
        ('unpaid', 'Unpaid'),
        ('partial', 'Partially Paid'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="invoices")
    invoice_number = models.CharField(max_length=20, unique=True)  # e.g., INV-2025-001
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    term = models.CharField(max_length=10, choices=[("1st", "First Term"), ("2nd", "Second Term"), ("3rd", "Third Term")])
    issue_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unpaid')

    def total_amount(self):
        return sum(item.amount for item in self.items.all())

    def amount_paid(self):
        return sum(payment.amount for payment in self.payments.all())

    def balance(self):
        return self.total_amount() - self.amount_paid()

    def update_status(self):
        paid = self.amount_paid()
        if paid == 0:
            self.status = 'unpaid'
        elif 0 < paid < self.total_amount():
            self.status = 'partial'
        elif paid >= self.total_amount():
            self.status = 'paid'
        self.save()

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.student}"


class InvoiceItem(models.Model):
    """Breakdown of each fee in the invoice"""
    invoice = models.ForeignKey(SchoolInvoice, on_delete=models.CASCADE, related_name="items")
    category = models.ForeignKey(FeeCategory, on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])

    def __str__(self):
        return f"{self.category} - {self.amount}"


class Payment(models.Model):
    """Stores payments for invoices"""
    invoice = models.ForeignKey(SchoolInvoice, on_delete=models.CASCADE, related_name="payments")
    amount = models.DecimalField(max_digits=12, decimal_places=2, validators=[MinValueValidator(0)])
    date_paid = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(
        max_length=20,
        choices=[("cash", "Cash"), ("bank", "Bank Transfer"), ("online", "Online Gateway")]
    )
    transaction_id = models.CharField(max_length=100, blank=True, null=True)  # for receipts/gateway

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # update invoice status whenever payment is recorded
        self.invoice.update_status()

    def __str__(self):
        return f"Payment of {self.amount} for {self.invoice.invoice_number}"
