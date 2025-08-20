from typing import Any
import json
from django.http.response import HttpResponse, JsonResponse
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect,  get_object_or_404
from django.urls import reverse
from django.views.generic import DetailView, View
from main.models import *
from .models import Student, StudentClass, StudentPromotionRecord
from staff.models import Teachers
from .forms import *
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.db.utils import DatabaseError

# Create your views here.


class StudentProfile(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'student/students_dashboard/index.html'
    context_object_name = 'student'
    
    def _get_admission_number(self, student):
        """Helper method to get student admission number based on class ID"""
        try:
            # Retrieve the admission record for the student
            admission_obj = Admission.objects.get(student=student)
            return admission_obj.admission_no
        except Admission.DoesNotExist:
            return 'No Admission No yet'



    def _get_student_subjects_and_teachers(self, myclass):
        """Helper method to get student subjects and teachers"""
        teachers = Teachers.objects.filter(teacher_class=myclass.student_class)
        student_subjects = [teacher.teacher_subject.name for teacher in teachers]
        return student_subjects, teachers

    def _get_student_grades(self, student, myclass):
        """Helper method to collect student grades for all terms"""
        grades = {1: {}, 2: {}, 3: {}}
        for grade in StudentsGrade.objects.filter(student=student, the_class=myclass.student_class):
            grades[int(grade.term)][grade.subject.name] = grade.total_score
        return json.dumps(grades)

    def _calculate_class_positions(self, student, myclass, students_in_class):
        """Helper method to calculate student positions for all terms"""
        positions = {}
        current_year = datetime.datetime.now().year
        current_session =  AcademicSession.objects.get(is_current=True)
        for term in ['1', '2', '3']:
            class_record = []
            for class_student in students_in_class:
                total_score = StudentsGrade.calculate_total_score(
                    class_student, term, current_session
                )
                
                class_record.append({
                    'id': class_student.id,
                    'name': class_student.user.first_name,
                    'surname': class_student.user.last_name,
                    'total_score': total_score,
                    'current_year': current_year
                })
            ranked_records = self.assign_positions(class_record)
            for record in ranked_records:
                if record['id'] == student.id:
                    positions[f'term_{term}_position'] = record['position']
                    break
                    
        positions['student_count'] = students_in_class.count()
        return positions

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.get_object()
        myclass = StudentClass.objects.get(student=student, current_class=True)
        the_class_object = myclass.student_class
        # Get basic class info
        student_subjects, teachers = self._get_student_subjects_and_teachers(myclass)
        # Get students in same class
        students_in_class = Student.objects.filter(
            student_active=True,
            myclasses__student_class=myclass.student_class,
            myclasses__current_class=True
        )

        # Build context
        context.update({
            'courses': student_subjects,
            'teachers': teachers,
            'myclass': myclass.student_class,
            'date_attend': myclass.date_attend_class,
            'admission_no': self._get_admission_number(student),
            'grades_json': self._get_student_grades(student, myclass),
        })
        
        # Add position data
        positions = self._calculate_class_positions(student, myclass, students_in_class)
        context.update({
            'first_term_position': positions.get('term_1_position'),
            'second_term_position': positions.get('term_2_position'),
            'third_term_position': positions.get('term_3_position'),
            'student_count': positions['student_count']
        })
        
        return context

    def assign_positions(self, data, score_key='total_score'):
        """
        Assigns positions based on the highest score in descending order.

        Parameters:
        - data: List of dictionaries, each containing an identifier and a score.
        - score_key: The key used in each dictionary to indicate the score (default is 'total_score').

        Returns:
        - Original list of dictionaries with an additional 'position' key indicating rank based on the score.
        """
        # Sort data by score in descending order without creating a new list
        # data: [{'id': 296, 'name': 'fatima Nura', 'surname': 'Wada', 'total_score': 0, 'current_year': 2025},]
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

def promotion_record_view(request, id):
    try:
        student_id = id
        # Get the student's current class
        student_class = get_object_or_404(StudentClass, student=student_id, current_class=True, student__student_active=True)
        # Retrieve promotion records for the student's current class
        promotion_records = StudentPromotionRecord.objects.filter(promoted_class=student_class.student_class)
        #promotion_records = StudentPromotionRecord.objects.all()
        if not promotion_records.exists():
            return JsonResponse({'error': 'No promotion records found for this class.'}, status=404)
        
        # Manually create a list of dictionaries from the query
        promotion_records_data = []
        for record in promotion_records:
            promotion_records_data.append({
                'pic': record.student.pic.url if record.student.pic else '',
                'student': f'{record.student.user.first_name} {record.student.user.last_name}',
                'promoted_class': f'{record.promoted_class.get_class_name_display()} {record.promoted_class.class_no}{record.promoted_class.get_class_type_display()}',
                'promotion_date': record.promotion_date.strftime('%Y-%m-%d'),
                'promoted_score': record.promoted_score,
                'promotion_year': record.promotion_year,
                'is_promoted': record.is_promoted
            })

    # Pass data to the template as JSON
        context = {
        'promotion_records_json': json.dumps(promotion_records_data),
        'student': student_id,
    }

        return render(request, 'student/students_dashboard/promotion.html', context)

    except StudentClass.DoesNotExist:
        return JsonResponse({'error': 'Student class not found.'}, status=404)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
