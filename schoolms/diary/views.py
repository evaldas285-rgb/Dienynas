"""Peržiūros dienynui."""
from __future__ import annotations

from typing import Iterable

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import GradeForm, HomeworkForm
from .models import Attendance, Grade, Homework, Lesson, ScheduleEntry, Student, Teacher, TrimesterResult


def _get_user_role(user: User) -> str:
    """Grąžina naudotojo rolę pagal susietus profilius."""

    if hasattr(user, "teacher"):
        return "teacher"
    if hasattr(user, "student"):
        return "student"
    if hasattr(user, "parent"):
        return "parent"
    if user.is_superuser:
        return "admin"
    return "guest"


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    """Pagrindinis skydelis pagal naudotojo rolę."""

    role = _get_user_role(request.user)
    context: dict[str, object] = {"role": role, "user": request.user}

    if role == "teacher":
        teacher = request.user.teacher
        context.update(
            {
                "lessons": teacher.lessons.select_related("classroom", "subject").order_by("-date")[:5],
                "grades": teacher.grades.select_related("student__user", "lesson__subject").order_by("-created_at")[:10],
                "homeworks": Homework.objects.filter(lesson__teacher=teacher).select_related("lesson__subject").order_by("-created_at")[:5],
            }
        )
    elif role == "student":
        student = request.user.student
        context.update(
            {
                "grades": student.grades.select_related("lesson__subject", "teacher__user").order_by("-created_at"),
                "attendance": student.attendance.select_related("lesson__subject").order_by("-lesson__date")[:10],
                "homeworks": Homework.objects.filter(lesson__classroom=student.classroom).select_related("lesson__subject").order_by("-created_at")[:5],
                "schedule": ScheduleEntry.objects.filter(classroom=student.classroom).select_related("subject", "teacher__user").order_by("weekday", "start_time"),
                "results": TrimesterResult.objects.filter(student=student).select_related("trimester", "subject").order_by("trimester__order"),
            }
        )
    elif role == "parent":
        parent = request.user.parent
        children = parent.children.select_related("user", "classroom")
        child_data: list[dict[str, object]] = []
        for child in children:
            child_data.append(
                {
                    "student": child,
                    "grades": child.grades.select_related("lesson__subject", "teacher__user").order_by("-created_at")[:10],
                    "attendance": child.attendance.select_related("lesson__subject").order_by("-lesson__date")[:10],
                    "results": child.trimester_results.select_related("trimester", "subject").order_by("trimester__order"),
                }
            )
        context["children"] = child_data
    else:
        context.update(
            {
                "teachers": Teacher.objects.select_related("user").all(),
                "students": Student.objects.select_related("user", "classroom").all(),
            }
        )

    return render(request, "diary/dashboard.html", context)


@login_required
def grade_list(request: HttpRequest) -> HttpResponse:
    """Pažymių sąrašas pagal rolę."""

    role = _get_user_role(request.user)
    grades: Iterable[Grade]
    if role == "teacher":
        grades = Grade.objects.filter(teacher=request.user.teacher)
    elif role == "student":
        grades = Grade.objects.filter(student=request.user.student)
    elif role == "parent":
        children = request.user.parent.children.all()
        grades = Grade.objects.filter(student__in=children)
    else:
        grades = Grade.objects.all()
    grades = grades.select_related("student__user", "lesson__subject", "teacher__user", "trimester").order_by("-created_at")

    return render(request, "diary/grade_list.html", {"grades": grades, "role": role})


@login_required
def grade_create(request: HttpRequest) -> HttpResponse:
    """Naujo pažymio sukūrimas mokytojui."""

    role = _get_user_role(request.user)
    if role != "teacher":
        messages.error(request, "Jūs neturite teisės pridėti pažymio.")
        return redirect("diary:grade_list")

    teacher = request.user.teacher
    if request.method == "POST":
        form = GradeForm(request.POST)
        if form.is_valid():
            grade: Grade = form.save(commit=False)
            grade.teacher = teacher
            if grade.lesson.teacher != teacher:
                messages.error(request, "Pamoka nepriklauso jums.")
            else:
                grade.save()
                messages.success(request, "Pažymys sėkmingai įrašytas.")
                return redirect("diary:grade_list")
    else:
        form = GradeForm()

    form.fields["lesson"].queryset = Lesson.objects.filter(teacher=teacher).select_related("subject", "classroom")
    form.fields["student"].queryset = Student.objects.filter(classroom__in=teacher.classes.all()).select_related("user")

    return render(request, "diary/grade_form.html", {"form": form, "role": role})


@login_required
def homework_create(request: HttpRequest) -> HttpResponse:
    """Namų darbų kūrimas mokytojo rolėje."""

    role = _get_user_role(request.user)
    if role != "teacher":
        messages.error(request, "Jūs neturite teisės kurti namų darbų.")
        return redirect("diary:dashboard")

    teacher = request.user.teacher
    if request.method == "POST":
        form = HomeworkForm(request.POST)
        if form.is_valid():
            homework: Homework = form.save(commit=False)
            if homework.lesson.teacher != teacher:
                messages.error(request, "Pamoka nepriklauso jums.")
            else:
                homework.save()
                messages.success(request, "Namų darbai sukurti.")
                return redirect("diary:dashboard")
    else:
        form = HomeworkForm()

    form.fields["lesson"].queryset = Lesson.objects.filter(teacher=teacher).select_related("subject", "classroom")

    return render(request, "diary/homework_form.html", {"form": form, "role": role})


@login_required
def attendance_list(request: HttpRequest) -> HttpResponse:
    """Lankomumo sąrašas pagal rolę."""

    role = _get_user_role(request.user)
    if role == "student":
        entries = Attendance.objects.filter(student=request.user.student)
    elif role == "parent":
        entries = Attendance.objects.filter(student__in=request.user.parent.children.all())
    elif role == "teacher":
        entries = Attendance.objects.filter(lesson__teacher=request.user.teacher)
    else:
        entries = Attendance.objects.all()
    entries = entries.select_related("lesson__subject", "student__user").order_by("-lesson__date")

    return render(request, "diary/attendance_list.html", {"entries": entries, "role": role})


@login_required
def schedule_view(request: HttpRequest) -> HttpResponse:
    """Tvarkaraščio peržiūra."""

    role = _get_user_role(request.user)
    if role == "student":
        schedule = ScheduleEntry.objects.filter(classroom=request.user.student.classroom)
    elif role == "teacher":
        schedule = ScheduleEntry.objects.filter(teacher=request.user.teacher)
    elif role == "parent":
        classrooms = {child.classroom for child in request.user.parent.children.all()}
        schedule = ScheduleEntry.objects.filter(classroom__in=classrooms)
    else:
        schedule = ScheduleEntry.objects.all()

    schedule = schedule.select_related("classroom", "subject", "teacher__user").order_by("weekday", "start_time")

    return render(request, "diary/schedule.html", {"entries": schedule, "role": role})
