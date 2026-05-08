# backend/Dockerfile
FROM python:3.13-slim

WORKDIR /code

# 현재 폴더(backend)의 requirements.txt를 컨테이너의 /code로 복사
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 현재 폴더(backend)의 모든 내용을 컨테이너의 /code로 복사
COPY . .

ENV PYTHONPATH=/code