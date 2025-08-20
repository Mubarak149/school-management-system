from django.db import models
from django.utils import timezone
from PIL import Image
from django.core.exceptions import ValidationError
from io import BytesIO
from django.core.files.base import ContentFile
from .utils import resize_image_field
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
        category = f" ({self.class_category.capitalize()})" if self.class_category.lower() != 'none' else ""
        return f"{self.get_class_level_display()} {self.class_name}{self.class_type.upper()}{category}"
        
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
    # Basic Identity
    school_name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='site_logo/', blank=True, null=True)
    principal_name = models.CharField(max_length=255, blank=True, null=True)
    principal_image = models.ImageField(upload_to='principal_images/', blank=True, null=True)
    director_name = models.CharField(max_length=255, blank=True, null=True)
    director_image = models.ImageField(upload_to='director_images/', blank=True, null=True)

    # Banner Images and Texts
    banner1 = models.ImageField(upload_to='site/banner/', null=True, blank=True)
    banner1_title = models.CharField(max_length=255, null=True, blank=True)
    banner1_text = models.TextField(null=True, blank=True)

    banner2 = models.ImageField(upload_to='site/banner/', null=True, blank=True)
    banner2_title = models.CharField(max_length=255, null=True, blank=True)
    banner2_text = models.TextField(null=True, blank=True)

    banner3 = models.ImageField(upload_to='site/banner/', null=True, blank=True)
    banner3_title = models.CharField(max_length=255, null=True, blank=True)
    banner3_text = models.TextField(null=True, blank=True)

    # Contact Info
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    
    # Social Links
    facebook_link = models.URLField(blank=True, null=True)
    instagram_link = models.URLField(blank=True, null=True)
    whatsapp_link = models.URLField(blank=True, null=True)
    youtube_link = models.URLField(blank=True, null=True)

    # Brand Colours for Uniform and Site Branding
    primary_color = models.CharField(max_length=7, default="#000000")  # Main brand colour
    secondary_color = models.CharField(max_length=7, default="#FFFFFF")  # Complementary colour
    accent_color = models.CharField(max_length=7, null=True, blank=True)  # Optional accent colour
    
    mission = models.TextField(null=True, blank=True)
    vision = models.TextField(null=True, blank=True)


    def __str__(self):
        return self.school_name

    def save(self, *args, **kwargs):
        if self.principal_image:
            self.principal_image = resize_image_field(self.principal_image, 300, 300)

        if self.director_image:
            self.director_image = resize_image_field(self.director_image, 300, 300)

        if self.logo:
            self.logo = resize_image_field(self.logo, 200, 200)

        if self.banner1:
            self.banner1 = resize_image_field(self.banner1, 1200, 400)

        if self.banner2:
            self.banner2 = resize_image_field(self.banner2, 1200, 400)

        if self.banner3:
            self.banner3 = resize_image_field(self.banner3, 1200, 400)

        super().save(*args, **kwargs)
    

