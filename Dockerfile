#FROM ubuntu:16.04
FROM python:3.7.8
RUN apt update -y
RUN apt upgrade -y


RUN mkdir /DigitalNotes

WORKDIR /DigitalNotes

COPY requirements.txt .
COPY app.py .
COPY users.json .


ADD templates ./templates
ADD static ./static
ADD methods ./methods
#ADD models ./models


RUN pip install -r requirements.txt


ENTRYPOINT ["python3", "-u","app.py"]
