FROM python:3.9.13

WORKDIR /src

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

RUN mkdir db

COPY . .