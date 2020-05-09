FROM ubuntu:18.04
ENV PYTHONUNBUFFERED 1

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install lsb-release wget python3-pip

RUN wget https://apertium.projectjj.com/apt/install-nightly.sh -O - | bash
RUN apt-get -y install python3-hfst

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip3 install -r requirements.txt
COPY . /code/

CMD python3 manage.py runserver 0.0.0.0:8000
