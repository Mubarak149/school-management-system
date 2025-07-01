from typing import Any
import json
from django.db import IntegrityError
from django.http import Http404
from django.urls import reverse, reverse_lazy
from django.http import HttpResponse, HttpResponseForbidden
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, UpdateView
from student.models import *
from student.forms import *
from .models import *
from .forms import *
from school_admin.models import SchoolClass, Subjects
from django.forms import BaseModelForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Min, Subquery, OuterRef
# Create your views here.

def student_subjs(the_student):
    myclass = StudentClass.objects.get(student=the_student, current_class=True)
    teachers = Teachers.objects.filter(teacher_class=myclass.student_class)# querying the teachers that are in the same class with the student
    student_subject = []
    for teacher_subject in teachers:
        student_subject.append(str(teacher_subject.teacher_subject.id))
        
    return student_subject

@login_required
def staffhome(request, cls):
    the_user = request.user
 
    try:
        staff = the_user.staff
    except Staff.DoesNotExist:
        if the_user.user_type == '1':
            messages.error(request, "Sorry, only teachers can access this page.")
            return redirect(reverse('adminHome'))
        elif the_user.user_type == '3':
            return redirect(reverse('viewStudent', kwargs={'id': the_user.student.id}))

    # Fetch teacher details and associated data
    teacher_queryset = staff.teachers_set.filter(
    id=Subquery(
        staff.teachers_set.filter(
            teacher_class=OuterRef("teacher_class")).order_by("id").values("id")[:1])).order_by("teacher_class")
    teacher_queryset_all = staff.teachers_set.all()
    teacher_ids = teacher_queryset.values_list('id', flat=True)
    teacher_subject_ids = teacher_queryset_all.values_list('teacher_subject', flat=True).distinct()
    # Fetch the class and related students
    try:
        the_class = SchoolClass.objects.get(id=cls)
        the_student_class = the_class.studentclass_set.filter(current_class=True)
    except SchoolClass.DoesNotExist:
        messages.error(request, "The specified class does not exist.")
        return redirect(reverse('staffHome', kwargs={'cls': cls}))

    class_ids = SchoolClass.objects.filter(teachers__id__in=teacher_ids).values_list('id', flat=True)
    if (the_user.user_type == '2') and (cls in class_ids):
        if request.method == 'POST':
            subject = request.POST.get('subject')
            if int(subject) in teacher_subject_ids:
                print(int(subject) in teacher_subject_ids,int(subject) ,teacher_subject_ids)
                total_score = request.POST.getlist('total_score')
                students = request.POST.getlist('student')
                term = request.POST.get('term')
                academic_session = AcademicSession.objects.get(is_current=True)
                for student_pos in range(len(students)):
                    student_id = students[student_pos]
                    if subject in student_subjs(student_id):  # Assuming `student_subjs` is a valid function
                        existing_grade = StudentsGrade.objects.filter(
                            student_id=student_id,
                            subject_id=subject,
                            the_class=the_class,
                            term=term,
                            grade_session=academic_session
                        ).exists()

                        if existing_grade:
                            messages.error(request, f"Result for student-id({student_id}) has already been uploaded.")
                            continue  # Skip this student to avoid IntegrityError

                        st = {
                            'student': student_id,
                            'subject': subject,
                            'the_class': the_class,
                            'total_score': total_score[student_pos],
                            'term': term,
                            'grade_session':academic_session,
                        }
                        the_student_score_form = StudentGradeForm(st)
                        if the_student_score_form.is_valid():
                            
                            try:
                                the_student_score_form.save()
                                messages.success(request, "Result uploaded successfully.")
                            except IntegrityError:
                                messages.error(request, f"You have already uploaded student-id({st['student']}) result.")
                                print(st,the_student_score_form.errors.as_text())
                                continue
                        else:
                            messages.error(request, f"Form errors: {the_student_score_form.errors.as_text()}")
                            return redirect(reverse('staffHome', kwargs={'cls': cls}))
                    else:
                        messages.error(request, "This student is not enrolled in the subject.")
                        return redirect(reverse('staffHome', kwargs={'cls': cls}))

                return redirect(reverse('staffHome', kwargs={'cls': cls}))

            else:
                messages.error(request, "This is not your subject.")
                print(int(subject) in teacher_subject_ids,int(subject) ,teacher_subject_ids)
                return redirect(reverse('staffHome', kwargs={'cls': cls}))

        else:
            teacher_objs = the_user.staff.teachers_set.all().distinct()
            subjects = list({subj.teacher_subject for subj in teacher_objs})
            gradeform = StudentGradeForm()
            
            context = {
                'subjects': subjects,
                'the_teacher_objs': teacher_queryset,
                'the_class': the_class,
                'the_student_class': the_student_class,
                'form': gradeform,
            }
            return render(request, 'staff/teacher_dashboard/index.html', context)
    
    else:
        if the_user.user_type == '1':
            messages.error(request, "Sorry, only teachers can access this page.")
            return redirect(reverse('adminHome'))
        elif the_user.user_type == '3':
            return redirect(reverse('viewStudent', kwargs={'id': the_user.student.id}))
        else:
            messages.error(request, "You are not allowed to view this class.")
            return redirect(reverse('staffHome', kwargs={'cls': class_ids[0] if class_ids else 'default'}))

