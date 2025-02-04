# schedule/models.py

from django.db import models

class Section(models.Model):
    name = models.CharField(max_length=100)
    number_of_classes = models.IntegerField()
    class_start_time = models.TimeField()
    class_end_time = models.TimeField()
    time_per_class = models.DurationField()
    break_time = models.DurationField()

    def __str__(self):
        return self.name

class Teacher(models.Model):
    name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    number_of_classes_per_week = models.IntegerField()

    def __str__(self):
        return self.name

class Schedule(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=20)
    start_time = models.TimeField()
    end_time = models.TimeField()



    class Meta:
        unique_together = ('teacher', 'section', 'day_of_week', 'start_time')

    def __str__(self):
        return f'teacher:{self.teacher}, section:{self.section}, day_of_week:{self.day_of_week}, start_time:{self.start_time}, end-time:{self.end_time}'
