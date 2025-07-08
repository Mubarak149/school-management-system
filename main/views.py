import json
from django.shortcuts import render, redirect, get_object_or_404, get_list_or_404
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.contrib.auth import authenticate, login, logout
from .forms import CustomAuthenticationForm
from django.contrib import messages
from staff.models import Staff
from student.models import Student, StudentPromotionRecord
from school_admin.models import BlogPost, SchoolClass
from .models import *
# Create your views here.

def create_admission_numbers():
    current_session = AcademicSession.objects.last()  # Get the latest academic session
    
    for student in Student.objects.all():
        # Ensure the student has a current class
        student_class = student.get_current_class()
        if not student_class:
            print(f"Skipping {student}: No current class assigned.")
            continue

        # Ensure an admission record does not already exist for this student and session
        if Admission.objects.filter(student=student, session=current_session).exists():
            print(f"Skipping {student}: Admission record already exists.")
            continue

        category = student_class.class_name  # Extract category from the class
        position_count = Admission.objects.filter(category=category, session=current_session).count() + 1

        # Create admission record
        admission = Admission.objects.create(
            student=student,
            session=current_session,
            category=category,
            position_count=position_count
        )

        print(f"Created Admission No: {admission.admission_no} for {student}")
    
def main(request):
    # Admission.objects.all().delete()
    # create_admission_numbers()
    if request.method == 'POST':
        # Create a copy of POST data and convert the username to lowercase
        post_data = request.POST.copy()
        post_data['username'] = post_data['username'].lower()  # Convert username to lowercase
        
        # Pass modified data to the form
        login_form = CustomAuthenticationForm(request, data=post_data)
        
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            
            # Authenticate user
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                try:
                    # Check user type and redirect accordingly
                    if user.user_type == '1':
                        return redirect(reverse('adminHome'))
                    elif user.user_type == '2':
                        if user.staff.is_teacher:
                            my_class_id = user.staff.teachers_set.filter(teacher=user.staff)[0].teacher_class.id
                            return redirect(reverse('staffHome', kwargs={"cls": my_class_id}))
                    elif user.user_type == '3':
                        return redirect(reverse('viewStudent', kwargs={"pk": user.student.id}))
                except (AttributeError, ObjectDoesNotExist, IndexError) as e:
                    messages.error(request, 'Error while processing user type.')
                    print(f'Error: {str(e)}')  # Optional: for debugging purposes
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            # Display form validation errors
            messages.error(request, f'{login_form.errors.as_text()}')

        return redirect(reverse('main'))
    
    # If GET request, render the login page with the form
    context = {'login_form': CustomAuthenticationForm()}
    return render(request, 'excellent-community/index.html', context)



def logout_view(request):
    logout(request)
    return redirect(reverse('main'))

def staff(request):
    STAFF_PER_ROW = 3
    
    def chunk_staff_list(staff_list, chunk_size):
        """Split staff list into rows of specified size"""
        return [staff_list[i:i + chunk_size] for i in range(0, len(staff_list), chunk_size)]

    try:
        # Get all active staff members
        active_staff_list = list(Staff.objects.filter(still_work=True))
        
        # Organize staff into rows
        staff_rows = chunk_staff_list(active_staff_list, STAFF_PER_ROW)
        
    except ObjectDoesNotExist:
        messages.error(request, "No active staff members found.")
        staff_rows = []

    context = {
        'login_form': CustomAuthenticationForm(),
        'staffs': staff_rows,
        'range_list': range(STAFF_PER_ROW),
    }
    
    return render(request, 'excellent-community/staff.html', context)

def about(request):
    context = {
            'login_form': CustomAuthenticationForm()
        }
        
    return render(request, 'excellent-community/about.html', context)

def contact(request):
    context = {
            'login_form': CustomAuthenticationForm()
        }
    return render(request, 'excellent-community/contact.html', context)

