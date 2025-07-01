from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
# Create your models here.


WORK_TITLES = (
        ('1','Director'),
        ('2','Principal'),
        ('3','VP Administration'),
        ('4', 'VP Academic'),
        ('5', 'Senior Master Admin'),
        ('6', 'Senior Master Acad'),
        ('7', 'Bursar'),
        ('8', 'Assistant Bursar'),
        ("9", "Exam's Officer"),
        ("10", "Assistant Exam's Officer"),
        ("11", 'Maintenance'),
        ('12', 'Assistant Maintenance'),
        ('13', 'Sport Master'),
        ('14', 'Health Master'),
        ('15', 'Assistant Health Master'),
        ('16', 'Displine Master'),
        ('17', 'Assistant Discipline Master'),
        ('18', 'Liberian'),
        ('19', 'Guidance and Counselling'),
        ('20', 'Assistant Guidance and Counselling'),
        ('21', 'HODLanguage'),
        ('22', 'HOD science'),
        ('23', 'HOD Art'),
        ('24', 'Head Master'),
        ('25', 'Assisstant Head Master 1'),
        ('26', 'Assisstant Head Master 2'),
        ('27', 'Non Academic Staff'),
        ('28', 'Academic Staff'),
    )

GENDER=(
        ('male',"Male"),
        ('female',"Female"),
        ('other',"Other")
        )
class Staff(models.Model):
    staff_user = models.OneToOneField("custom_user.User", on_delete=models.CASCADE)
    staff_gender = models.CharField(default='other',choices=GENDER,max_length=50)
    work_title = models.CharField(choices=WORK_TITLES,max_length=100)
    still_work = models.BooleanField(default=True)
    staff_pic = models.ImageField(default='avater.avif', upload_to='staff_picture')
    staff_contact = models.CharField(max_length=12, blank=True, null=True)
    staff_nin = models.CharField(max_length=12, blank=True, null=True)
    is_teacher = models.BooleanField(default=False)
    start_work_date = models.DateField(auto_now_add=True, blank=True, null=True)
    
class Teachers(models.Model):
    teacher = models.ForeignKey("staff.Staff", on_delete=models.CASCADE)
    teacher_subject = models.ForeignKey("school_admin.Subjects", on_delete=models.CASCADE)
    teacher_class = models.ForeignKey("school_admin.SchoolClass", on_delete=models.CASCADE)

    class Meta:
        unique_together = ('teacher', 'teacher_subject', 'teacher_class')
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"
        ordering = ["teacher"]
    
    def save(self, *args, **kwargs):
        # Check how many unique subjects this teacher already has
        subject_count = Teachers.objects.filter(teacher=self.teacher).values('teacher_subject').distinct().count()
        """
        if self.pk is None:  # if creating a new instance
            if subject_count >= 3:
                raise ValidationError(f'{self.teacher} is already assigned to the maximum number of 3 subjects.')
        else:  # if updating an existing instance
            if subject_count > 3:
                raise ValidationError(f'{self.teacher} is already assigned to the maximum number of 3 subjects.')
        """
        super().save(*args, **kwargs)

class Promoter(models.Model):
    promoter = models.ForeignKey(Staff, on_delete=models.CASCADE)
    school_class = models.OneToOneField("school_admin.SchoolClass", on_delete=models.CASCADE, blank=True,null=True)  # A class can have only one promoter
