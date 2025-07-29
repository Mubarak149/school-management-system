from django.db import models
from main.models import AcademicSession

# Create your models here.
class StudentSchoolFees(models.Model):
    TERM = (
        ('1', "First Term"),
        ('2', "Second Term"),
        ('3', "Third Term")
    )
    student = models.ForeignKey("student.Student", on_delete=models.CASCADE, related_name='myschoolfees')
    price = models.IntegerField()
    date_paid = models.DateField(auto_now_add=True)
    date_updated = models.DateField(auto_now=True)
    completed = models.BooleanField(default=False)
    term = models.CharField(choices=TERM, default=1, max_length=50)
    paid_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    