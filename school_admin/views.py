import json
from django.db import transaction
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import render,redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from main.models import *
from student.forms import *
from staff.forms import *
from staff.models import Staff
from .models import *
from .forms import *
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
# Create your views here.
from django.core.exceptions import ObjectDoesNotExist

def get_admission_no(the_student):
    try:
        # Get the student's current class
        student_class_instance = StudentClass.objects.get(student=the_student, current_class=True)
        class_name = student_class_instance.student_class.class_name  # 'lb', 'mb', 'ub', or 'ss'
    except ObjectDoesNotExist:
        return None  # No current class found

    try:
        # Get the current academic session
        current_session = AcademicSession.objects.get(is_current=True)

        # Retrieve the admission record for the student in the current session
        the_admission_no = Admission.objects.get(student=the_student, category=class_name, session=current_session)
        return the_admission_no  # Return the generated admission number
    except (Admission.DoesNotExist, AcademicSession.DoesNotExist):
        return None  # No admission record or current session found
    

def update_admission_no(the_student, post_data):
    try:
        # Get the student's current class
        student_class_instance = StudentClass.objects.get(student=the_student, current_class=True)
        class_name = student_class_instance.student_class.class_name  # 'lb', 'mb', 'ub', or 'ss'
    except ObjectDoesNotExist:
        return None  # No current class found

    try:
        # Get the current academic session
        current_session = AcademicSession.objects.get(is_current=True)

        # Fetch the student's admission record for the current session
        admission_record = Admission.objects.get(student=the_student, category=class_name, session=current_session)

        # Update admission number if the key exists in post_data
        new_admission_no = post_data.get("admission_no", "").strip()
        if new_admission_no:
            admission_record.admission_no = new_admission_no
            admission_record.save()
            return admission_record.admission_no  # Return the updated admission number

    except (Admission.DoesNotExist, AcademicSession.DoesNotExist):
        return None  # No admission record or current session found

    return None


#admin start here
def home(request):
    try:
        if request.user.user_type == '1':  # Admin
            active_students = Student.objects.filter(student_active=True).order_by('enrollment_date')
            non_active_students = Student.objects.filter(student_active=False)
            staffs = Staff.objects.all()
            active_staffs = Staff.objects.filter(still_work=True)  # querying current staff
            teachers = Staff.objects.filter(is_teacher=True)  # querying academic staff
            classes = SchoolClass.objects.all()
            parent = ParentForm()
            student_address = AddressForm()

            # Pagination setup
            per_page = 100  # Adjust number of students per page
            page_number = request.GET.get('page')  # Get page number from request
            paginator = Paginator(active_students, per_page)
            students_page = paginator.get_page(page_number)  # Get paginated students

            # Create student JSON
            Students_obj = [
                {
                    'avatar': student.pic.url if student.pic else '',
                    'firstname': student.user.first_name,
                    'lastname': student.user.last_name,
                    'email': student.user.email,
                    'enrollment_date': str(student.enrollment_date),
                    'active': student.student_active,
                    'id': student.id,
                } for student in students_page  # Use paginated students
            ]

            # Create staff JSON
            Staffs_obj = [
                {
                    'avatar': str(staff.staff_pic.url) if staff.staff_pic else '',
                    'firstname': staff.staff_user.first_name,
                    'lastname': staff.staff_user.last_name,
                    'email': staff.staff_user.email,
                    'start_work_date': staff.start_work_date.strftime('%Y-%m-%d'),
                    'active': staff.still_work,
                    'work_title': str(staff.get_work_title_display()),
                    'id': staff.id,
                } for staff in active_staffs
            ]

            context = {
                'sessions': AcademicSession.objects.all(),
                'classes': classes,
                'student': None,
                'student_json': json.dumps(Students_obj),  # Serialize student data to JSON
                'staff_form': NewStaffForm(),
                'non_active_students': non_active_students,
                'staffs': active_staffs,
                'staff_json': json.dumps(Staffs_obj),  # Serialize staff data to JSON
                'student_form': StudentForm(),
                'user_form': StudentUserForm(),
                'parent_form': parent,
                'student_address': student_address,
                'student_count': Student.objects.count(),
                'staff_count': staffs.count(),
                'teacher_count': teachers.count(),
                'students_page': students_page,  # Pass paginated students
            }
            return render(request, 'school-admin/admin_dashboard/index.html', context)


        elif request.user.user_type == '2':  # Staff
            messages.error(request, "Only Admins can access this page")
            the_staff = Staff.objects.get(staff_user=request.user)
            if the_staff.is_teacher:
                try:
                    the_staff_teacher_obj = Teachers.objects.filter(teacher=the_staff).first()
                    the_teacher_class = the_staff_teacher_obj.teacher_class.id
                    return redirect(reverse('staffHome', kwargs={'cls': the_teacher_class}))
                except AttributeError:
                    messages.error(request, "Error finding the teacher's class.")
                    return redirect(reverse('main'))
            else:
                messages.error(request, "You are not a teacher, you can't access that page.")
                return redirect(reverse('main'))

        elif request.user.user_type == '3':  # Student
            messages.error(request, "You don't have access to this page.")
            return redirect(reverse('viewStudent', kwargs={"pk": request.user.student.id}))

    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect(reverse('main'))
        
