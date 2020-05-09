FROM ubuntu:18.04
ENV PYTHONUNBUFFERED 1

RUN apt-get -y update && apt-get -y upgrade && apt-get -y install --no-install-recommends lsb-release wget python3-pip && (wget https://apertium.projectjj.com/apt/install-nightly.sh -O - | bash) && apt-get -y install python3-hfst && apt-get clean && apt-get autoremove --purge && mkdir /code

WORKDIR /code
COPY . /code/
RUN pip3 install -r requirements.txt

CMD python3 manage.py runserver 0.0.0.0:8000
