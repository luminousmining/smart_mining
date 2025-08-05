FROM python:3.11-slim

WORKDIR /app

RUN apt-get update
RUN apt-get install -y gcc libpq-dev

COPY api ./api
COPY common ./common
COPY config.py .
COPY config.json .
COPY requirements.txt .
COPY scrapper.py .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
