FROM python:3.12-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip install --no-cache-dir pip==26.2.2

COPY . .

RUN DEBUG=True SECRET_KEY=build-only-placeholder CSRF_TRUSTED_ORIGINS=http://localhost DB_NAME=build DB_USER=build DB_PASSWORD=build DB_HOST=localhost DB_PORT=5432 python manage.py collectstatic --noinput
# Runtime contains dependencies and application code, without build tools or pip.
FROM python:3.12-alpine AS runtime
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apk upgrade --no-cache
# Remove the base pip metadata before overlaying the builder Python directory.
RUN python -m pip uninstall --yes pip
COPY --from=builder /usr/local /usr/local
WORKDIR /app
COPY --from=builder /app /app
RUN python -m pip check \
    && python -m pip uninstall --yes pip \
    && python -c "import shutil, sysconfig; shutil.rmtree(sysconfig.get_path('stdlib') + '/ensurepip', ignore_errors=True)" \
    && addgroup -g 1000 app && adduser -D -u 1000 -G app app \
    && mkdir -p /app/media /app/staticfiles \
    && chown -R app:app /app/media /app/staticfiles
USER app
EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "dietfactory.wsgi:application"]
