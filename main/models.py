import datetime
from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.

        
class Admission(models.Model):
    CATEGORY = (
        ('lb','lwb'),
        ('mb','mdlb'),
        ('ub','upb'),
        ('ss','ss')
    )
    student = models.ForeignKey("student.Student", on_delete=models.CASCADE)
    session = models.ForeignKey("main.AcademicSession", on_delete=models.CASCADE)
    branch = models.CharField(max_length=50, default="ECSG")
    category = models.CharField(max_length=50, choices=CATEGORY)
    position_count = models.IntegerField()
    
    class Meta:
        unique_together = ('student', 'session', 'position_count')  # Ensure one record per student-session pair
        
    
    @property
    def admission_no(self):
        """Dynamically generate the admission number including the category"""
        session = self.session
        category_display = dict(self.CATEGORY).get(self.category, self.category).upper()
        count = self.position_count

        return f"{self.branch}/{category_display}//{session.start_year}/{session.end_year}//{count}"
    
    @classmethod
    def generate_admission_no(cls, student):
        category = student.studentclass_set.get(current_class=True).student_class.class_name
        session = student.enrollment_session
        count = cls.objects.filter(category=category, session=session).count() + 1
        # Get the default branch value
        branch_default = 'ECSG'
        return f"{branch_default}/{category.upper()}//{session.start_year}/{session.end_year}//{count}"
    
    @classmethod
    def get_students_by_category(cls, category):
        """Return all students in a specific category."""
        from student.models import Student
        return Student.objects.filter(admission__category=category)
    
    def save(self, *args, **kwargs):
        """Assign a unique position count for the category before saving"""
        if self.position_count is None:  # Ensure we only assign if it's a new record
            last_count = Admission.objects.filter(category=self.category, session=self.session).count()
            self.position_count = last_count + 1  # Increment count for this category
        
        super().save(*args, **kwargs)
        

class AcademicSession(models.Model):
    name = models.CharField(max_length=200, unique=True, blank=True)
    start_year = models.IntegerField()
    end_year = models.IntegerField()
    is_current = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_year']
        verbose_name = "Academic Session"
        verbose_name_plural = "Academic Sessions"
        constraints = [
            models.UniqueConstraint(
                fields=['start_year', 'end_year'],
                name='unique_academic_session'
            ),
            models.CheckConstraint(
                check=models.Q(end_year__gt=models.F('start_year')),
                name='end_year_after_start_year'
            )
        ]

    def clean(self):
        if self.end_year != self.start_year + 1:
            raise ValidationError("End year must be exactly one year after start year")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.clean()
        if not self.name:
            self.name = f"{self.start_year}/{self.end_year}"
        if self.is_current:
            AcademicSession.objects.exclude(id=self.id).update(is_current=False)
        super().save(*args, **kwargs)
        
    @classmethod
    def current_session_grades(self, student_instance):
        from student.models import StudentsGrade
        
        try:
            current_session = self.objects.get(is_current=True)
        except self.DoesNotExist:
            return {"error": "No active academic session found."}
        
        # Retrieve grades for all terms in the current session
        grades = StudentsGrade.objects.filter(
            student=student_instance,
            grade_session=current_session
        ).order_by('term')

        # Organizing results into a dictionary
        grades_dict = {
            "First_Term": [],
            "Second_Term": [],
            "Third_Term": []
        }

        term_mapping = {
            '1': "First_Term",
            '2': "Second_Term",
            '3': "Third_Term"
        }

        for grade in grades:
            term_name = term_mapping.get(grade.term, "Unknown Term")
            grades_dict[term_name].append({
                "subject": grade.subject.name,
                "score": grade.total_score,
                "session": grade.grade_session.name
            })

        return grades_dict

    
    @classmethod
    def session_grade(self,student_instance, session_instance):
        from student.models import StudentsGrade
        grades = StudentsGrade.objects.filter(
        student=student_instance,
        grade_session=session_instance,
        term='1',  # Replace with the desired term
    )
        return grades
