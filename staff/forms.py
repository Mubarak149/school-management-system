from django import forms
from custom_user.models import User
from .models import *

class StaffUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','middle_name','last_name','email','password']


class StaffUserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','middle_name','last_name','email']
        
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }


class NewStaffForm(forms.ModelForm):
    
    class Meta:
        model = Staff
        fields = ['staff_gender','work_title','staff_pic','staff_contact', 'staff_nin', 'is_teacher']
        
        widgets = {
        'staff_nin': forms.TextInput(attrs={'class': 'form-control'}),
        'work_title': forms.Select(attrs={'class': 'form-select', 'required': True}),
        'staff_gender': forms.Select(attrs={'class': 'form-select', 'required': True}),
        'staff_pic':forms.FileInput(attrs={'class': 'form-control'}),
        "staff_contact": forms.TextInput(attrs={'class': 'form-control', 'value':"07034567789"}),
        }
        
class EditStaffForm(forms.ModelForm):
    
    class Meta:
        model = Staff
        fields = ['staff_gender','work_title','staff_pic','staff_contact','is_teacher']
        
        widgets = {
            'work_title':forms.Select(attrs={'class':'form-select'}),
            'staff_contact': forms.TextInput(attrs={'class': 'form-control'}),
            'is_teacher': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'staff_gender':forms.Select(attrs={'class':'form-select'}),
        }
        
class NewTeacherForm(forms.ModelForm):
    
    class Meta:
        model = Teachers
        fields = ['teacher_subject', 'teacher_class']

