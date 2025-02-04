from django.contrib import admin

# Register your models here.
from .models import Teacher, Schedule, Section
admin.site.register(Teacher)
admin.site.register(Schedule)
admin.site.register(Section)