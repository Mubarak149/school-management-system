# finance/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Payment, SchoolInvoice

@receiver(post_save, sender=Payment)
def update_invoice_on_payment(sender, instance, created, **kwargs):
    """
    Update invoice status whenever a payment is created or updated.
    """
    if created or instance.amount:  # covers create and update
        instance.invoice.update_status()


@receiver(post_delete, sender=Payment)
def update_invoice_on_payment_delete(sender, instance, **kwargs):
    """
    Recalculate invoice status if a payment is deleted.
    """
    instance.invoice.update_status()
