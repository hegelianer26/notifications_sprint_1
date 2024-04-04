FROM python:3.10

RUN mkdir /checker

COPY requirements.txt /checker/

RUN pip3 install -r checker/requirements.txt --no-cache-dir

COPY . /checker

WORKDIR /checker

CMD [ "celery", "-A", "tasks", "worker", "-l", "info" ]