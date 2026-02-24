from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("education", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Assignment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True)),
                ("due_date", models.DateTimeField()),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="assignments", to="education.course"
                    ),
                ),
            ],
            options={"ordering": ["due_date"]},
        ),
        migrations.CreateModel(
            name="Submission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.TextField(blank=True)),
                ("link", models.URLField(blank=True)),
                ("submitted_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "assignment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to="assignments.assignment",
                    ),
                ),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submissions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={"ordering": ["-submitted_at"]},
        ),
        migrations.CreateModel(
            name="Grade",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("value", models.IntegerField()),
                ("comment", models.TextField(blank=True)),
                ("graded_at", models.DateTimeField(default=django.utils.timezone.now)),
                (
                    "graded_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="grades_given",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "submission",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="grade",
                        to="assignments.submission",
                    ),
                ),
            ],
            options={"ordering": ["-graded_at"]},
        ),
        migrations.AddConstraint(
            model_name="submission",
            constraint=models.UniqueConstraint(fields=("assignment", "student"), name="unique_submission_per_student"),
        ),
    ]
