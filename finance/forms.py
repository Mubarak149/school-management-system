from django import forms
from .models import SchoolInvoice, InvoiceItem, Payment, FeeCategory


class FeeCategoryForm(forms.ModelForm):
    class Meta:
        model = FeeCategory
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter description'}),
        }



# Main Invoice Form
class InvoiceForm(forms.ModelForm):
    class Meta:
        model = SchoolInvoice
        fields = ["student", "invoice_number", "session", "term", "issue_date", "due_date", "status"]
        

# Invoice Item Form (each item has an amount + description)
class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ["description", "amount"]


class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ["invoice", "amount", "date_paid", "payment_method", "transaction_id"]
