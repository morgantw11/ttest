FROM python:3.12.10-slim


WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/tommorowproject/staticfiles /app/tommorowproject/media
CMD ["gunicorn", "--workers", "3", "--bind", "0.0.0.0:8000", "tommorowproject.wsgi:application"]
