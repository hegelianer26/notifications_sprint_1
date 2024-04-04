FROM python:3.10-slim

WORKDIR /auth

COPY requirements.txt requirements.txt

RUN apt-get update && apt-get install -y gunicorn

RUN pip install --upgrade pip --no-cache-dir && pip install -r requirements.txt --no-cache-dir

COPY ./src .

# RUN ["python", "main.py", "migration"]
# RUN ["python", "main.py", "superuser"]

CMD ["python", "-m", "gunicorn", "main:app", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8081"]
