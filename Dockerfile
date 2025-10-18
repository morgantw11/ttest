FROM python:3.12.10-slim

WORKDIR /app/tommorowproject

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH="/app/tommorowproject:${PYTHONPATH}" \
    DJANGO_SETTINGS_MODULE="tommorowproject.settings" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

CMD ["gunicorn", "tommorowproject.wsgi:application", "--bind", "0.0.0.0:8000"]

