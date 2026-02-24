from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("education", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Lesson",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "weekday",
                    models.IntegerField(
                        choices=[
                            (0, "Понедельник"),
                            (1, "Вторник"),
                            (2, "Среда"),
                            (3, "Четверг"),
                            (4, "Пятница"),
                            (5, "Суббота"),
                            (6, "Воскресенье"),
                        ]
                    ),
                ),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("room", models.CharField(max_length=120)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="lessons", to="education.course"
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="lessons", to="education.group"
                    ),
                ),
                (
                    "teacher",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, related_name="lessons", to=settings.AUTH_USER_MODEL
                    ),
                ),
            ],
            options={"ordering": ["weekday", "start_time"]},
        ),
    ]
