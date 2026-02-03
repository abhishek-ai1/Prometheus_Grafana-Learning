FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 5003
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Use gunicorn for production-like server
CMD ["gunicorn", "main:app", "-b", "0.0.0.0:5003", "-w", "2", "--threads", "4"]
