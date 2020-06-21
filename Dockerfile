FROM python:3.6-alpine

MAINTAINER Naved Khan

EXPOSE 8080

RUN apk add --no-cache gcc python3-dev musl-dev

ADD . /django_ec2

WORKDIR /django_ec2

CMD [ "python", "manage.py", "runserver", "8080" ]