def status(request):
    context = {
            'login_form': CustomAuthenticationForm()
        }
    return render(request, 'excellent-community/Status.html', context)

def gallery(request):
    context = {
            'login_form': CustomAuthenticationForm()
        }
    return render(request, 'excellent-community/gallery.html', context)

def admission(request):
    context = {
            'login_form': CustomAuthenticationForm()
        }
    return render(request, 'excellent-community/admission.html', context)

def staff_hierarchy(request):
    admin_positions = [
        '1',  # Director
        '2',  # Principal
        '3',  # VP Administration
        '4',  # VP Academic
        '5',  # Senior Master Admin
        '7',  # Bursar
        '24', # Head Master
    ]

    administratives = Staff.objects.filter(work_title__in=admin_positions, still_work=True).order_by('work_title')

    return render(request, 'excellent-community/administratives.html', {
        'administratives': administratives
    })


def blog_view(request):
    blogs = BlogPost.objects.order_by('-date_sent')
    #creating blog json using list comprehension start
    blog_json = [
                    {
                    'id': blog.id,
                    'title':blog.title,
                    'content': blog.content,
                    'pic': blog.pic.url,
                    'date_sent': f'{blog.date_sent}'
                    }
                for blog in blogs  # Assuming `Staff` is your model
                ]
        #creating blog json end
        
    context = {
            'blog_json': json.dumps(blog_json),
            'login_form': CustomAuthenticationForm(),
        }
    return render(request, 'excellent-community/blog.html', context)

def graduate_view(request):
    if request.method == "POST":
        admission_number = request.POST.get('admission', '').strip()
        
        try:
            # Extract the category from the admission number (e.g., 'UPB' from 'ECSG/UPB//2024/2025//1')
            section = admission_number.split('/')[1].upper()

            # Map category code to database values
            category_mapping = {
                'LWB': 'lb',
                'MDLB': 'mb',
                'UPB': 'ub',
                'SS': 'ss'
            }
            
            if section not in category_mapping:
                messages.error(request, "Invalid Admission Number Format")
                return redirect(reverse('graduate_view'))

            # Retrieve the Admission record based on admission_no
            admission_obj = get_object_or_404(Admission, admission_no=admission_number)

            # Get all promotion records for the student
            promotion_records = list(StudentPromotionRecord.objects.filter(student=admission_obj.student))

            if not promotion_records:
                messages.error(request, "No Promotion Records Found")
                return redirect(reverse('graduate_view'))

            last_record = promotion_records[-1]
            student_classes = SchoolClass.objects.filter(studentclass__student=admission_obj.student)

            # Check graduation condition (if student has reached final class)
            class_condition = (
                last_record.promoted_class.id == student_classes.last().id or
                (len(student_classes) > 1 and last_record.promoted_class.id == list(student_classes)[-2].id)
            )

            # Prepare student JSON data
            student_json = [{
                'id': admission_obj.student.id,
                'name': f"{admission_obj.student.user.first_name} {admission_obj.student.user.last_name}",
                'reg_no': admission_obj.admission_no,
                'pic': admission_obj.student.pic.url if admission_obj.student.pic else None,
                'graduation_date': str(last_record.promotion_date),
                'graduation_status': class_condition
            }]

            # Prepare classes JSON data
            classes_json = [{
                'id': record.id,
                'class_name': f"{record.get_class_name_display()} {record.class_no} {record.get_class_type_display()} {record.get_class_category_display()}",
            } for record in student_classes]

            context = {
                'student_json': json.dumps(student_json),
                'classes_json': json.dumps(classes_json),
            }
            return render(request, 'excellent-community/studentDetails.html', context)

        except ObjectDoesNotExist as e:
            messages.error(request, 'Student or promotion record not found.')
            print(f'Error: {str(e)}')  # Debugging
            return redirect(reverse('graduate_view'))

    return render(request, "excellent-community/searchStudent.html")
