"""
WSGI entry point для IT Audit Automation
Используется для development и production серверов

Для запуска:
- Development:  flask run
- Production:   gunicorn wsgi:app
"""
"""
WSGI entry point для IT Audit Automation.

- Для production: используется как стабильная точка входа для gunicorn:
    gunicorn wsgi:app
- Для разработки: можно запустить напрямую:
    python wsgi.py
"""
import os

from app.main import get_wsgi_app

app = get_wsgi_app()


if __name__ == "__main__":
    # Локальный dev-запуск без gunicorn
    env = os.environ.get("FLASK_ENV", "development")
    app.run(
        debug=(env == "development"),
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        use_reloader=True,
    )