@login_required
@transaction.atomic
def add_new_admin(request):
    if request.method == 'POST':
        admin_form = NewAdminForm(request.POST, request.FILES)
        user_form = AdminUserForm(request.POST)
        
        if admin_form.is_valid() and user_form.is_valid():
            try:
                # Create user instance for the admin
                user_instance = User.objects.create_user(
                    email=user_form.cleaned_data['email'].lower(),
                    password=user_form.cleaned_data['password'],
                    user_type=1,  # 1 corresponds to "Admin"
                    middle_name=user_form.cleaned_data['middle_name'],
                    first_name=user_form.cleaned_data['first_name'],
                    last_name=user_form.cleaned_data['last_name'],
                )
                
                # Create the admin instance linked to the user
                admin = Admin.objects.create(
                    user=user_instance,
                    contact=admin_form.cleaned_data['contact'],
                    pic=admin_form.cleaned_data['pic'],
                )
                
                user_instance.save()
                admin.save()
                
                messages.success(request, 'You successfully added a new admin.')
                return redirect(reverse('adminHome'))
            except Exception as e:
                # Rollback if something goes wrong
                transaction.rollback()
                messages.error(request, f"An error occurred: {str(e)}")
                return redirect(reverse('adminHome'))
        else:
            # If forms are not valid, display errors
            messages.error(request, user_form.errors.as_text() + admin_form.errors.as_text())
    
    else:
        # If GET request, render the form
        admin_form = NewAdminForm()
        user_form = AdminUserForm()
        context = {
            'admin_form': admin_form,
            'user_form': user_form,
        }
        return render(request, 'school-admin/admin_dashboard/newadmin.html', context)
 
class MyProfile(LoginRequiredMixin, DetailView):
    model = Admin
    template_name = 'school-admin/admin_dashboard/profile.html'
    context_object_name = 'admin'

    def get_object(self):
        try:
            # Ensure the admin profile belongs to the logged-in user
            return get_object_or_404(Admin, user=self.request.user)
        except Admin.DoesNotExist:
            # If no Admin profile exists for the logged-in user, raise a 404 or handle the error
            messages.error(self.request, "Profile not found. Please contact support.")
            return redirect(reverse_lazy('adminHome'))  # Redirect to the admin home page

    def handle_no_permission(self):
        messages.error(self.request, "You need to log in to view your profile.")
        return redirect(reverse_lazy('main'))  # Redirect to login if user is not authenticated

