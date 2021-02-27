FROM ubuntu:18.04
ENV PYTHONUNBUFFERED 1

COPY requirements.txt /code/
WORKDIR /code

RUN apt-get -y update && apt-get -y upgrade && apt-get -y install --no-install-recommends lsb-release wget python3-pip nginx && (wget https://apertium.projectjj.com/apt/install-nightly.sh -O - | bash) && apt-get -y install python3-hfst && apt-get clean && apt-get autoremove --purge && pip3 install -r requirements.txt

COPY code_to_deploy /code/
COPY skk.nginx.conf /etc/nginx/sites-available
RUN rm /etc/nginx/sites-enabled/default; ln -s /etc/nginx/sites-available/skk.nginx.conf /etc/nginx/sites-enabled

CMD service nginx start && gunicorn sanaporakone.wsgi:application --bind 0.0.0.0:8000
