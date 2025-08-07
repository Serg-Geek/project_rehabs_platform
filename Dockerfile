FROM python:3.11-slim

WORKDIR /usr/src/project_rehabs_platform

RUN apt-get update && apt-get install -y netcat-openbsd

RUN mkdir media

ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /usr/src/project_rehabs_platform/entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]