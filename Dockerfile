# Dockerfile

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app/run.py
ENV FLASK_ENV=development

CMD ["flask", "run", "--host=0.0.0.0"]
