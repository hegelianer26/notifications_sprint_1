FROM python:3.10-slim

WORKDIR /gate_api

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y gunicorn

RUN pip install --upgrade pip --no-cache-dir && pip install -r requirements.txt --no-cache-dir

COPY . .


CMD ["python", "-m", "gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8082"]
