"""Dienyno modelių administravimas."""
from django.contrib import admin

from . import models


@admin.register(models.ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ("grade", "letter", "name")
    ordering = ("grade", "letter")


@admin.register(models.Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("code", "name")
    search_fields = ("name", "code")


@admin.register(models.Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__first_name", "user__last_name")
    filter_horizontal = ("subjects", "classes")


@admin.register(models.Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("user", "classroom")
    list_filter = ("classroom",)
    search_fields = ("user__first_name", "user__last_name")


@admin.register(models.Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ("user",)
    search_fields = ("user__first_name", "user__last_name")
    filter_horizontal = ("children",)


@admin.register(models.Trimester)
class TrimesterAdmin(admin.ModelAdmin):
    list_display = ("order", "name", "start_date", "end_date")
    ordering = ("order",)


@admin.register(models.Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("date", "subject", "classroom", "teacher")
    list_filter = ("classroom", "subject", "teacher")
    search_fields = ("topic",)


@admin.register(models.Homework)
class HomeworkAdmin(admin.ModelAdmin):
    list_display = ("lesson", "due_date", "created_at")
    list_filter = ("lesson__classroom", "lesson__subject")


@admin.register(models.ScheduleEntry)
class ScheduleEntryAdmin(admin.ModelAdmin):
    list_display = ("classroom", "subject", "weekday", "start_time", "end_time")
    list_filter = ("classroom", "weekday")


@admin.register(models.Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("lesson", "student", "status")
    list_filter = ("status", "lesson__classroom")
    search_fields = ("student__user__first_name", "student__user__last_name")


@admin.register(models.Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("student", "lesson", "grade_type", "value", "created_at")
    list_filter = ("grade_type", "value", "lesson__subject")
    search_fields = ("student__user__first_name", "student__user__last_name")


@admin.register(models.TrimesterResult)
class TrimesterResultAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "trimester", "average")
    list_filter = ("trimester", "subject")
    search_fields = ("student__user__first_name", "student__user__last_name")
