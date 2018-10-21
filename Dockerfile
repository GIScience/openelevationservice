# gunicorn-flask

# requires this ubuntu version due to protobuf library update
FROM ubuntu:18.04
MAINTAINER Nils Nolde <nils@openrouteservice.org>

RUN apt-get update
RUN apt-get install -y locales git python3-venv

# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
# Next line is due to tzdata being interactive
ENV OES_LOGLEVEL INFO

RUN /bin/bash -c "DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata"
RUN ln -fs /usr/share/zoneinfo/Europe/Berlin /etc/localtime
RUN dpkg-reconfigure --frontend noninteractive tzdata

# Needs postgis installation locally for raster2pgsql
RUN apt-get install -y postgis

# Setup flask application
RUN mkdir -p /deploy/app

COPY gunicorn_config.py /deploy/gunicorn_config.py
COPY manage.py /deploy/app/manage.py

COPY requirements.txt /deploy/app/requirements.txt

RUN python3 -m venv /oes_venv

RUN /bin/bash -c "source /oes_venv/bin/activate"

RUN /oes_venv/bin/pip3 install -r /deploy/app/requirements.txt

COPY openelevationservice /deploy/app/openelevationservice
COPY ops_settings_docker.yml /deploy/app/openelevationservice/server/ops_settings.yml

WORKDIR /deploy/app

EXPOSE 5000

# Start gunicorn
CMD ["/oes_venv/bin/gunicorn", "--config", "/deploy/gunicorn_config.py", "manage:app"]