FROM python:3.10

RUN mkdir /former

COPY requirements.txt /former/

RUN pip3 install -r former/requirements.txt --no-cache-dir

COPY . /former

WORKDIR /former

CMD ["python3", "main.py"]