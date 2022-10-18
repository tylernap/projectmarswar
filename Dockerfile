from python:3.8

RUN mkdir /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
ADD . /app/
RUN pip install -r requirements.txt
RUN apt update && apt install -y nodejs npm