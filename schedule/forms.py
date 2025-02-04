# schedule/forms.py

from django import forms
from .models import Section, Teacher

class SectionForm(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name', 'number_of_classes', 'class_start_time', 'class_end_time', 'time_per_class', 'break_time']

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'subject', 'number_of_classes_per_week']