@login_required
def settings(request):
    try:
        admin_user = request.user
        the_admin = Admin.objects.get(user=admin_user)
    except Admin.DoesNotExist:
        messages.error(request, 'Admin profile does not exist.')
        return redirect(reverse('adminHome'))
    except Exception as e:
        messages.error(request, f'An unexpected error occurred: {str(e)}')
        return redirect(reverse('adminHome'))

    if request.method == 'POST':
        promotion_status = request.POST.get('promotion')
        admin_user_form = AdminUserEditForm(request.POST, instance=the_admin.user)
        admin_form = AdminEditForm(request.POST, request.FILES, instance=the_admin)

        if admin_user_form.is_valid() and admin_form.is_valid():
            try:
                # Save user details
                admin_user = admin_user_form.save(commit=False)
                password = request.POST.get('password', None)
                if password:
                    admin_user.set_password(password)  # Update password if provided
                
                admin_user.save()
                admin_form.save()

                # Handle promotion logic if required
                if promotion_status == 'on':
                    print('let promote')
                
                messages.success(request, 'Admin updated successfully.')
                return redirect(reverse('adminHome'))
            except Exception as e:
                messages.error(request, f'Error during update: {str(e)}')
                return redirect(reverse('adminHome'))
        else:
            messages.error(request, f'Update failed: {admin_user_form.errors.as_text()} | {admin_form.errors.as_text()}')
            return redirect(reverse('adminHome'))

    # If not a POST request, display the form
    context = {
        'admin_user_form': AdminUserEditForm(instance=the_admin.user),
        'admin_form': AdminEditForm(instance=the_admin),
    }
    return render(request, 'school-admin/admin_dashboard/adminSetting.html', context)

#admin ends here

#blog Views S

class SchoolNews(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = BlogPost
    template_name = 'school-admin/admin_dashboard/schoolnews.html'
    form_class = PostForm

    def get_success_url(self):
        messages.success(self.request, 'You have successfully made a post.')
        return reverse('Blog')

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            form.save()
            return self.form_valid(form)
        else:
            messages.error(self.request, 'There was an error with your submission. Please correct the errors below.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Form submission failed. Please check the form and try again.')
        return super().form_invalid(form)

    def form_valid(self, form):
        messages.success(self.request, 'Your post has been successfully created.')
        return super().form_valid(form)

    # This function restricts access to only admin users
    def test_func(self):
        try:
            return self.request.user.is_authenticated and self.request.user.user_type == '1'
        except AttributeError:
            messages.error(self.request, 'You do not have the correct permissions.')
            return False

    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access this page.')
        return redirect('main')  # Redirect to a page (like the login page or homepage) if the user isn't an admin

class EditPost(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = BlogPost
    template_name = 'school-admin/admin_dashboard/edit_post.html'
    form_class = PostForm

    def get_success_url(self):
        messages.success(self.request, 'The post has been successfully updated.')
        return reverse_lazy('Blog')

    def form_valid(self, form):
        messages.success(self.request, 'Post updated successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)

    # Restrict access to admin users
    def test_func(self):
        try:
            return self.request.user.is_authenticated and self.request.user.user_type == '1'
        except AttributeError:
            messages.error(self.request, 'You do not have the correct permissions.')
            return False

    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access this page.')
        return redirect('main')

    # Handle object not found error
    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except ObjectDoesNotExist:
            messages.error(self.request, 'The post you are trying to edit does not exist.')
            return redirect('Blog')

class DeletePost(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = BlogPost
    template_name = 'school-admin/admin_dashboard/delete_post.html'
    success_url = reverse_lazy('Blog')

    def delete(self, request, *args, **kwargs):
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(request, 'The post has been successfully deleted.')
            return response
        except ObjectDoesNotExist:
            messages.error(request, 'The post you are trying to delete does not exist.')
            return redirect('Blog')

    # Restrict access to admin users
    def test_func(self):
        try:
            return self.request.user.is_authenticated and self.request.user.user_type == '1'
        except AttributeError:
            messages.error(self.request, 'You do not have the correct permissions.')
            return False

    def handle_no_permission(self):
        messages.error(self.request, 'You do not have permission to access this page.')
        return redirect('main')

    # Handle object not found error
    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except ObjectDoesNotExist:
            messages.error(self.request, 'The post you are trying to delete does not exist.')
            return redirect('Blog')
#blog views E


@login_required
def add_new_student(request):
    if request.method == 'POST':
        student_form = StudentForm(request.POST, request.FILES)
        user_form = StudentUserForm(request.POST)
        parent_form = ParentForm(request.POST)
        student_address_form = AddressForm(request.POST)
        new_class_form = ClassForm(request.POST)
        class_id = request.POST.get('student_class')
        session_id = request.POST.get('session')

        # Validate all forms
        valid_forms = all([
            student_form.is_valid(),
            user_form.is_valid(),
            parent_form.is_valid(),
            student_address_form.is_valid(),
            new_class_form.is_valid()
        ])

        if not valid_forms:
            messages.error(request, "Form validation failed. Please check your inputs.")
            return redirect(reverse('adminHome'))

        try:
            session = AcademicSession.objects.get(id=int(session_id))

            with transaction.atomic():
                # Create Student Address
                address = StudentAddress.objects.create(**student_address_form.cleaned_data)

                # Create Parent
                parent = Parent.objects.create(**parent_form.cleaned_data)

                # Create User
                user = User.objects.create_user(
                    email=user_form.cleaned_data['email'],
                    password=user_form.cleaned_data['password'],
                    user_type=3,  # Student user type
                    middle_name=user_form.cleaned_data['middle_name'],
                    first_name=user_form.cleaned_data['first_name'],
                    last_name=user_form.cleaned_data['last_name'],
                )

                # Create Student
                student = Student.objects.create(
                    user=user,
                    parent=parent,
                    address=address,
                    dob=student_form.cleaned_data["dob"],
                    nin=student_form.cleaned_data["nin"],
                    gender=student_form.cleaned_data["gender"],
                    enrollment_session=session,
                    enrollment_date=student_form.cleaned_data["enrollment_date"],
                    is_transfer=False,
                    pic=student_form.cleaned_data["pic"]
                )

                # Create Student Class Record
                student_class = new_class_form.cleaned_data['student_class']
                stclass = StudentClass.objects.create(
                    student=student,
                    student_class=student_class,
                    session_attend_class=session
                )

                # Create Admission Record for Current Session
                admission = Admission.objects.create(
                    student=student,
                    category=stclass.student_class.class_name,
                    session=session
                )

                messages.success(request, f'Successfully added student: {student.user.first_name} {student.user.last_name}.')
                return redirect(reverse('adminHome'))

        except IntegrityError as e:
            messages.error(request, f'Database error: {str(e)}')

        except ObjectDoesNotExist as e:
            messages.error(request, f'Data retrieval error: {str(e)}')

        except KeyError:
            messages.error(request, 'A required field is missing. Please try again.')

        except Exception as e:
            messages.error(request, f'An unexpected error occurred: {str(e)}')

    return redirect(reverse('adminHome'))


@login_required
def edit_student(request, id):
    try:
        # Retrieve the student and their admission number
        the_student = Student.objects.get(id=id)
        the_admission_no = get_admission_no(the_student)
        
        if the_admission_no == None:
            messages.error(request, 'Admission number does not exist.')
            return redirect(reverse('adminHome'))
        
    except Student.DoesNotExist:
        messages.error(request, 'Student does not exist.')
        return redirect(reverse('adminHome'))
    
    except Exception as e:
        messages.error(request, f'An unexpected error occurred: {str(e)}')
        return redirect(reverse('adminHome'))


    if request.method == 'POST':
        # Instantiate forms with POST data and existing instances
        user_form = StudentUserEditForm(request.POST, instance=the_student.user)
        student_form = StudentEditForm(request.POST, request.FILES, instance=the_student)
        parent_form = ParentEditForm(request.POST, instance=the_student.parent)
        

        # Ensure admission_form is not None before validating
        if all([user_form.is_valid(), student_form.is_valid(), parent_form.is_valid()]):
            try:
                # Save user form with password update if provided
                student_user = user_form.save(commit=False)
                password = request.POST.get('password', None)
                if password:
                    student_user.set_password(password)
                student_user.save()

                # Save other forms
                student_form.save()
                parent_form.save()

                messages.success(request, 'Student information updated successfully!')
                return redirect(reverse('adminHome'))

            except Exception as e:
                messages.error(request, f'Failed to update student: {str(e)}')

        else:
            messages.error(request, 'Please correct the errors below.')
    # If GET request or form submission fails, render the form with current data
    sessions = AcademicSession.objects.all()
    student_session = the_student.enrollment_session
    context = {
        'sessions':sessions,
        'student_session': student_session,
        'user_form': StudentUserEditForm(instance=the_student.user),
        'student_form': StudentEditForm(instance=the_student),
        'parent_form': ParentEditForm(instance=the_student.parent),
        'admission_no': the_admission_no.admission_no,
    }
    return render(request, 'school-admin/admin_dashboard/edit.html', context)


@login_required
def delete_student(request, pk):
    try:
        # Attempt to retrieve and delete the student
        the_student = Student.objects.get(id=pk)
        the_user = the_student.user
        the_user.delete()
        the_student.delete()
        messages.success(request, "Student successfully deleted.")
    except Student.DoesNotExist:
        messages.error(request, "Student not found.")
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
    
    return redirect(reverse('adminHome'))
    
def students_view(request):
    
    CLASS_NAME_DISPLAY = {
    'lb': 'Lower Basic',
    'mb': 'Middle Basic',
    'ub': 'Upper Basic',
    'ss': 'Senior Secondary',
    }
    classes = SchoolClass.objects.all()
    records = []  # Initialize records list outside the loop
    session = AcademicSession.objects.get(is_current=True)
    for the_class in classes:
        students_in_class = Student.objects.filter(
            student_active=True,
            studentclass__student_class=the_class,
            studentclass__current_class=True  # Ensuring it's the current class
        )

        student_count = students_in_class.count()  # Count the number of students in the class

        for student in students_in_class:
            # Fetch the admission number from the correct model (adjust based on your logic)
            try:
                admission_record = Admission.objects.get(student=student,session=session)
                admission_no = admission_record.admission_no if admission_record else 'N/A'
            except (Admission.DoesNotExist, AttributeError):
                admission_no = 'N/A'  # Handle cases where admission record is not found
                
            class_name_display = the_class.get_class_name_display()

            # Append the student's class and admission details to the records
            records.append({
                'class_name': f"{class_name_display} {the_class.class_no}{the_class.class_type.upper()}",
                'student_count': student_count,
                'name': student.user.first_name,   # Assuming 'user' is a related field in the Student model
                'surname': student.user.last_name, # Adjust if necessary
                'admission_no': admission_no,
                'email': student.user.email,
            })

    return render(request, 'school-admin/admin_dashboard/studentdownload.html', {'student_json': records})
    
    
   
def assign_positions(data, score_key='total_score'):
    """
    Assigns positions based on the highest score in descending order.

    Parameters:
    - data: List of dictionaries, each containing an identifier and a score.
    - score_key: The key used in each dictionary to indicate the score (default is 'total_score').

    Returns:
    - Original list of dictionaries with an additional 'position' key indicating rank based on the score.
    """
    # Sort data by score in descending order without creating a new list
    data.sort(key=lambda x: x[score_key], reverse=True)
    
    # Initialize position tracking
    current_position = 0
    previous_score = None
    # Assign positions in the original list
    for i, item in enumerate(data):
       
        # Check if this item has the same score as the previous one
        if previous_score is not None and item[score_key] == previous_score:
            # If the score is the same, assign the same position
            item['position'] = current_position
            if item[score_key] == 0:
                item['position'] = 'Not Seated'
           
        else:
            # If the score is different, update the position
            current_position = current_position + 1
            item['position'] = current_position
            
        # Update the previous_score to the current item's score
        previous_score = item[score_key]
    return data
    
   
def students_term_score(request):
    if request.method == "POST":  
        # Mapping class codes to display names (for easy readability)
        CLASS_NAME_DISPLAY = {
            'lb': 'Lower Basic',
            'mb': 'Middle Basic',
            'ub': 'Upper Basic',
            'ss': 'Senior Secondary',
        }
        classes = SchoolClass.objects.all()
        records = []  # Initialize records list outside the loop
        academic_session = AcademicSession.objects.get(is_current=True)
        for the_class in classes:
            # Get all students in the current class
            students_in_class = Student.objects.filter(
                student_active=True,  # Only get active students
                studentclass__student_class = the_class,
                studentclass__current_class=True  # Only current class
            )

            # Count the number of students in this class
            student_count = students_in_class.count()

            # Loop through each student in the class
            the_class_record = []
            for student in students_in_class:
                # Try to fetch the admission number based on the class
                admission_no = 'N/A'  # Default value in case we can't find it
                try:
                    admission_record = Admission.objects.get(student=student,session=academic_session, category=the_class.class_name)
                    admission_no = admission_record.admission_no if admission_record else 'N/A'
                except (Admission.DoesNotExist, AttributeError):
                    # If no admission record is found, it stays 'N/A'
                    admission_no = 'N/A'

                # Get the class name in a readable format (e.g., Lower Basic 1A)
                class_name_display = the_class.get_class_name_display()
                # Calculate the total score for the student in the current term
                term = request.POST.get('term')
                session = request.POST.get('session')
                total_score = StudentsGrade.calculate_total_score(
                    student,
                    term,  # Assuming term '1' for now, can be updated as needed
                    academic_session  # Replace with the current year if needed
                )
                the_student_record = {
                    'class_name': f"{class_name_display} {the_class.class_no}{the_class.class_type.upper()}",  # Class name and details
                    'student_count': student_count,  # Number of students in the class
                    'name': student.user.first_name,  # Student's first name
                    'surname': student.user.last_name,  # Student's last name
                    'admission_no': admission_no,  # Admission number
                    'total_score': total_score,  # Student's total score
                
                }
                # Create a record with student information
                the_class_record.append(the_student_record)
            cls = assign_positions(the_class_record, score_key='total_score') 
            records.append(cls)
        # Render the student data to the template
        return render(request, 'school-admin/admin_dashboard/student_score_view.html', {'student_json': records})
    else:
        session = AcademicSession.objects.all()
        context = {
            'sessions':session,
        }
        return render(request, 'school-admin/admin_dashboard/student_score_view_form.html', context)
#student End


# Staff/Teacher
@login_required
def add_new_staff(request):
    if request.method == 'POST':
        user_form = StaffUserForm(request.POST)
        staff_form = NewStaffForm(request.POST, request.FILES)
        
        if user_form.is_valid() and staff_form.is_valid():
            try:
                # Create the User object
                user = User.objects.create_user(
                    first_name=user_form.cleaned_data['first_name'],
                    last_name=user_form.cleaned_data['last_name'],
                    middle_name=user_form.cleaned_data['middle_name'],
                    email=user_form.cleaned_data['email'].lower(),
                    password=user_form.cleaned_data['password'],
                    user_type=2
                )
                
                # Create the Staff object
                staff = Staff.objects.create(
                    staff_user=user,
                    staff_gender=staff_form.cleaned_data['staff_gender'],
                    work_title=staff_form.cleaned_data['work_title'],
                    staff_pic=staff_form.cleaned_data['staff_pic'],
                    staff_contact=staff_form.cleaned_data['staff_contact'],
                    is_teacher=staff_form.cleaned_data['is_teacher'],
                )
                
                messages.success(request, 'Staff Created Successfully')
                
                if staff.is_teacher:
                    return redirect(reverse('addTeacher', kwargs={'id': staff.pk}))
                else:
                    messages.info(request, 'Staff is not a teacher.')
            
            except Exception as e:
                messages.error(request, f'An unexpected error occurred: {str(e)}')
        else:
            errors = user_form.errors.as_text() + staff_form.errors.as_text()
            messages.error(request, f'Form submission failed. Errors: {errors}')
    
    return redirect(reverse('adminHome'))
    
@login_required
def add_teacher(request, id):
    try:
        the_staff = Staff.objects.get(id=id)
    except Staff.DoesNotExist:
        messages.error(request, 'Staff member does not exist.')
        return redirect(reverse('adminHome'))
    
    if request.method == 'POST':
        new_teacher_form = NewTeacherForm(request.POST)
        teacher_subject = request.POST.get('teacher_subject')
        teacher_class_from_request = request.POST.get('teacher_class')
        try:
            teacher_subject = Subjects.objects.get(id=teacher_subject)
        except:
            messages.error(request, 'The Subject Dont Exist')
            return redirect(reverse('addTeacher', kwargs={'id': the_staff.id}))
        
        if new_teacher_form.is_valid():
            # Query existing subjects for the staff
            t_obj = Teachers.objects.filter(teacher=the_staff)
            staff_subjects = t_obj.values_list('teacher_subject', flat=True).distinct()
            staff_classes = t_obj.values_list('teacher_class', flat=True).distinct()
            
            staff_subjects_names = staff_subjects.values('teacher_subject__name')
            teacher_subject_names = [item['teacher_subject__name'] for item in staff_subjects_names]
            
            staff_class_names = staff_classes.values('teacher_class__id')
            teacher_class_from_db = [item['teacher_class__id'] for item in staff_class_names]
            
            
            # Check if the subject is already assigned
            #if str(teacher_subject) in teacher_subject_names and int(teacher_class_from_request) in teacher_class_from_db:
            #   messages.error(request, 'The subject is already assigned to this teacher.')
            #   print('The subject is already assigned to this teacher.')
            if staff_subjects.count() >= 50:
                messages.error(request, 'The teacher already has enough subjects.')
                print('The teacher already has enough subjects.')
            else:
                try:
                    Teachers.objects.create(
                        teacher=the_staff,
                        teacher_class=new_teacher_form.cleaned_data['teacher_class'],
                        teacher_subject=teacher_subject
                    )
                    messages.success(request, 'Teaching assignment added successfully.')
                    return redirect(reverse('addTeacher', kwargs={'id': the_staff.id}))
                except IntegrityError:
                    messages.error(request, 'Failed to assign teaching. Please check the teacher profile.')
                    print('Failed to assign teaching. Please check the teacher profile.')
        else:
            messages.error(request, 'Form submission failed. Please correct the errors below.')
        
        return redirect(reverse('addTeacher', kwargs={'id': the_staff.id}))
    
    else:
        if the_staff.is_teacher:
            form = NewTeacherForm()
            classes = SchoolClass.objects.all()
            subjects = Subjects.objects.all()
            context = {
                'subjects':subjects,
                'classes':classes,
                'the_staff': the_staff,
                'form': form
            }
            return render(request, 'school-admin/admin_dashboard/addteacher.html', context)
        else:
            messages.error(request, 'The staff member is not a teacher.')
            return redirect(reverse('adminHome'))
    
def delete_teacher_obj(request, pk):
    the_teacher_obj = None
    try:
        the_teacher_obj = get_object_or_404(Teachers, id=pk)
        the_teacher_obj.delete()
        messages.success(request, "Record successfully deleted.")
    except Exception as e:
        messages.error(request, f"An error occurred while deleting the staff: {str(e)}")
        return redirect(reverse('adminHome'))
    print(the_teacher_obj.teacher.id)
    return redirect(reverse('adminHome'))
    return redirect(reverse('addTeacher', kwargs={'id': the_teacher_obj.id}))

@login_required
def edit_staff(request, id):
    the_staff = get_object_or_404(Staff, id=id)
    if request.method == 'POST':
        
        staff_user_form = StaffUserEditForm(request.POST, instance=the_staff.staff_user)
        staff_form = EditStaffForm(request.POST, instance=the_staff)
        
        if staff_user_form.is_valid() and staff_form.is_valid():
            staff_user = staff_user_form.save(commit=False)
            password = request.POST.get('password', None)

            # Update password only if it's provided
            if password:
                staff_user.set_password(password, )

            staff_user.save()
            staff_form.save()

            messages.success(request, 'Staff information updated successfully!')
            
        else:
            messages.error(request, 'Editing Staff Fail')
            return redirect(reverse('editStaff',kwargs={'id':id}))
        
        return redirect(reverse('adminHome'))
    else:
        staff_form = EditStaffForm(instance=the_staff)
        staff_user_form = StaffUserEditForm(instance=the_staff.staff_user)
        context = {
            'staff_form': staff_form,
            'staff_user_form':staff_user_form
            }
        return render(request, 'school-admin/admin_dashboard/editteacher.html', context)

@login_required
def delete_staff(request, pk):
    try:
        the_staff = get_object_or_404(Staff, id=pk)
        the_staff.delete()
        messages.success(request, "Staff successfully deleted.")
    except Exception as e:
        messages.error(request, f"An error occurred while deleting the staff: {str(e)}")
    
    return redirect(reverse('adminHome'))

# Staff/Teacher

#Academic Session
def academic_session_management(request):
    if request.method == 'POST':
        form = AcademicSessionForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Academic Session added successfully.')
            return redirect(reverse('academic_session_management'))
        else:
            messages.error(request, 'Academic Session not added.')
            
    form = AcademicSessionForm()
    sessions = AcademicSession.objects.all()
    context = {
        'form': form, 
        'sessions': sessions,
    }
    return render(request, 'school-admin/admin_dashboard/academic_session_management.html',context)

def set_current_session(request, id):
    the_session = get_object_or_404(AcademicSession, id=id)
    if request.method == 'POST':
        try:
            # Get the session object
            session = AcademicSession.objects.get(id=the_session.id)
            
            # Set all sessions as not current
            AcademicSession.objects.update(is_current=False)
            
            # Set the selected session as current
            session.is_current = True
            session.save()
            
            return JsonResponse({'success': True})
        except AcademicSession.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Session not found'}, status=404)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)
# END Academic Session

#Subjects

# ✅ Create and List Subjects
def subject_list_create(request):
    subjects = Subjects.objects.all()

    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            messages.error(request, 'Subject added Sucessfully')
            return redirect('subject_list_create')
    else:
        form = SubjectForm()
        
    return render(request, 'school-admin/subject/subject_list_create.html',{'subjects': subjects})
  
# ✅ Update Subject
def subject_update(request, pk):
    subject = get_object_or_404(Subjects, pk=pk)
    if request.method == 'POST':
        form = SubjectForm(request.POST, instance=subject)
        if form.is_valid():
            form.save()
            return redirect('subject_list_create')
    else:
        form = SubjectForm(instance=subject)
    return render(request, 'subjects/subject_update.html', {'form': form})

# ✅ Delete Subject
def subject_delete(request, pk):
    subject = get_object_or_404(Subjects, pk=pk)
    if request.method == 'POST':
        subject.delete()
        return redirect('subject_list_create')
    return render(request, 'subjects/subject_confirm_delete.html', {'subject': subject})
#End Subjects