class StudentGradesView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = "staff/teacher_dashboard/studentgrades.html"
    context_object_name = 'student'
    
    def get_context_data(self, **kwargs: Any):
        # Query the teacher subject start
        
        the_user = self.request.user
        the_staff_obj = None
        the_teacher_obj = None
        the_teacher_subjects = []
        if the_user.user_type == '2':  # Ensure it's a staff member
            the_staff_obj = the_user.staff
            if the_staff_obj.is_teacher:  # Ensure the staff member is a teacher
                the_teacher_obj = Teachers.objects.filter(teacher=the_staff_obj)  # Query the teacher object
                the_teacher_subjects = list(the_teacher_obj.values_list('teacher_subject', flat=True).distinct())
        
        context = super().get_context_data(**kwargs)
        
        # Get the student's current class
        current_class = self.get_object().studentclass_set.get(current_class=True).student_class
        context['myclass'] = current_class
         # Get the current year
        current_session = AcademicSession.objects.get(is_current=True)
        # Filter grades to only include those from the current class
        grades = [
            {
                'avatar': grade.student.pic.url,
                'subject': grade.subject.name,
                'subject_id': int(grade.subject.id),
                'Date': f"{grade.record_date.day}/{grade.record_date.month}/{grade.record_date.year}",
                'term': grade.get_term_display(),
                'year': grade.year,
                'class': f"{grade.the_class.get_class_name_display()} {grade.the_class.class_no}{grade.the_class.get_class_type_display()}",
                'id': grade.id,
                'score': grade.total_score,
            }
            for grade in self.get_object().studentsgrade_set.filter(the_class=current_class, grade_session=current_session)
        ]
        
        # Pass the teacher's subjects and grades to the context
        context['teacher_subjects'] = json.dumps([{'teacher_subjects': the_teacher_subjects}])
        context['grades'] = json.dumps(grades)
        
        return context
    

class UpdateGradeScoreView(LoginRequiredMixin, UpdateView):
    model = StudentsGrade
    template_name = "staff/teacher_dashboard/updatestudentsgrade.html"
    form_class = StudentGradeEditForm
    context_object_name = 'studentgrade'
    
    def get_success_url(self) -> str:
        success_url = reverse_lazy('studentGrades' , kwargs={"pk":self.get_object().student.id})
        #return super().get_success_url()
        return success_url
    
    def dispatch(self, request, *args, **kwargs):
        # Check if the user has permission to access this view
        if request.user.user_type != '2':
            # If not, return a 403 Forbidden response or redirect to another page
            return HttpResponseForbidden("You do not have permission to access this page.")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form = super().form_valid(form)
        return form
    
    def form_invalid(self, form: BaseModelForm) -> HttpResponse:
        print(form.errors.as_text())
        return super().form_invalid(form)

 
