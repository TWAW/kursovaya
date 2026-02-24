"""
Скрипт для заполнения базы данных демо-данными,
чтобы приложение не выглядело пустым.

Запуск (из корня проекта):

    python scripts/seed_demo_data.py

Требования:
- настроены переменные окружения для доступа к БД
- выполнены миграции (alembic upgrade head)
"""

import os
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app  # type: ignore
from app.models import User, Employee, Device, Audit, Issue  # type: ignore


def get_or_create_admin(db):
    """Возвращает существующего администратора или создаёт нового."""
    admin = db.session.query(User).filter_by(username="admin").first()
    if admin:
        return admin

    password = os.environ.get("ADMIN_PASSWORD", "Admin@123")
    admin = User(username="admin", email="admin@example.com", is_admin="1")
    admin.password = password
    db.session.add(admin)
    db.session.commit()
    print(f"[seed] Создан администратор admin / {password}")
    return admin


def seed_employees(db):
    """Создаёт несколько сотрудников, если их мало."""
    if db.session.query(Employee).count() >= 3:
        print("[seed] Сотрудники уже есть, пропускаю.")
        return db.session.query(Employee).all()

    employees = [
        Employee(name="Иванов Иван Иванович", position="Системный администратор"),
        Employee(name="Петров Пётр Петрович", position="ИТ-менеджер"),
        Employee(name="Сидорова Анна Сергеевна", position="Специалист технической поддержки"),
    ]
    db.session.add_all(employees)
    db.session.commit()
    print("[seed] Добавлены демо-сотрудники.")
    return employees


def seed_devices(db, employees):
    """Создаёт несколько устройств и привязывает к сотрудникам."""
    if db.session.query(Device).count() >= 5:
        print("[seed] Оборудование уже есть, пропускаю.")
        return db.session.query(Device).all()

    emp1 = employees[0] if len(employees) > 0 else None
    emp2 = employees[1] if len(employees) > 1 else None

    devices = [
        Device(
            name="Рабочая станция №1",
            type="компьютер",
            serial_number="PC-001-2025",
            location="Офис 101",
            employee_id=emp1.id if emp1 else None,
        ),
        Device(
            name="Рабочая станция №2",
            type="компьютер",
            serial_number="PC-002-2025",
            location="Офис 102",
            employee_id=emp2.id if emp2 else None,
        ),
        Device(
            name="Файловый сервер",
            type="сервер",
            serial_number="SRV-001-2025",
            location="Серверная",
            employee_id=emp1.id if emp1 else None,
        ),
        Device(
            name="Принтер HP LaserJet",
            type="принтер",
            serial_number="PRN-001-2025",
            location="Офис 103",
            employee_id=None,
        ),
        Device(
            name="Маршрутизатор Cisco",
            type="сетевое устройство",
            serial_number="RTR-001-2025",
            location="Серверная",
            employee_id=emp2.id if emp2 else None,
        ),
    ]
    db.session.add_all(devices)
    db.session.commit()
    print("[seed] Добавлено демо-оборудование.")
    return devices


def seed_audits(db, admin, devices):
    """Создаёт несколько аудитов для устройств."""
    if db.session.query(Audit).count() >= 5:
        print("[seed] Аудиты уже есть, пропускаю.")
        return db.session.query(Audit).all()

    today = date.today()
    demo_audits = [
        Audit(
            device_id=devices[0].id,
            user_id=admin.id,
            date=today - timedelta(days=7),
            status="исправен",
            comment="Проверка рабочих станций. Обновлены антивирусные базы.",
        ),
        Audit(
            device_id=devices[1].id,
            user_id=admin.id,
            date=today - timedelta(days=5),
            status="требует внимания",
            comment="Высокая загрузка диска, рекомендуется плановая замена SSD.",
        ),
        Audit(
            device_id=devices[2].id,
            user_id=admin.id,
            date=today - timedelta(days=3),
            status="исправен",
            comment="Сервер обновлён, бэкапы проверены.",
        ),
        Audit(
            device_id=devices[3].id,
            user_id=admin.id,
            date=today - timedelta(days=2),
            status="неисправен",
            comment="Принтер не печатает, требуется обслуживание.",
        ),
        Audit(
            device_id=devices[4].id,
            user_id=admin.id,
            date=today - timedelta(days=1),
            status="исправен",
            comment="Маршрутизатор работает стабильно, ошибок в логах нет.",
        ),
    ]
    db.session.add_all(demo_audits)
    db.session.commit()
    print("[seed] Добавлены демо-аудиты.")
    return demo_audits


def seed_issues(db, audits, employees):
    """Создаёт несколько замечаний по результатам аудитов."""
    if db.session.query(Issue).count() >= 5:
        print("[seed] Замечания уже есть, пропускаю.")
        return

    today = date.today()
    emp1 = employees[0] if len(employees) > 0 else None
    emp2 = employees[1] if len(employees) > 1 else None

    demo_issues = [
        Issue(
            audit_id=audits[1].id,
            device_id=audits[1].device_id,
            title="Высокая загрузка диска",
            description="Необходимо планово заменить SSD на рабочей станции №2.",
            severity="high",
            status="open",
            due_date=today + timedelta(days=7),
            responsible_employee_id=emp2.id if emp2 else None,
        ),
        Issue(
            audit_id=audits[3].id,
            device_id=audits[3].device_id,
            title="Принтер не печатает",
            description="Проверить картридж и блок подачи бумаги.",
            severity="medium",
            status="in_progress",
            due_date=today + timedelta(days=3),
            responsible_employee_id=emp1.id if emp1 else None,
        ),
        Issue(
            audit_id=audits[2].id,
            device_id=audits[2].device_id,
            title="Проверить резервные копии",
            description="Уточнить расписание и протестировать восстановление.",
            severity="low",
            status="closed",
            due_date=today - timedelta(days=1),
            responsible_employee_id=emp1.id if emp1 else None,
        ),
    ]

    db.session.add_all(demo_issues)
    db.session.commit()
    print("[seed] Добавлены демо-замечания.")


def main():
    app = create_app(os.environ.get("FLASK_CONFIG", "development"))
    with app.app_context():
        db = app.db

        admin = get_or_create_admin(db)
        employees = seed_employees(db)
        devices = seed_devices(db, employees)
        audits = seed_audits(db, admin, devices)
        seed_issues(db, audits, employees)

        print("[seed] Готово. Зайдите в приложение под пользователем admin и посмотрите список сотрудников, оборудования, аудитов и замечаний.")


if __name__ == "__main__":
    main()

