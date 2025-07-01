from django_use_email_as_username.models import BaseUser, BaseUserManager
from django.db import models

class User(BaseUser):
    user_type_data=(
        ('1',"Admin"),
        ('2',"Staff"),
        ('3',"Student")
        )
    user_type=models.CharField(default=1,choices=user_type_data,max_length=10)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    
    
    objects = BaseUserManager()

    def __str__(self):
        return self.email 
    
    def save(self, *args, **kwargs):
        # Ensure the email is saved in lowercase
        if self.email:
            self.email = self.email.lower()
        super(User, self).save(*args, **kwargs)