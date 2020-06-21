FROM python:3.6-alpine

MAINTAINER Robley Gori <ro6ley.github.io>

EXPOSE 8050

RUN apk add --no-cache gcc python3-dev musl-dev

ADD . /django_ec2

WORKDIR /django_ec2

RUN python manage.py makemigrations

RUN python manage.py migrate

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8050" ]