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
    classes = (
        ('lb','Lower Basic'),
        ('mb','Middle Basic'),
        ('ub','Upper Basic'),
        ('ss', 'SS'),
    )
    category = (
        ('science','Science'),
        ('art','Art'), 
        ('commercial','Commercial'),
        ('none','None'),
    )
    class_type_choice = (
        ('a','A'),
        ('b','B'),
        ('c','C'),
        ('d','D'),
        
    )
    class_name = models.CharField(choices=classes,default='lb',max_length=10)
    class_no = models.IntegerField()
    class_type = models.CharField(choices=class_type_choice,default='a',max_length=12)
    class_category = models.CharField(choices=category,default='none', max_length=50)
    
    def __str__(self):
        return f'{self.class_name} {self.class_no}{self.class_type} {self.class_category}'
    
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

