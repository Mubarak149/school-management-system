import datetime
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from django.db import DatabaseError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from custom_user.models import User
from staff.models import Teachers
from school_admin.models import SchoolClass
from main.models import *
# Create your models here.

class Student(models.Model):
    #relations fields
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('student.Parent', on_delete=models.CASCADE)
    address = models.ForeignKey("student.StudentAddress", on_delete=models.CASCADE)
    #other fields
    GENDER=(
        ('male',"Male"),
        ('female',"Female"),
        ('other',"Other")
        )
    dob = models.DateField(auto_now=False, auto_now_add=False)
    reg_no = models.CharField(null=True, blank=True, max_length=12, unique=True)
    nin = models.CharField(null=True, blank=True, max_length=12, default='No NIN')
    gender = models.CharField(choices=GENDER,default='other', max_length=50)
    enrollment_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    enrollment_date = models.DateField(auto_now=False)
    graduation_date = models.DateField(default=timezone.datetime.now)
    is_transfer = models.BooleanField(default=False)
    pic = models.ImageField(upload_to='student_media', default='avater.avif')
    student_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name} ({self.user.email})"

    
    def get_current_class(self):
        student_class = StudentClass.objects.filter(student=self, current_class=True).first()
        return student_class.student_class if student_class else None
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
class StudentAddress(models.Model):
    state = models.CharField(null=True, blank=True, max_length=50, default='Kaduna')
    lga = models.CharField(null=True, blank=True, max_length=50, default='Giwa')
    ward = models.CharField(null=True, blank=True,max_length=50, default='Giwa')
    street = models.CharField(null=True, blank=True,max_length=50, default='Giwa')

class Parent(models.Model):
    GENDER=(
        ('male',"Male"),
        ('female',"Female"),
        ('other',"Other")
        )
    parent_first_name = models.CharField(max_length=50)
    parent_last_name = models.CharField(max_length=50)
    parent_middle_name = models.CharField(null=True, blank=True,max_length=50)
    occupation = models.CharField(max_length=50, null=True, blank=True, default='No Job')
    phone_no = models.CharField(null=True, blank=True,max_length=50, default='09012345678')
    parent_gender = models.CharField(default='male',choices=GENDER,max_length=50)


class StudentsGrade(models.Model):
    TERM = (
        ('1', "First Term"),
        ('2', "Second Term"),
        ('3', "Third Term")
    )
    student = models.ForeignKey("student.Student", on_delete=models.CASCADE, related_name='mygrades')
    subject = models.ForeignKey("school_admin.Subjects", on_delete=models.CASCADE, related_name='student_grade')
    total_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    the_class = models.ForeignKey("school_admin.SchoolClass", on_delete=models.CASCADE, related_name='grades')
    record_date = models.DateField(default=timezone.now)
    term = models.CharField(choices=TERM, default=1, max_length=50)
    grade_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='session_grades')
    year = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(datetime.date.today().year)],
        default=datetime.date.today().year
    )

    def __str__(self):
        return f'{self.student} - {self.subject} - Term: {self.term} - Year: {self.year}'
    
    class Meta:
        unique_together = ('student','term', 'grade_session', 'subject', 'the_class')
        
    @classmethod
    def get_student_grades_by_term_and_session(self, the_student, term, session):
        try:
            # Get all subjects and their scores for the specified student, term, and year
            grades = list(
                self.objects.filter(student=the_student, term=term, grade_session=session).values('total_score')
            )
            message = "Success"
            return [message, grades]
        except ObjectDoesNotExist:
            message = "Error: No grades found for the specified student, term, or year."
            print("Error: No grades found for the specified student, term, or year.")
            return [None,message]
        except ValueError:
            message = "Error: Invalid input for student, term, or year."
            print("Error: Invalid input for student, term, or year.")
            return [None,message]
        except DatabaseError as e:
            message = f"Database error: {e}"
            print(f"Database error: {e}")
            return [None,message]
        except Exception as e:
            message = f"An unexpected error occurred: {e}"
            print(f"An unexpected error occurred: {e}")
            return [None,message]

    @classmethod
    def calculate_total_score(cls, the_student, term, session):
        try:
            # Retrieve all total scores for the student for the specified term and year session
            student_scores = cls.get_student_grades_by_term_and_session(the_student, term, session)
            # Check if retrieval was successful
            if student_scores[0] is None:
                raise ValueError(f"Failed to retrieve student scores.{student_scores[1]}")
            student_scores = student_scores[1]
            # Sum up all the total scores in the list
            combined_score = sum(score['total_score'] for score in student_scores)
            return combined_score

        except ValueError as ve:
            print(f"Value error: {ve}")
            return None
        except Exception as e:
            # Handle any other unexpected errors
            print(f"An error occurred: {e}")
            return None



class StudentClassManager(models.Manager):
    def get_current_class(self, student):
        """
        Returns the current class of a student.

        Args:
            student (Student): The student instance.

        Returns:
            StudentClass instance or None if no current class is found.
        """
        return self.filter(student=student, current_class=True).first()

    def assign_class(self, student, school_class, session):
        """
        Assigns a new class to a student and ensures only one class is marked as current.

        Args:
            student (Student): The student instance.
            school_class (SchoolClass): The class to assign.
            session (AcademicSession): The academic session.

        Returns:
            StudentClass instance: The newly assigned current class.
        """
        with transaction.atomic():
            # Set all other classes for the student to `current_class=False`
            self.filter(student=student, current_class=True).update(current_class=False)

            # Create and return the new current class
            return self.create(
                student=student,
                student_class=school_class,
                session_attend_class=session,
                current_class=True
            )
    def get_current_classes(self):
        """Get all current class assignments"""
        return self.get_queryset().filter(current_class=True)
    
    def get_student_current_class(self, student):
        """Get a student's current class"""
        return self.get_queryset().filter(
            student=student,
            current_class=True
        ).select_related('student_class').first()

class StudentClass(models.Model):  
    student = models.ForeignKey("student.Student", on_delete=models.CASCADE, related_name='myclasses')
    student_class = models.ForeignKey("school_admin.SchoolClass", on_delete=models.CASCADE, related_name='students')
    current_class = models.BooleanField(default=True)
    session_attend_class = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    date_attend_class = models.DateField(auto_now_add=True)

    objects = StudentClassManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student"],
                condition=models.Q(current_class=True),
                name="unique_current_class_per_student"
            )
        ]

    def save(self, *args, **kwargs):
        """
        Ensure that only one `current_class=True` exists for a student.
        """
        if self.current_class:
            # Set all other student classes to `False`
            StudentClass.objects.filter(student=self.student, current_class=True).update(current_class=False)
        
        super().save(*args, **kwargs)


class StudentPromotionRecord(models.Model):
    student = models.ForeignKey("student.Student",on_delete=models.CASCADE)
    promoted_class = models.ForeignKey("school_admin.SchoolClass", on_delete=models.CASCADE)
    promotion_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    promotion_date = models.DateField(default=timezone.now)
    promoted_score = models.IntegerField( validators=[MinValueValidator(0)] )
    promotion_year = models.IntegerField(
        validators=[MinValueValidator(1900), MaxValueValidator(datetime.date.today().year)],
        default=datetime.date.today().year
    )
    is_promoted = models.BooleanField()
    
    class Meta:
        unique_together = ('promotion_session', 'student')