class StaffProfile(LoginRequiredMixin, DetailView):
    model = Staff
    template_name = 'staff/teacher_dashboard/myProfile.html'
    context_object_name = 'staff'
    
    def get_object(self, queryset=None):
        pk = self.kwargs.get('pk')
        the_staff = None
        try:
            the_staff = self.model.objects.get(pk=pk)
            # Check if the logged-in user is associated with this staff
            if self.request.user != the_staff.staff_user and self.request.user.user_type != '1':
                raise Http404("You are not authorized to access this profile.")
        except Staff.DoesNotExist:
            messages.error(self.request, "Staff member not found.")
            raise Http404("Staff member not found.")
        
        return the_staff
        
    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        the_staff = self.get_object()
        
        try:
            subjects = list(Teachers.objects.filter(teacher=the_staff).values('teacher_subject').distinct())
            subjects = [Subjects.objects.get(id=n['teacher_subject']) for n in subjects]
        except Subjects.DoesNotExist:
            subjects = []  # Handle cases where subjects might not exist

        context['subjects'] = subjects
        return context


@login_required
def staff_setting(request, id):
    # Get the currently logged-in user
    the_user = request.user
    # Retrieve the associated staff object
    staff = get_object_or_404(Staff, id=id)
    # Query the Teacher objects associated with this staff
    teacher_queryset = staff.teachers_set.all().order_by('teacher_class')
    # Retrieve the IDs of these Teacher objects
    teacher_ids = teacher_queryset.values_list('id', flat=True)
    # Query the SchoolClass objects associated with the retrieved Teacher IDs
    class_ids = SchoolClass.objects.filter(teachers__id__in=teacher_ids).values_list('id', flat=True)
        # Check if the logged-in user is the same as the staff user
    if request.user != staff.staff_user:
        messages.error(request, "You are not authorized to access this page.")
        return redirect(reverse('staffHome' ,kwargs={'cls':class_ids[0]}))

    if request.method == 'POST':
        edit_staff_form = EditStaffForm(request.POST, instance=staff)
        staff_user_form = StaffUserEditForm(request.POST, instance=staff.staff_user)
        if edit_staff_form.is_valid() and staff_user_form.is_valid():
            staff_user_form.save()
            edit_staff_form.save()
            messages.success(request, 'Update Profile Successfully')
            
        else:
            messages.error(request, f'{edit_staff_form.errors.as_text()}')
            return redirect(reverse('staffSetting',kwargs={'id':id}))
        
        return redirect(reverse('staffHome' ,kwargs={'cls':class_ids[0]}))
    else:
        staff_form = EditStaffForm(instance=staff)
        staff_user_form = StaffUserEditForm(instance=staff.staff_user)
        context = {
            'staff_form': staff_form,
            'staff_user_form':staff_user_form
            }
        return render(request, 'staff/teacher_dashboard/setting.html', context)


def calculate_promotion_eligibility(grade_data, passing_score, min_terms):
    """
    Calculates the total scores per term, session score, and checks if the student is eligible for promotion.

    Args:
        grade_data (dict): Dictionary containing term-wise scores.
        passing_score (int): The minimum average score required for promotion.
        min_terms (int): Minimum number of terms with scores required for promotion.

    Returns:
        dict: Dictionary with total scores per term, session score, and promotion eligibility.
    """
    
    term_scores = {}  # Store total score per term
    total_session_score = 0
    non_empty_terms = 0  # Count terms with scores

    for term, subjects in grade_data.items():
        total_term_score = sum(subject['score'] for subject in subjects)  # Sum scores per term
        term_scores[term] = total_term_score
        total_session_score += total_term_score
        
        if total_term_score > 0:
            non_empty_terms += 1

    # Add session total score
    term_scores['Total_Session_Score'] = total_session_score

    # Calculate the average score per term (if terms are available)
    if non_empty_terms > 0:
        average_score = total_session_score / non_empty_terms
    else:
        average_score = 0

    # Check if the student meets promotion criteria
    is_eligible = (average_score >= passing_score) and (non_empty_terms >= min_terms)

    # Add eligibility status to the dictionary
    term_scores['Promotion_Eligible'] = is_eligible
    term_scores['Average_Score'] = round(average_score, 2)

    return term_scores

