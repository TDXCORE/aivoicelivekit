FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY src/main.py ./main.py

RUN mkdir -p logs

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

CMD ["python", "src/main.py"]