# Памятка проекта SynergyEdu

Этот файл нужен, чтобы быстро восстановить контекст в новой сессии.

## Что это за проект
- Тип: учебный портал техникума.
- Backend: Django (`backend_django/`).
- БД: PostgreSQL.
- UI: Django templates + HTMX + Bootstrap 5.

## Ключевые модули
- `accounts`: роли, вход, дашборд, команды `create_roles` и `seed_demo`.
- `education`: группы, дисциплины, записи на курс.
- `schedule`: расписание занятий.
- `assignments`: задания, сдачи, оценки.
- `announcements`: объявления.

## Что уже реализовано
- Русификация моделей и полей для Django Admin.
- Русификация названий приложений через `AppConfig.verbose_name`.
- Статусы заданий/сдач в интерфейсе.
- Модалки Bootstrap + HTMX:
  - сдача задания студентом;
  - выставление оценки преподавателем.
- Валидация сдачи: нельзя сохранить пустые `text` и `link`.
- Production-подготовка:
  - настройки безопасности в `settings.py` для `DEBUG=False`,
  - endpoint `/healthz`,
  - обновлены `README.md` и `.env.example`.

## Важные маршруты
- `/healthz` — проверка сервера.
- Student:
  - `/student/assignments`
  - `/student/submission/modal/<assignment_id>/`
  - `/student/submission/save/<assignment_id>/`
- Teacher:
  - `/teacher/submissions/<assignment_id>`
  - `/teacher/grade/modal/<submission_id>/`
  - `/teacher/grade/save/<submission_id>/`

## Правила работы
- В конце дня по команде `Отбой` обновлять `DAILY_LOG.md`.
- Не менять структуру БД без явного запроса.
- После правок запускать минимум:
  - `python manage.py check`

## Быстрые команды
```powershell
cd backend_django
python manage.py check
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```
