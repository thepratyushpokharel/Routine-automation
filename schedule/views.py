# schedule/views.py

from django.shortcuts import render, redirect
from .forms import SectionForm, TeacherForm
from .models import Section, Teacher, Schedule
import datetime

def home(request):
    return render(request, 'schedule/home.html')

def add_section(request):
    if request.method == 'POST':
        form = SectionForm(request.POST)
        if form.is_valid():

            form.save()
            return redirect('home')
    else:
        form = SectionForm()
    return render(request, 'schedule/add_section.html', {'form': form})

def add_teacher(request):
    if request.method == 'POST':
        teach = TeacherForm(request.POST)
        if teach.is_valid():
            name =request.POST['name']
            subject = request.POST['subject']
            number_of_classes_per_week = request.POST['number_of_classes_per_week']
            teacher_new = Teacher.objects.create(
                    name = name,
                    subject = subject,
                    number_of_classes_per_week = number_of_classes_per_week
            )
            teacher_new.save()
            return redirect('home')
        
    return render(request, 'schedule/add_teacher.html',{})


from itertools import cycle
import datetime
from collections import defaultdict
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Section, Teacher, Schedule

def time_add(start_time, duration):
    """Add duration (timedelta) to start_time (time) and return new time."""
    return (datetime.datetime.combine(datetime.date.today(), start_time) + duration).time()

def is_teacher_available(teacher_schedule, teacher, day, start_time, end_time):
    """Check if the teacher is available during the given time slot on the specified day."""
    for scheduled_class in teacher_schedule[teacher.id][day]:
        if not (end_time <= scheduled_class['start_time'] or start_time >= scheduled_class['end_time']):
            return False
    return True

def generate_schedule(request):
    print("Starting schedule generation...")

    sections = Section.objects.all()
    teachers = list(Teacher.objects.all())

    # Check for minimum data
    if not sections.exists():
        messages.error(request, "No sections available to generate a schedule.")
        return redirect('home')
    
    if not teachers:
        messages.error(request, "No teachers available to generate a schedule.")
        return redirect('home')

    days_of_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

    teacher_schedule = {teacher.id: {day: [] for day in days_of_week} for teacher in teachers}
    teacher_class_count = {(teacher.id, section.id): 0 for teacher in teachers for section in sections}
    section_times = {}

    # Compute section times
    print("Computing section times...")
    for section in sections:
        section_times[section.id] = []
        current_time = section.class_start_time
        print(f"Section {section.name} start time: {current_time}, end time: {section.class_end_time}")
        while current_time < section.class_end_time:
            print(f"Current time: {current_time}")
            end_time = time_add(current_time, section.time_per_class)
            print(f"Calculated end time: {end_time}")
            if end_time <= section.class_end_time:
                section_times[section.id].append((current_time, end_time))
                print(f"Added class time: {current_time} - {end_time}")
            current_time = time_add(end_time, section.break_time)
            print(f"Next start time after break: {current_time}")
        print(f"Section {section.name} times: {section_times[section.id]}")

    schedule = []

    # Generate schedule
    print("Generating schedule...")
    for section in sections:
        print(f"Scheduling for section: {section.name}")
        for day in days_of_week:
            print(f"Day: {day}")
            class_times = section_times[section.id]
            teacher_cycle = cycle(teachers)
            for start_time, end_time in class_times:
                print(f"Class time: {start_time} - {end_time}")
                teacher = next(teacher_cycle)
                while (not is_teacher_available(teacher_schedule, teacher, day, start_time, end_time) or 
                       teacher_class_count[(teacher.id, section.id)] >= teacher.number_of_classes_per_week):
                    teacher = next(teacher_cycle)
                
                teacher_schedule[teacher.id][day].append({'start_time': start_time, 'end_time': end_time})
                teacher_class_count[(teacher.id, section.id)] += 1
                schedule.append({
                    'teacher': teacher,
                    'section': section,
                    'day_of_week': day,
                    'start_time': start_time,
                    'end_time': end_time,
                })
                print(f"Scheduled {teacher.name} for section {section.name} on {day} from {start_time} to {end_time}")

    # Save the generated schedule to the database
    print("Saving schedule to database...")
    Schedule.objects.all().delete()  # Clear any existing schedules
    for entry in schedule:
        Schedule.objects.create(
            teacher=entry['teacher'],
            section=entry['section'],
            day_of_week=entry['day_of_week'],
            start_time=entry['start_time'],
            end_time=entry['end_time'],
        )
        print(f"Saved {entry['teacher'].name}'s schedule for section {entry['section'].name} on {entry['day_of_week']}")

    print("Schedule generation complete.")
    return render(request, 'schedule/schedule.html', {'schedule': schedule})




# schedule/views.py

import openpyxl
from django.http import HttpResponse

def download_schedule(request):
    schedule = Schedule.objects.all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Schedule"

    ws.append(['Teacher', 'Section', 'Day of Week', 'Start Time', 'End Time'])

    for entry in schedule:
        ws.append([entry.teacher.name, entry.section.name, entry.day_of_week, entry.start_time, entry.end_time])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=schedule.xlsx'
    wb.save(response)
    return response
