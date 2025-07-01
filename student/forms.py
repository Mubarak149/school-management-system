from django import forms
from custom_user.models import User
from .models import *

class StudentUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','middle_name','last_name','email','password']
        
        widgets = {
        'first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
        'last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
        'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
        'email': forms.EmailInput(attrs={'class': 'form-control', 'required': True}),
        'password': forms.PasswordInput(attrs={'class': 'form-control', 'required': True, 'value':"12345678"}),
        }
        
class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['dob','nin','gender','enrollment_date','pic']
        
        widgets = {
        'gender': forms.Select(attrs={'class': 'form-select', 'required': True}),
        'nin': forms.TextInput(attrs={'class': 'form-control','required': False}),
        'pic': forms.FileInput(attrs={'class': 'form-control'}),
        }
        
class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = ['parent_first_name','parent_last_name', 'parent_middle_name', 'parent_gender','occupation', 'phone_no']
        
        widgets = {
        'parent_first_name': forms.TextInput(attrs={'class': 'form-control', 'required': True,'value':"Dahiru"}),
        'parent_last_name': forms.TextInput(attrs={'class': 'form-control', 'required': True,'value':"Ishaq"}),
        'parent_middle_name': forms.TextInput(attrs={'class': 'form-control'}),
        'parent_gender': forms.Select(attrs={'class': 'form-select', 'required': True}),
        'occupation':forms.TextInput(attrs={'class': 'form-control', 'value':"Trading"}),
        "phone_no": forms.TextInput(attrs={'class': 'form-control', 'required': False}),
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = StudentAddress
        fields = '__all__'
        
        
    
class StudentUserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name','middle_name','last_name','email']
        
        widgets = {
        'first_name': forms.TextInput(attrs={'class': 'form-control'}),
        'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
        'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        
class StudentEditForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['nin','gender', 'is_transfer','pic','student_active']
        # dont forget to put it back'dob',
        
        widgets = {
        'nin': forms.NumberInput(attrs={'class':'form-select'}),
        'gender': forms.Select(attrs={'class': 'form-control'}),
        'is_transfer': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        'pic': forms.FileInput(attrs={'class': 'form-control'}),
        'student_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
    
class ParentEditForm(forms.ModelForm):
        class Meta:
            model = Parent
            fields = '__all__'
            
            widgets = {
            'parent_first_name':forms.TextInput(attrs={'class': 'form-control'}),
            'parent_last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_no': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_gender': forms.Select(attrs={'class':'form-select'}),
            }
            
class ClassForm(forms.ModelForm):
    
    class Meta:
        model = StudentClass
        fields = ['student_class']
        
class StudentGradeForm(forms.ModelForm):
    class Meta:
        model = StudentsGrade
        fields = [
            'student',
            'subject',
            'total_score',
            'the_class',
            'term',
            'grade_session',
            ]
        
        widgets = {
            'total_score':forms.TextInput(attrs={'class': 'form-control'}),
            'subject':forms.Select(attrs={'class':'form-select'}),
            'the_class': forms.Select(attrs={'class':'form-select'}),
            'term': forms.Select(attrs={'class':'form-select'}),
            }
        
class StudentGradeEditForm(forms.ModelForm):
    class Meta:
        model = StudentsGrade
        fields = [
            'subject',
            'total_score',
            'term',
            ]
        
        widgets = {
            'subject': forms.Select(attrs={'class':'form-select'}),
            'total_score':forms.NumberInput(attrs={'class': 'form-control', 'max':100}),
            'term': forms.Select(attrs={'class':'form-select'}),
            }


class PicEdit(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['pic']