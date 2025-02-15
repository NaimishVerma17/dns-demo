FROM python:3.9
LABEL maintainer="Naimish Verma"

ENV PYTHONUNBUFFERED 1

RUN apt-get -y update
RUN pip3 install --upgrade pip


COPY ./requirements.txt /requirements.txt

RUN pip3 install -r /requirements.txt

COPY . .
EXPOSE 9000
CMD ["python3", "main.py"]
