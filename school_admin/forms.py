from django import forms
from .models import *
from main.models import AcademicSession
from custom_user.models import User


class AdminUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','middle_name','last_name','email','password']
        

class AdminUserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','middle_name','last_name','email']
        
        widgets = {
        'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True,'value':"Dahiru"}),
        'middle_name': forms.TextInput(attrs={'class': 'form-control','value':"Ishaq"}),
        'last_name': forms.TextInput(attrs={'class': 'form-control', 'value':"Magaji"}),
        'email': forms.EmailInput(attrs={'class': 'form-control', 'value':"admin@gmail.com",'required': True}),
        }
    
class AdminEditForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = ['pic', 'contact','is_it_work']
        
        widgets = {
            'is_it_work': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'contact': forms.TextInput(attrs={'class': 'form-control', 'required': True,'value':"091234567"}),
            'pic': forms.FileInput(attrs={'class': 'form-control'}),
        }
#i can use it for editing
class NewAdminForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = ['pic', 'contact']

        
class PostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'content', 'pic']
        
class AcademicSessionForm(forms.ModelForm):
    class Meta:
        model = AcademicSession
        fields = "__all__"
        
class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subjects
        fields = ['name']
        

class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = ['class_level', 'class_name', 'class_type', 'class_category']
        widgets = {
            'class_level': forms.Select(attrs={'class': 'form-control'}),
            'class_name': forms.TextInput(attrs={'class': 'form-control'}),
            'class_type': forms.Select(attrs={'class': 'form-control'}),
            'class_category': forms.Select(attrs={'class': 'form-control'}),
        }