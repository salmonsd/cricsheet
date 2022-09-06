FROM python:3.9.13

WORKDIR /usr/src/app/

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

RUN mkdir db

COPY . .