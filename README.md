# SynergyEdu - Учебный портал Техникума

Backend проекта находится в `backend_django/` и использует:
- Django
- PostgreSQL
- Django Admin
- HTMX + Bootstrap 5

## Быстрый старт (локально)

1. Подготовить окружение:
```powershell
cd backend_django
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Настроить переменные окружения:
```powershell
copy .env.example .env
```
Заполните в `.env`:
- `DEBUG`
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `CSRF_TRUSTED_ORIGINS` (опционально)

3. Подготовить БД и данные:
```powershell
python manage.py migrate
python manage.py create_roles
python manage.py seed_demo
```

4. Собрать статику:
```powershell
python manage.py collectstatic --noinput
```

5. Запустить локально:
```powershell
python manage.py runserver
```

## Развёртывание в техникуме (production)

1. Установить Python 3.12+ и PostgreSQL.
2. Создать базу данных и пользователя PostgreSQL (с правами на эту БД).
3. Клонировать проект, создать venv, установить зависимости:
```powershell
cd backend_django
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
4. Настроить `.env` для production:
- `DEBUG=False`
- `SECRET_KEY=<сложный секретный ключ>`
- `ALLOWED_HOSTS=<домен,ip через запятую>`
- `DB_*` параметры production БД
- `CSRF_TRUSTED_ORIGINS=https://your-domain` (если доступ по домену/https)

5. Выполнить миграции и роли:
```powershell
python manage.py migrate
python manage.py create_roles
```

6. Заполнить демо-данные при необходимости:
```powershell
python manage.py seed_demo
```

7. Собрать статику:
```powershell
python manage.py collectstatic --noinput
```

8. Запуск:
- Демо-режим:
```powershell
python manage.py runserver 0.0.0.0:8000
```
- Production (gunicorn):
```powershell
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

Подсказка для домена:
- В `ALLOWED_HOSTS` укажите домен(ы) и/или IP через запятую.
- В `CSRF_TRUSTED_ORIGINS` добавьте полный origin с протоколом, например `https://portal.college.local`.

## Healthcheck

- Endpoint: `/healthz`
- Ответ: `ok`

## Демо-аккаунты

- `admin` / `Admin123!`
- `teacher1` / `Teacher123!`
- `student1` / `Student123!`
