# SynergyEdu

Основной backend проекта теперь находится в `backend_django/` и использует стек:
- Django
- PostgreSQL
- Django Admin
- HTMX + Bootstrap 5

Старые backend/frontend (если были в репозитории до миграции) можно держать как `legacy/` или в текущем расположении. Основной запуск ниже относится только к `backend_django`.

## Локальный запуск backend_django

1. Создать и активировать виртуальное окружение:
```powershell
cd backend_django
python -m venv .venv
.venv\Scripts\activate
```

2. Установить зависимости:
```powershell
pip install -r requirements.txt
```

3. Настроить `.env`:
- Скопировать `.env.example` в `.env` (если нужно)
- Заполнить параметры PostgreSQL:
  - `DEBUG`
  - `SECRET_KEY`
  - `ALLOWED_HOSTS`
  - `DB_NAME`
  - `DB_USER`
  - `DB_PASSWORD`
  - `DB_HOST`
  - `DB_PORT`

4. Применить миграции:
```powershell
python manage.py migrate
```

5. Создать роли RBAC:
```powershell
python manage.py create_roles
```

6. Заполнить демо-данные:
```powershell
python manage.py seed_demo
```

7. Запустить сервер:
```powershell
python manage.py runserver
```

## Демо-аккаунты

- `admin` / `Admin123!`
- `teacher1` / `Teacher123!`
- `student1` / `Student123!`

## Основные маршруты

- `/login`
- `/` (dashboard по роли)
- Student:
  - `/student/schedule`
  - `/student/assignments`
  - `/student/grades`
  - `/student/announcements`
- Teacher:
  - `/teacher/assignments`
  - `/teacher/submissions/<assignment_id>`
  - `/teacher/grade/<submission_id>` (HTMX POST)
  - `/teacher/announcements`
- Admin:
  - `/admin/`
