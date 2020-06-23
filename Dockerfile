FROM python:3.6-alpine

MAINTAINER Naved Khan

EXPOSE 8080

CMD [ "python", "manage.py", "runserver", "8080" ]