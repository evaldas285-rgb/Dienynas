"""Dienyno duomenų modeliai."""
from __future__ import annotations

from django.conf import settings
from django.db import models
from django.utils import timezone


class ClassRoom(models.Model):
    """Mokinių klasės."""

    name = models.CharField("Klasė", max_length=50)
    grade = models.PositiveIntegerField("Klasės numeris")
    letter = models.CharField("Raidė", max_length=2)

    class Meta:
        verbose_name = "Klasė"
        verbose_name_plural = "Klasės"
        unique_together = ("grade", "letter")
        ordering = ["grade", "letter"]

    def __str__(self) -> str:  # pragma: no cover - paprastas atvaizdavimas
        return f"{self.grade}{self.letter} ({self.name})"


class Subject(models.Model):
    """Dalykai su klasifikatoriaus kodu."""

    name = models.CharField("Pavadinimas", max_length=100)
    code = models.CharField("Kodas", max_length=20, unique=True)

    class Meta:
        verbose_name = "Dalykas"
        verbose_name_plural = "Dalykai"
        ordering = ["name"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.name} ({self.code})"


class Teacher(models.Model):
    """Mokytojų profilis."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Naudotojas")
    subjects = models.ManyToManyField(Subject, verbose_name="Dalykai", blank=True)
    classes = models.ManyToManyField(ClassRoom, verbose_name="Klasės", blank=True)

    class Meta:
        verbose_name = "Mokytojas"
        verbose_name_plural = "Mokytojai"
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self) -> str:  # pragma: no cover
        return self.user.get_full_name()


class Student(models.Model):
    """Mokinių profilis."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Naudotojas")
    classroom = models.ForeignKey(ClassRoom, on_delete=models.PROTECT, verbose_name="Klasė", related_name="students")

    class Meta:
        verbose_name = "Mokinys"
        verbose_name_plural = "Mokiniai"
        ordering = ["classroom__grade", "classroom__letter", "user__last_name"]

    def __str__(self) -> str:  # pragma: no cover
        return self.user.get_full_name()


class Parent(models.Model):
    """Tėvų profilis."""

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Naudotojas")
    children = models.ManyToManyField(Student, related_name="parents", verbose_name="Vaikai")

    class Meta:
        verbose_name = "Tėvas / mama"
        verbose_name_plural = "Tėvai"
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self) -> str:  # pragma: no cover
        return self.user.get_full_name()


class Trimester(models.Model):
    """Mokymosi trimestai."""

    name = models.CharField("Pavadinimas", max_length=50)
    order = models.PositiveIntegerField("Eilės numeris", unique=True)
    start_date = models.DateField("Pradžia")
    end_date = models.DateField("Pabaiga")

    class Meta:
        verbose_name = "Trimestras"
        verbose_name_plural = "Trimestrai"
        ordering = ["order"]

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Lesson(models.Model):
    """Pamokų įrašai."""

    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="lessons", verbose_name="Klasė")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="lessons", verbose_name="Dalykas")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="lessons", verbose_name="Mokytojas")
    date = models.DateField("Data", default=timezone.now)
    topic = models.CharField("Tema", max_length=200)

    class Meta:
        verbose_name = "Pamoka"
        verbose_name_plural = "Pamokos"
        ordering = ["-date"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.subject.name} {self.date:%Y-%m-%d}"


class Homework(models.Model):
    """Namų darbai, kuriuos skiria mokytojai."""

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="homeworks", verbose_name="Pamoka")
    description = models.TextField("Užduotis")
    due_date = models.DateField("Atlikti iki", null=True, blank=True)
    created_at = models.DateTimeField("Sukurta", auto_now_add=True)

    class Meta:
        verbose_name = "Namų darbas"
        verbose_name_plural = "Namų darbai"
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.lesson.subject.name} namų darbai"


class ScheduleEntry(models.Model):
    """Tvarkaraščio įrašai."""

    WEEKDAYS = [
        (1, "Pirmadienis"),
        (2, "Antradienis"),
        (3, "Trečiadienis"),
        (4, "Ketvirtadienis"),
        (5, "Penktadienis"),
    ]

    classroom = models.ForeignKey(ClassRoom, on_delete=models.CASCADE, related_name="schedule", verbose_name="Klasė")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="schedule_entries", verbose_name="Dalykas")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="schedule_entries", verbose_name="Mokytojas")
    weekday = models.IntegerField("Savaitės diena", choices=WEEKDAYS)
    start_time = models.TimeField("Pradžia")
    end_time = models.TimeField("Pabaiga")
    location = models.CharField("Kabinetas", max_length=50, blank=True)

    class Meta:
        verbose_name = "Tvarkaraščio įrašas"
        verbose_name_plural = "Tvarkaraštis"
        ordering = ["weekday", "start_time"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.get_weekday_display()} {self.subject.name}"


class Attendance(models.Model):
    """Lankomumo įrašai."""

    STATUS_CHOICES = [
        ("L", "Lankėsi"),
        ("N", "Nelankė"),
        ("P", "Pavėlavo"),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="attendance", verbose_name="Pamoka")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="attendance", verbose_name="Mokinys")
    status = models.CharField("Statusas", max_length=1, choices=STATUS_CHOICES)
    comment = models.CharField("Pastaba", max_length=200, blank=True)

    class Meta:
        verbose_name = "Lankomumas"
        verbose_name_plural = "Lankomumas"
        unique_together = ("lesson", "student")

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.student} - {self.get_status_display()}"


class Grade(models.Model):
    """Pažymių įrašai."""

    TYPE_CHOICES = [
        ("kontrolinis", "Kontrolinis darbas"),
        ("savarankiskas", "Savarankiškas darbas"),
        ("namu_darbai", "Namų darbai"),
        ("iskaita", "Įskaita"),
        ("egzaminas", "Egzaminas"),
        ("dalyvavimas", "Dalyvavimas"),
        ("trimestras", "Trimestro įvertinimas"),
    ]

    VALUE_CHOICES = [(str(i), str(i)) for i in range(1, 11)] + [
        ("N", "Neįvertintas"),
        ("II", "Įskaita išlaikyta"),
        ("NE", "Įskaita neišlaikyta"),
    ]

    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="grades", verbose_name="Pamoka")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="grades", verbose_name="Mokinys")
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="grades", verbose_name="Mokytojas")
    trimester = models.ForeignKey(Trimester, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Trimestras")
    grade_type = models.CharField("Tipas", max_length=20, choices=TYPE_CHOICES)
    value = models.CharField("Įvertinimas", max_length=2, choices=VALUE_CHOICES)
    description = models.CharField("Aprašas", max_length=200, blank=True)
    created_at = models.DateTimeField("Sukurta", auto_now_add=True)

    class Meta:
        verbose_name = "Pažymys"
        verbose_name_plural = "Pažymiai"
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.student} - {self.value}"


class TrimesterResult(models.Model):
    """Trimestro rezultatai pagal dalyką."""

    trimester = models.ForeignKey(Trimester, on_delete=models.CASCADE, related_name="results", verbose_name="Trimestras")
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="trimester_results", verbose_name="Mokinys")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="trimester_results", verbose_name="Dalykas")
    average = models.DecimalField("Vidurkis", max_digits=4, decimal_places=2)
    comment = models.CharField("Komentaras", max_length=200, blank=True)

    class Meta:
        verbose_name = "Trimestro rezultatas"
        verbose_name_plural = "Trimestro rezultatai"
        unique_together = ("trimester", "student", "subject")

    def __str__(self) -> str:  # pragma: no cover
        return f"{self.student} - {self.subject} ({self.trimester})"
