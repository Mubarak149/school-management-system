from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login, logout
from .forms import CustomAuthenticationForm
from django.contrib import messages
from staff.models import Staff
from .models import Admission
from student.models import StudentsGrade, StudentPromotionRecord, StudentSchoolFees
from .models import *
# Create your views here.

def main(request):
    active_notification = Notification.objects.filter(active=True).order_by('-created_at').first()
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
    context = {'login_form': CustomAuthenticationForm(),
               'active_notification':active_notification,
               }
    return render(request, 'excellent-community/index.html', context)


def logout_view(request):
    logout(request)
    return redirect(reverse('main'))

def about(request):
    context = {
            'login_form': CustomAuthenticationForm()
        }
        
    return render(request, 'excellent-community/about.html', context)

def status(request):
    context = {
            'login_form': CustomAuthenticationForm()
        }
    return render(request, 'excellent-community/Status.html', context)

def gallery_view(request):
    context = {'login_form': CustomAuthenticationForm(),
               'images': images,
               }
    images = GalleryImage.objects.all().order_by('-uploaded_at')
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
    context = {
            'login_form': CustomAuthenticationForm(),
            'administratives': administratives,
        }
    return render(request, 'excellent-community/administratives.html', context)


def search_student_academic_view(request):
    context = {'login_form': CustomAuthenticationForm(),}
    
    if request.method == 'POST':
        admission_number = request.POST.get('admission').strip()
        
        try:
            # Find the Admission record by matching admission_no property dynamically
            all_admissions = Admission.objects.all()
            admission_obj = next(
                (adm for adm in all_admissions if adm.admission_no == admission_number),
                None
            )

            if not admission_obj:
                raise ValueError("No student found with that admission number.")

            student = admission_obj.student

            # Retrieve academic records
            current_class = student.get_current_class()
            grades = StudentsGrade.objects.filter(student=student).select_related('subject', 'the_class', 'grade_session')
            promotions = StudentPromotionRecord.objects.filter(student=student).select_related('promoted_class', 'promotion_session')
            fees = StudentSchoolFees.objects.filter(student=student).select_related('paid_session')

            context = {
                'login_form': CustomAuthenticationForm(),
                'student': student,
                'admission': admission_obj,
                'current_class': current_class,
                'grades': grades,
                'promotions': promotions,
                'fees': fees,
                'admission_number': admission_number
            }
        except Exception as e:
            messages.error(request, f"Error: {e}")
            print(f"Search Error: {e}")

    return render(request, 'excellent-community/searchStudent.html', context)
