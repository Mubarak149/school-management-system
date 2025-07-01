from typing import Any
from django.core.management.base import BaseCommand
from school_admin.models import SchoolClass, Subjects

class Command(BaseCommand):
    help = 'Create initial data for SchoolClass and Subjects models'

    def handle(self, *args, **kwargs):
        # Create Subject instances
        subjects = [
            'Mathematics', 'English', 'Physics', 'Chemistry', 
            'Biology', 'History', 'Geography', 'Computer Science','Government',
            'English Literature', 'Agricultural Science', 'Hausa Language', 'Islamic Studies',
            'Christian Studies', 'Economics', 'Civic Education', 'Data Processing',
            'National Values', 'Pre-Vocational Studies', 'B/Science&Tech', 'B/Studies',
            'Arabic', 'Literacy', 'Numeracy', 'Pre Science', 'Social Habit', 'Hand Writing', 'Health Habit',
        ]
        
        for subject in subjects:
            Subjects.objects.get_or_create(name=subject)
        
        # Create SchoolClass instances
        school_classes = [
            {'class_name': 'lb', 'class_no': 1, 'class_type': 'a', 'class_category': 'none'},
            {'class_name': 'lb', 'class_no': 1, 'class_type': 'b', 'class_category': 'none'},
            {'class_name': 'lb', 'class_no': 2, 'class_type': 'a', 'class_category': 'none'},
            {'class_name': 'lb', 'class_no': 2, 'class_type': 'b', 'class_category': 'none'},
            {'class_name': 'mb', 'class_no': 1, 'class_type': 'a', 'class_category': 'none'},
            {'class_name': 'mb', 'class_no': 1, 'class_type': 'b', 'class_category': 'none'},
            {'class_name': 'mb', 'class_no': 1, 'class_type': 'c', 'class_category': 'none'},
            {'class_name': 'mb', 'class_no': 2, 'class_type': 'a', 'class_category': 'none'},
            {'class_name': 'mb', 'class_no': 2, 'class_type': 'b', 'class_category': 'none'},
            {'class_name': 'mb', 'class_no': 2, 'class_type': 'c', 'class_category': 'none'},
            {'class_name': 'mb', 'class_no': 3, 'class_type': 'a', 'class_category': 'none'},
            {'class_name': 'mb', 'class_no': 3, 'class_type': 'b', 'class_category': 'none'},
            {'class_name': 'mb', 'class_no': 4, 'class_type': 'a', 'class_category': 'none'},
            {'class_name': 'mb', 'class_no': 4, 'class_type': 'b', 'class_category': 'none'},
            {'class_name': 'mb', 'class_no': 5, 'class_type': 'a', 'class_category': 'none'},
            {'class_name': 'mb', 'class_no': 5, 'class_type': 'b', 'class_category': 'none'},
            {'class_name': 'ub', 'class_no': 7, 'class_type': 'a', 'class_category': 'none'},
            {'class_name': 'ub', 'class_no': 7, 'class_type': 'b', 'class_category': 'none'},
            {'class_name': 'ub', 'class_no': 7, 'class_type': 'c', 'class_category': 'none'},
            {'class_name': 'ub', 'class_no': 8, 'class_type': 'a', 'class_category': 'none'},
            {'class_name': 'ub', 'class_no': 8, 'class_type': 'b', 'class_category': 'none'},
            {'class_name': 'ub', 'class_no': 8, 'class_type': 'c', 'class_category': 'none'},
            {'class_name': 'ub', 'class_no': 9, 'class_type': 'a', 'class_category': 'none'},
            {'class_name': 'ub', 'class_no': 9, 'class_type': 'b', 'class_category': 'none'},
            {'class_name': 'ub', 'class_no': 9, 'class_type': 'c', 'class_category': 'none'},
            {'class_name': 'ss', 'class_no': 1, 'class_type': 'a', 'class_category': 'science'},
            {'class_name': 'ss', 'class_no': 1, 'class_type': 'b', 'class_category': 'art'},
            {'class_name': 'ss', 'class_no': 2, 'class_type': 'a', 'class_category': 'science'},
            {'class_name': 'ss', 'class_no': 2, 'class_type': 'b', 'class_category': 'art'},
            {'class_name': 'ss', 'class_no': 3, 'class_type': 'a', 'class_category': 'science'},
            {'class_name': 'ss', 'class_no': 3, 'class_type': 'b', 'class_category': 'art'},
        ]
        
        for school_class in school_classes:
            SchoolClass.objects.get_or_create(**school_class)
        
        self.stdout.write(self.style.SUCCESS('Subjects and School Classes created successfully!'))
