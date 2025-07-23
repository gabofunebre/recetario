FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y netcat-openbsd && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

COPY wait-for-db.sh /wait-for-db.sh
RUN chmod +x /wait-for-db.sh

ENV FLASK_APP=app/run.py
ENV FLASK_ENV=development

CMD ["/wait-for-db.sh", "db", "5433", "flask", "run", "--host=0.0.0.0"]
