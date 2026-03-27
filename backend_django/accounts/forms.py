from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import transaction

from education.models import Course, Enrollment, Group
from .models import StudentProfile, TeacherRegistrationRequest

User = get_user_model()


def _split_full_name(full_name: str) -> tuple[str, str]:
    chunks = [part for part in full_name.strip().split() if part]
    if not chunks:
        return "", ""
    if len(chunks) == 1:
        return chunks[0], ""
    return chunks[0], " ".join(chunks[1:])


class BaseRegistrationForm(forms.Form):
    full_name = forms.CharField(label="ФИО", max_length=255)
    username = forms.CharField(label="Логин", max_length=150)
    email = forms.EmailField(label="Email")
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            css = "form-control form-control-lg"
            if isinstance(field.widget, forms.Textarea):
                css = "form-control"
            field.widget.attrs.setdefault("class", css)

    def clean_full_name(self):
        value = self.cleaned_data["full_name"].strip()
        if len(value.split()) < 2:
            raise ValidationError("Укажите ФИО полностью.")
        return value

    def clean_username(self):
        value = self.cleaned_data["username"].strip()
        if User.objects.filter(username__iexact=value).exists():
            raise ValidationError("Пользователь с таким логином уже существует.")
        if TeacherRegistrationRequest.objects.filter(username__iexact=value, status=TeacherRegistrationRequest.STATUS_PENDING).exists():
            raise ValidationError("Заявка с таким логином уже ожидает рассмотрения.")
        return value

    def clean_email(self):
        value = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=value).exists():
            raise ValidationError("Пользователь с таким email уже существует.")
        if TeacherRegistrationRequest.objects.filter(email__iexact=value, status=TeacherRegistrationRequest.STATUS_PENDING).exists():
            raise ValidationError("Заявка с таким email уже ожидает рассмотрения.")
        return value

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            self.add_error("password2", "Пароли не совпадают.")
            return cleaned_data

        if password1:
            try:
                validate_password(password1)
            except ValidationError as exc:
                self.add_error("password1", exc)

        return cleaned_data


class StudentRegistrationForm(BaseRegistrationForm):
    group = forms.ModelChoiceField(label="Группа", queryset=Group.objects.order_by("name"), empty_label="Выберите группу")

    @transaction.atomic
    def save(self):
        full_name = self.cleaned_data["full_name"]
        first_name, last_name = _split_full_name(full_name)
        username = self.cleaned_data["username"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password1"]
        selected_group = self.cleaned_data["group"]

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        StudentProfile.objects.create(user=user, group=selected_group)

        student_courses = Course.objects.filter(group=selected_group).only("id")
        enrollments = [Enrollment(student=user, course=course) for course in student_courses]
        if enrollments:
            Enrollment.objects.bulk_create(enrollments, ignore_conflicts=True)

        return user


class TeacherRegistrationRequestForm(BaseRegistrationForm):
    comment = forms.CharField(
        label="Информация о дисциплине / комментарий",
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Например: Математика, 1 курс"}),
        required=False,
    )

    def save(self):
        return TeacherRegistrationRequest.objects.create(
            full_name=self.cleaned_data["full_name"],
            username=self.cleaned_data["username"],
            email=self.cleaned_data["email"],
            password_hash=make_password(self.cleaned_data["password1"]),
            comment=self.cleaned_data["comment"],
            status=TeacherRegistrationRequest.STATUS_PENDING,
        )
