from django import forms

from education.models import Course

from .models import Assignment


class SubmissionForm(forms.Form):
    text = forms.CharField(required=False, strip=True)
    link = forms.URLField(required=False)

    def clean(self):
        cleaned_data = super().clean()
        text = (cleaned_data.get("text") or "").strip()
        link = (cleaned_data.get("link") or "").strip()

        if not text and not link:
            raise forms.ValidationError("Заполните текст решения или укажите ссылку.")

        return cleaned_data


class GradeForm(forms.Form):
    value = forms.IntegerField(min_value=0, max_value=100)
    comment = forms.CharField(required=False, strip=True)


class AssignmentTeacherForm(forms.ModelForm):
    due_date = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
    )

    class Meta:
        model = Assignment
        fields = ("title", "description", "due_date", "course")

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.teacher = teacher
        course_qs = Course.objects.none()
        if teacher is not None:
            course_qs = Course.objects.filter(teacher=teacher).select_related("group").order_by("title")
        self.fields["course"].queryset = course_qs
        self.fields["course"].label_from_instance = lambda obj: (
            f"{obj.title} ({obj.group.name})" if obj.group else obj.title
        )

        self.fields["title"].widget.attrs.setdefault("class", "form-control")
        self.fields["description"].widget.attrs.setdefault("class", "form-control")
        self.fields["description"].widget.attrs.setdefault("rows", 4)
        self.fields["due_date"].widget.attrs.setdefault("class", "form-control")
        self.fields["course"].widget.attrs.setdefault("class", "form-select")

        if self.instance and self.instance.pk and self.instance.due_date:
            local_due_date = self.instance.due_date.strftime("%Y-%m-%dT%H:%M")
            self.initial.setdefault("due_date", local_due_date)

    def clean_course(self):
        course = self.cleaned_data["course"]
        if self.teacher and course.teacher_id != self.teacher.id:
            raise forms.ValidationError("Можно выбрать только свой курс.")
        return course