def get_students_in_current_class(the_class):
    from student.models import Student, StudentClass

    # Get only students whose `current_class` is True
    students = Student.objects.filter(studentclass__student_class=the_class, studentclass__current_class=True)

    return students

@login_required
def promotion_view(request, cls):
    try:
        staff = request.user.staff  # Access the staff related to the logged-in user
        the_class = SchoolClass.objects.get(id=cls)
        the_students_in_class = get_students_in_current_class(the_class)
        students_eligible_for_promotion_record = []
        students_not_eligible_for_promotion_record = []
        for the_student in the_students_in_class:
            # Fetch the student's grades for the current session
            grade_session = AcademicSession.current_session_grades(the_student)
             # Calculate total and average scores, and determine promotion eligibility
            result = calculate_promotion_eligibility(grade_session, passing_score=450, min_terms=3)
            if result['Promotion_Eligible']:
                result['student'] = the_student
                result['name'] = the_student.user.first_name +" "+ the_student.user.last_name
                students_eligible_for_promotion_record.append(result)
            else:
                result['student'] = the_student
                result['name'] = the_student.user.first_name +" "+ the_student.user.last_name
                students_not_eligible_for_promotion_record.append(result)
                
    except ObjectDoesNotExist:
        messages.error(request, "You are not registered as a staff member.")
        return render(request, 'staff/teacher_dashboard/promote_student.html')
    
    except SchoolClass.DoesNotExist:
        messages.error(request, "The specified class does not exist.")
        return redirect(reverse('staffHome', kwargs={'cls': cls}))
    
    try:
        my_promoters_role = Promoter.objects.get(school_class=the_class)
        # If a Promoter exists, check if the current staff is the promoter
        if my_promoters_role.promoter != staff:
            messages.error(request, "You are not the assigned promoter for this class.")
            return render(request, 'staff/teacher_dashboard/promote_student.html')
    except Promoter.DoesNotExist:
        # If no Promoter exists, create one for the current staff
        my_promoters_role = Promoter.objects.create(promoter=staff, school_class=the_class)

    next_classes = SchoolClass.objects.exclude(id=the_class.id)
    context = {
        'all_students': students_eligible_for_promotion_record + students_not_eligible_for_promotion_record,
        'next_classes': next_classes,
        'current_class': the_class,
    }
    if request.method == "POST":
        class_id = request.POST.get('next_class')
        the_class = SchoolClass.objects.get(id=class_id)
        academic_session = AcademicSession.objects.get(is_current=True)
        print(students_not_eligible_for_promotion_record)
        if students_eligible_for_promotion_record:
            for record in students_eligible_for_promotion_record:
                StudentClass.objects.assign_class(student=record['student'], school_class=the_class, session=academic_session)
                StudentPromotionRecord.objects.create(
                    student=record['student'],
                    promoted_class=the_class,
                    promotion_session=academic_session,
                    promotion_date=timezone.now(),
                    promoted_score=record['Total_Session_Score'],
                    promotion_year=datetime.date.today().year,
                    is_promoted=True
                )
                
            context = {
                        'all_students':students_not_eligible_for_promotion_record,
                        'next_classes': next_classes,
                        'current_class': the_class,
                    }
        else:
            messages.error(request, "Students Are not Eligible For Promotion")  
            
    return render(request, 'staff/teacher_dashboard/promote_student.html', context)
