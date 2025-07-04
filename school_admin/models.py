from django.db import models
from django.utils import timezone
# Create your models here.
class Admin(models.Model):
    user = models.OneToOneField("custom_user.User", on_delete=models.CASCADE)
    contact = models.CharField(max_length=50)
    is_it_work = models.BooleanField(default=True)
    initial_work_date = models.DateField(auto_now_add=True)
    pic = models.ImageField(upload_to='staff_media', default='avater.avif')
 

class SchoolClass(models.Model):
    CLASS_LEVEL_CHOICES = (
        ('nursery', 'Nursery'),
        ('primary', 'Primary'),
        ('junior_secondary', 'Junior Secondary'),
        ('senior_secondary', 'Senior Secondary'),
        ('college', 'College'),
        ('other', 'Other'),
    )

    CLASS_TYPE_CHOICES = (
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D'),
        ('other', 'Other'),
    )

    CATEGORY_CHOICES = (
        ('science', 'Science'),
        ('art', 'Art'),
        ('commercial', 'Commercial'),
        ('general', 'General'),
        ('none', 'None'),
    )

    # Class level: Nursery, Primary, etc.
    class_level = models.CharField(
        max_length=20,
        choices=CLASS_LEVEL_CHOICES,
        default='primary'
    )

    # Class name or number (e.g. 1, 2, Basic 3, SS1)
    class_name = models.CharField(max_length=50)

    # Type within class (A, B, etc.)
    class_type = models.CharField(
        max_length=10,
        choices=CLASS_TYPE_CHOICES,
        default='a'
    )

    # Academic category (Science, Art, etc.)
    class_category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general'
    )

    def __str__(self):
        return f"{self.get_class_level_display()} {self.class_name}{self.class_type.upper()} ({self.class_category.capitalize()})"

    class Meta:
        ordering = ['class_level', 'class_name', 'class_type']
        verbose_name = "School Class"
        verbose_name_plural = "School Classes"

    
class Subjects(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name
    
class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    pic = models.ImageField(upload_to="Post_Picture", default='post.jpg')
    date_sent = models.DateField(default=timezone.now)
    
    def __str__(self):
        return f"{self.title} - {self.date_sent}"  


class SiteSetting(models.Model):
    site_name = models.CharField(max_length=100, default="Excellent Community School")
    logo = models.ImageField(upload_to='site/logo/', null=True, blank=True)
    principal_pic = models.ImageField(upload_to='site/principal/', null=True, blank=True)
    banner1 = models.ImageField(upload_to='site/banner/', null=True, blank=True)
    banner1_title = models.CharField(max_length=255, null=True, blank=True)
    banner1_text = models.TextField(null=True, blank=True)

    banner2 = models.ImageField(upload_to='site/banner/', null=True, blank=True)
    banner2_title = models.CharField(max_length=255, null=True, blank=True)
    banner2_text = models.TextField(null=True, blank=True)

    banner3 = models.ImageField(upload_to='site/banner/', null=True, blank=True)
    banner3_title = models.CharField(max_length=255, null=True, blank=True)
    banner3_text = models.TextField(null=True, blank=True)

    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=20)
    facebook_link = models.URLField(null=True, blank=True)
    instagram_link = models.URLField(null=True, blank=True)
    whatsapp_link = models.URLField(null=True, blank=True)
    google_link = models.URLField(null=True, blank=True)

    primary_color = models.CharField(max_length=7, default="#000000")  # For dynamic CSS colors

    def __str__(self):
        return self.site_name
