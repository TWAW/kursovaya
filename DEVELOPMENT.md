# 🚀 IT Audit Automation — Руководство разработчика

**Последнее обновление:** 2 февраля 2026  
**Версия:** 2.0 (Production-ready)

---

## 📋 Содержание

1. [Структура проекта](#структура-проекта)
2. [Быстрый старт](#быстрый-старт)
3. [Архитектура](#архитектура)
4. [Работа с БД](#работа-с-бд)
5. [Разработка новых функций](#разработка-новых-функций)
6. [Важные соглашения](#важные-соглашения)
7. [Troubleshooting](#troubleshooting)

---

## 📁 Структура проекта

```
project12/
│
├── app/                          # Основной пакет приложения
│   ├── main.py                   # Точка входа Python, get_wsgi_app()
│   ├── __init__.py               # create_app() — фабрика приложения
│   ├── config.py                 # Конфигурация (dev/prod/test)
│   │
│   ├── api/                      # HTTP-слой (маршруты/зависимости/DTO)
│   │   ├── routes.py             # Регистрация blueprints
│   │   ├── deps.py               # get_db_session() и др. зависимости
│   │   └── schemas.py            # DTO для границы API (DeviceCreateDTO и т.п.)
│   │
│   ├── services/                 # Бизнес-логика (независима от Flask)
│   │   ├── __init__.py
│   │   ├── devices_service.py    # CRUD по оборудованию
│   │   └── auth_service.py       # Логика входа, 2FA, смены пароля
│   │
│   ├── db/                       # Слой данных
│   │   └── session.py            # Base, Database, init_engine()
│   │
│   ├── models/                   # Доменная модель (SQLAlchemy)
│   │   └── __init__.py           # User, Employee, Device, Audit, Issue, AuditLog
│   │
│   ├── core/                     # Общие доменные примитивы
│   │   └── exceptions.py         # DomainError, ValidationError, NotFoundError, ...
│   │
│   ├── routes/                   # Flask blueprints (HTTP-обработчики)
│   │   ├── auth.py               # /login, /logout, 2FA (薄 HTTP-слой)
│   │   ├── main.py               # /, главная страница
│   │   ├── devices.py            # /devices, управление оборудованием
│   │   ├── audits.py             # /audits, управление аудитами
│   │   └── reports.py            # /report, отчеты
│   │
│   ├── forms/                    # WTForms формы
│   │   ├── auth_forms.py         # LoginForm
│   │   └── device_forms.py       # DeviceForm, DeviceEditForm
│   │
│   ├── utils/                    # Вспомогательные функции (ограниченно)
│   │   └── helpers.py
│   │
│   ├── templates/                # Jinja2 шаблоны
│   └── static/                   # Статические файлы
│
├── migrations/                   # Alembic миграции БД
│   ├── env.py                    # Окружение для миграций (использует app.db.session.Base)
│   └── versions/                 # Версии миграций
│
├── tests/                        # Pytest-тесты
├── wsgi.py                       # WSGI entry point (wsgi:app для gunicorn)
├── Dockerfile                    # Продакшен-образ приложения
├── docker-compose.yml            # Локальная разработка (app + PostgreSQL)
├── requirements.txt              # Python зависимости
├── alembic.ini                   # Конфигурация Alembic
├── README.md                     # Описание проекта
└── DEVELOPMENT.md                # Этот файл
```

---

## ⚡ Быстрый старт

### 1️⃣ Подготовка окружения

```bash
# Клонируй репо
cd project12

# Активируй venv (если используется)
.venv\Scripts\Activate.ps1  # Windows PowerShell

# Установи зависимости
pip install -r requirements.txt

# Проверь что все установилось
python -c "import flask, sqlalchemy, psycopg; print('OK')"
```

### 2️⃣ Настройка БД

```bash
# Убедись что PostgreSQL запущен
# Windows: Services → postgresql-x64-18 должен быть Running

# Проверь подключение
$env:PGPASSWORD='it_audit_pass123'
& "C:\Program Files\PostgreSQL\18\bin\psql" -U it_audit_user -h localhost -d it_audit_dev -c "SELECT version();"
```

### 3️⃣ Запуск приложения (локально, без Docker)

```bash
# Development сервер (с hot-reload)
python -m app.main

# или старый способ (остаётся совместимым):
python wsgi.py

# Откроется на http://127.0.0.1:5000 (PORT можно переопределить)
# Вход по умолчанию:
#   admin / Admin@123  (или значение ADMIN_PASSWORD из env)
```

### 4️⃣ Проверка миграций

```bash
# Посмотреть историю миграций
python -m alembic current

# Все миграции должны быть applied
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# current revision: 1111ab9aa0a7 (или новее)
```

---

## 🏗️ Архитектура

### **Уровни приложения:**

```
┌───────────────────────────────────────────────────────────────┐
│          PRESENTATION LAYER (Jinja2)                          │
│   templates/ (HTML шаблоны с Bootstrap 5)                     │
└───────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────┐
│          HTTP / API LAYER (Flask)                             │
│   app/api/routes.py  — регистрация blueprints                 │
│   app/routes/*.py    — HTTP-обработчики без SQL/бизнес-логики │
│   app/api/deps.py    — явные зависимости (get_db_session)     │
└───────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────┐
│          SERVICE LAYER (business logic)                       │
│   app/services/*.py — чистые сервисы, принимающие Session     │
│   работают с моделями и доменными исключениями                │
└───────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────┐
│          DATA LAYER (SQLAlchemy ORM)                          │
│   app/db/session.py  — Base, Database, init_engine            │
│   app/models/__init__.py — ORM-модели                         │
└───────────────────────────────────────────────────────────────┘
                              ↓
┌───────────────────────────────────────────────────────────────┐
│          DATABASE (PostgreSQL)                                │
│   Таблицы: users, devices, audits, employees, issues, ...     │
└───────────────────────────────────────────────────────────────┘
```

### **Поток запроса:**

```
1. Пользователь открывает http://127.0.0.1:5000/devices
   ↓
2. Flask маршрут @devices_bp.route('/') вызывает list_devices()
   ↓
3. list_devices() запрашивает Device.query() через ORM
   ↓
4. SQLAlchemy генерирует SQL → SELECT * FROM devices
   ↓
5. PostgreSQL возвращает результаты
   ↓
6. list_devices() передает данные в render_template('devices.html')
   ↓
7. Jinja2 рендерит HTML с данными
   ↓
8. HTML отправляется в браузер
```

---

## 🗄️ Работа с БД

### **Подключение к PostgreSQL**

**Способ 1: psql (командная строка)**
```powershell
$env:PGPASSWORD='it_audit_pass123'
& "C:\Program Files\PostgreSQL\18\bin\psql" -U it_audit_user -h localhost -d it_audit_dev

# Команды:
\dt                     # Список таблиц
SELECT * FROM users;    # Просмотр пользователей
\q                      # Выход
```

**Способ 2: DBeaver (GUI)**
- Скачай: https://dbeaver.io/download/
- New Database Connection → PostgreSQL
- Server: localhost, Port: 5432
- Database: it_audit_dev, User: it_audit_user, Password: it_audit_pass123

**Способ 3: Python (в приложении)**
```python
from app import create_app
app = create_app('development')

with app.app_context():
    db = app.db
    session = db.session()
    
    from app.models import Device
    devices = session.query(Device).all()
    for d in devices:
        print(f"ID={d.id}, Name={d.name}")
    
    session.close()
```

### **Модели и связи**

```python
# Модели находятся в app/models/__init__.py

User            # Пользователь (login, password)
├─ id: int (primary key)
├─ username: str (unique)
├─ password_hash: str (bcrypt)
├─ email: str
└─ is_admin: bool

Employee        # Сотрудник
├─ id: int
├─ name: str
├─ position: str
└─ devices: List[Device]  # Обратная связь

Device          # Оборудование
├─ id: int
├─ name: str
├─ type: str (компьютер, сервер, принтер, сетевое устройство)
├─ serial_number: str (unique)
├─ location: str
├─ employee_id: int (foreign key)
├─ employee: Employee  # Связь
└─ audits: List[Audit]  # Обратная связь

Audit           # Запись аудита
├─ id: int
├─ device_id: int (foreign key)
├─ date: date
├─ status: str (исправен, неисправен, требует внимания)
├─ comment: text
└─ device: Device  # Связь
```

### **Миграции (Alembic)**

```bash
# 1. После изменения моделей в app/models/__init__.py
# Измени модель, например добавь поле:
# class Device(Base):
#     new_field = Column(String(100))

# 2. Создай миграцию
python -m alembic revision --autogenerate -m "Add new_field to Device"

# 3. Проверь файл миграции в migrations/versions/
# Убедись что изменения правильные

# 4. Применить миграцию
python -m alembic upgrade head

# Откат миграции (если что-то не так)
python -m alembic downgrade -1
```

### **Очистка БД (для разработки)**

```bash
# ВНИМАНИЕ! Это удалит ВСЕ данные!

# Способ 1: Пересоздать БД
$env:PGPASSWORD='1234'
& "C:\Program Files\PostgreSQL\18\bin\psql" -U postgres -h localhost -c "DROP DATABASE it_audit_dev; CREATE DATABASE it_audit_dev OWNER it_audit_user;"

# Способ 2: Перезапустить миграции
python -m alembic downgrade base  # Откатить все
python -m alembic upgrade head    # Применить заново

# Потом перезапусти приложение
python wsgi.py
```

---

## 🛠️ Разработка новых функций

### **Пример: Добавить новое поле в Device**

```python
# 1. Измени модель (app/models/__init__.py)
class Device(Base):
    __tablename__ = 'devices'
    
    # ... существующие поля ...
    warranty_until = Column(Date)  # ← Новое поле

# 2. Создай миграцию
python -m alembic revision --autogenerate -m "Add warranty_until to Device"

# 3. Применить
python -m alembic upgrade head

# 4. Обнови форму (app/routes/devices.py)
warranty = request.form.get('warranty_until')
device = Device(..., warranty_until=warranty)

# 5. Обнови шаблон (app/templates/devices.html)
<input type="date" name="warranty_until" class="form-control">

# 6. Протестируй
```

### **Пример: Добавить новый маршрут (по слоям)**

1. **Сервисный слой** — `app/services/devices_service.py`:

```python
def get_device_statistics(session: Session) -> dict[str, Any]:
    total = session.query(Device).count()
    by_type = (
        session.query(Device.type, func.count())
        .group_by(Device.type)
        .all()
    )
    return {"total": total, "by_type": by_type}
```

2. **HTTP-слой** — `app/routes/devices.py`:

```python
@devices_bp.route('/statistics', methods=['GET'])
@login_required_decorator
def device_statistics():
    session = get_db_session()
    try:
        stats = get_device_statistics(session)
        return render_template(
            'device_stats.html',
            total=stats["total"],
            by_type=stats["by_type"],
        )
    except ServiceError as e:
        flash(str(e), 'error')
        return redirect(url_for('devices.list_devices'))
```

### **Пример: Добавить новую форму**

```python
# app/forms/device_forms.py (создай если нет)

from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

class DeviceForm(FlaskForm):
    """Форма для добавления устройства"""
    name = StringField('Название', validators=[DataRequired()])
    device_type = SelectField('Тип', choices=[
        ('компьютер', 'Компьютер'),
        ('сервер', 'Сервер'),
        ('принтер', 'Принтер'),
        ('сетевое устройство', 'Сетевое устройство')
    ])
    serial_number = StringField('Серийный номер', validators=[DataRequired()])
    location = StringField('Место установки', validators=[DataRequired()])
    submit = SubmitField('Добавить')
```

---

## 📝 Важные соглашения

### **1️⃣ Код должен быть production-ready**

```python
# ❌ Плохо
result = db_session.query(Device).all()
print(f"Found {len(result)} devices")
return render_template(...)

# ✅ Хорошо
try:
    devices = db_session.query(Device).all()
    logger.info(f"Loaded {len(devices)} devices")
    return render_template('devices.html', devices=devices)
except Exception as e:
    logger.error(f"Failed to load devices: {str(e)}")
    flash('Ошибка при загрузке оборудования', 'error')
    return render_template('error.html')
finally:
    db_session.close()
```

### **2️⃣ Всегда закрывай сессию БД**

```python
db_session = db.session()
try:
    # твой код
    device = db_session.query(Device).get(id)
finally:
    db_session.close()  # ← ОБЯЗАТЕЛЬНО!
```

### **3️⃣ Используй валидацию всегда**

```python
# ❌ Плохо
name = request.form.get('name')
device = Device(name=name)

# ✅ Хорошо
if not name or len(name) < 3:
    flash('Название должно быть от 3 символов', 'error')
    return redirect(url_for('devices.list_devices'))
device = Device(name=name.strip())
```

### **4️⃣ CSRF защита обязательна**

```html
<!-- ❌ Плохо -->
<form method="POST" action="/devices/add">
    <input type="text" name="name">
</form>

<!-- ✅ Хорошо -->
<form method="POST" action="/devices/add">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
    <input type="text" name="name">
</form>
```

### **5️⃣ Имена переменных и функций**

```python
# ❌ Плохо
def addDev():  # camelCase
    d = request.form.get('name')
    db.add(d)

# ✅ Хорошо
def add_device():  # snake_case
    name = request.form.get('name')
    device = Device(name=name)
    db.session.add(device)
```

---

## 🔧 Конфигурация

### **Environment переменные**

```bash
# Development (по умолчанию)
# Нет переменных, используются defaults из config.py

# Production
export FLASK_ENV=production
export SECRET_KEY="your-super-secret-key-here"
export DATABASE_URL="postgresql+psycopg://user:pass@prod-db:5432/it_audit"
```

### **Изменение конфигурации**

Все параметры в `app/config.py`:

```python
class DevelopmentConfig(Config):
    DEBUG = True  # ← включить отладку
    SQLALCHEMY_ECHO = True  # ← показывать SQL запросы

class ProductionConfig(Config):
    DEBUG = False  # ← выключить отладку на production!
    SESSION_COOKIE_SECURE = True  # ← только HTTPS
```

---

## 🐛 Troubleshooting

### **Ошибка: CSRF token is missing**

```
jinja2.exceptions.UndefinedError: 'form' is undefined
```

**Решение:** Проверь что form передается в render_template:
```python
form = LoginForm()
return render_template('login.html', form=form)
```

И в шаблоне используй:
```html
<input type="hidden" name="csrf_token" value="{{ csrf_token() }}"/>
```

### **Ошибка: ModuleNotFoundError: No module named 'app'**

**Решение:** Убедись что запускаешь из корня проекта:
```bash
cd project12
python wsgi.py
```

### **Ошибка: connection refused (PostgreSQL)**

```
psycopg.OperationalError: connection refused
```

**Решение:** 
1. Проверь что PostgreSQL запущен:
   ```bash
   Get-Service postgresql-x64-18  # должен быть Running
   ```

2. Проверь connection string в config.py (host, port, database, username, password)

3. Проверь пароль:
   ```bash
   $env:PGPASSWORD='it_audit_pass123'
   & "C:\Program Files\PostgreSQL\18\bin\psql" -U it_audit_user -h localhost -d it_audit_dev -c "SELECT 1;"
   ```

### **Ошибка: UNIQUE constraint failed (duplicate serial_number)**

**Решение:** Серийный номер уже существует в БД. Используй другой или удали старую запись:
```bash
$env:PGPASSWORD='it_audit_pass123'
& "C:\Program Files\PostgreSQL\18\bin\psql" -U it_audit_user -h localhost -d it_audit_dev -c "DELETE FROM devices WHERE serial_number='ABC123';"
```

### **Приложение не обновляется (кэш)**

**Решение:** Очисти кэш браузера или используй Ctrl+Shift+Delete

### **Миграция не применяется**

```bash
# Проверь статус
python -m alembic current

# Посмотри ошибку
python -m alembic upgrade head -v

# Откатись и попробуй еще раз
python -m alembic downgrade -1
```

---

## 📚 Полезные команды

```bash
# Запуск приложения
python wsgi.py

# Создание миграции
python -m alembic revision --autogenerate -m "Description"

# Применение миграций
python -m alembic upgrade head

# Откат миграции
python -m alembic downgrade -1

# Просмотр миграций
python -m alembic history

# Проверка Python окружения
python -c "import flask, sqlalchemy, psycopg; print('OK')"

# Обновление зависимостей
pip install -r requirements.txt --upgrade

# Проверка версий
pip freeze
```

---

## 🔐 Безопасность

### **Что уже реализовано:**
- ✅ bcrypt для хеширования паролей (12 rounds)
- ✅ CSRF защита (Flask-WTF)
- ✅ Session-only cookies (не сохраняются в localStorage)
- ✅ SQL injection protection (SQLAlchemy параметризованные запросы)
- ✅ XSS protection (Jinja2 autoescape)

### **Что добавить на production:**
- ⚠️ HTTPS (SSL сертификат)
- ⚠️ Rate limiting (защита от brute-force)
- ⚠️ Logging всех действий
- ⚠️ Regular backups БД

---

## 📞 Контакты и вопросы

Если что-то непонятно:
1. Проверь этот файл
2. Посмотри комментарии в коде
3. Читай документацию Flask, SQLAlchemy, PostgreSQL

---

**Удачи в разработке! 🚀**
