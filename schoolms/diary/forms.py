"""Formos duomenų įvedimui."""
from __future__ import annotations

from django import forms

from .models import Grade, Homework


class BaseStyledForm(forms.ModelForm):
    """Bendras formų stilius su Bootstrap."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            existing = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = (existing + " form-control").strip()


class GradeForm(BaseStyledForm):
    """Pažymio įvedimo forma."""

    class Meta:
        model = Grade
        fields = [
            "lesson",
            "student",
            "trimester",
            "grade_type",
            "value",
            "description",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }


class HomeworkForm(BaseStyledForm):
    """Namų darbų formos aprašas."""

    class Meta:
        model = Homework
        fields = ["lesson", "description", "due_date"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }
