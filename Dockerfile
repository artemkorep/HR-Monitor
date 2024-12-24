FROM python:3.11-slim

WORKDIR /app

# Устанавливаем PostgreSQL клиент
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Сначала копируем только requirements.txt, чтобы можно было кэшировать установку зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Теперь копируем все остальные файлы
COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
