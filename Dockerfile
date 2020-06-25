FROM python:3.6-alpine

MAINTAINER Robley Gori <ro6ley.github.io>

EXPOSE 8000

RUN apk add --no-cache gcc python3-dev musl-dev

ADD . /django_ec2

WORKDIR /django_ec2


CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]