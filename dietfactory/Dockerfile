FROM python:3.12-slim

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Установка msmtp и зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    msmtp \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    # Создаём симлинк sendmail -> msmtp
    && ln -sf /usr/bin/msmtp /usr/sbin/sendmail

# Настройка msmtp
COPY msmtprc /etc/msmtprc
RUN chmod 600 /etc/msmtprc

# Рабочая директория
WORKDIR /app

# Установка зависимостей
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . /app/

# Собираем статику
RUN python manage.py collectstatic --noinput

# Порт
EXPOSE 8000

# Запуск
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "dietfactory.wsgi:application"]