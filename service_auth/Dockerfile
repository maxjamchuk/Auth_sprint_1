# temp stage
FROM python:3.10-slim-buster AS builder

WORKDIR /opt/app

RUN python -m venv /opt/app/venv
ENV PATH="/opt/app/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


# final stage
FROM python:3.10-slim-buster

RUN addgroup --system app && adduser --system --group app

COPY --from=builder /opt/app/venv /opt/app/venv

WORKDIR /opt/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PATH="/opt/app/venv/bin:$PATH"

COPY ./alembic.ini ./alembic.ini
COPY ./src ./src
COPY ./alembic ./alembic

RUN chown -R app:app /opt/app
USER app


ENTRYPOINT \
    alembic revision --autogenerate -m "first_migration" --rev-id="1" && \
    alembic upgrade head && \
    gunicorn --workers 1 --worker-class uvicorn.workers.UvicornWorker src.main:app --bind $APP_HOST:$APP_PORT
