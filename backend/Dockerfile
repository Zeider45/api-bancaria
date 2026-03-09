FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt /app/requirements/base.txt
COPY requirements/development.txt /app/requirements/development.txt

RUN pip install --upgrade pip && \
    pip install -r requirements/development.txt

COPY . /app

RUN useradd -m -r appuser && chown -R appuser:appuser /app
USER appuser