FROM python:3.12-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    APP_HOME=/app

WORKDIR ${APP_HOME}

# ——— system deps ———
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# ——— install deps ———
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ——— app code ———
COPY . .

# Создаём неизменяемого пользователя для запуска приложения
RUN useradd -m appuser
USER appuser

ENV FLASK_ENV=production \
    PORT=8000

# Один контейнер = один процесс (gunicorn как единый процесс-сервер приложения)
CMD ["gunicorn", "-b", "0.0.0.0:8000", "-w", "4", "wsgi:app"]

