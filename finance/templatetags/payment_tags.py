from django import template

register = template.Library()

@register.filter
def status_badge(status):
    """
    Return a Bootstrap badge HTML string for invoice/payment status
    """
    if status == "paid":
        css = "bg-success"
        label = "Paid"
    elif status == "pending":
        css = "bg-warning text-dark"
        label = "Pending"
    elif status == "overdue":
        css = "bg-danger"
        label = "Overdue"
    else:
        css = "bg-secondary"
        label = str(status).capitalize()

    return f'<span class="badge {css}">{label}</span>'
status_badge.is_safe = True   # so Django won’t escape the HTML
