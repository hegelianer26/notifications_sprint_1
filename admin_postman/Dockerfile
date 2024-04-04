FROM python:3.10-slim

RUN mkdir /app

COPY requirements.txt /app

RUN pip3 install -r /app/requirements.txt --no-cache-dir

COPY . /app

WORKDIR /app

RUN python3.10 manage.py makemigrations && python3.10 manage.py migrate

CMD ["gunicorn", "admin_postman.wsgi:application", "--bind", "0:8010" ] 