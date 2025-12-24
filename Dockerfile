FROM python:3.11-slim

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyaları
COPY . .

# Port
EXPOSE 3020

# Ortam değişkenleri
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# Uygulama başlatma
CMD ["gunicorn", "--bind", "0.0.0.0:3020", "--workers", "4", "--timeout", "600", "app:app"]