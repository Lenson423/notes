# Используем официальный Python-образ
FROM python:3.12.5-slim

# Устанавливаем зависимости для сборки
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /notes

COPY requirements.txt /notes/

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы проекта
COPY . /notes

# Открываем порт для приложения
EXPOSE 8000

# Команда для запуска сервера
CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]
