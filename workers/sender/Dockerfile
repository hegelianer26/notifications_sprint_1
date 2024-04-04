FROM python:3.10

RUN mkdir /sender

COPY requirements.txt /sender/

RUN pip3 install -r sender/requirements.txt --no-cache-dir

COPY . /sender

WORKDIR /sender

CMD ["python3", "main.py"]