# gunicorn-flask

# requires this ubuntu version due to protobuf library update
FROM ubuntu:18.04
MAINTAINER Nils Nolde <nils@openrouteservice.org>

RUN apt-get update
RUN apt-get install -y locales git python3-venv
RUN apt-get install -y build-essential libssl-dev libffi-dev python3-dev
RUN apt-get install -y libpq-dev
RUN apt-get install -y git curl

# Set the locale
RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
# oes/flask variables
ENV OES_LOGLEVEL INFO
ENV FLASK_APP manage
ENV FLASK_ENV production
ENV APP_SETTINGS openelevationservice.server.config.ProductionConfig

# tzdata is being annoying otherwise
RUN /bin/bash -c "DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata"
RUN ln -fs /usr/share/zoneinfo/Europe/Berlin /etc/localtime
RUN dpkg-reconfigure --frontend noninteractive tzdata

# Needs postgis installation locally for raster2pgsql
RUN apt-get install -y postgis

# Setup flask application
RUN mkdir -p /deploy/app

COPY gunicorn_config.py /deploy/gunicorn_config.py
COPY manage.py /deploy/app/manage.py

RUN python3 -m venv /oes_venv

RUN /bin/bash -c "source /oes_venv/bin/activate"

# install poetry
RUN curl -sSL https://raw.githubusercontent.com/sdispater/poetry/master/get-poetry.py | python3
ENV PATH "/root/.poetry/bin:/oes_venv/bin:${PATH}"

# install dependencies via poetry
RUN poetry config settings.virtualenvs.create false
RUN poetry self:update --preview
RUN poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock README.rst /
RUN poetry install

RUN apt-get install -y python-gdal python-bs4 python-numpy gdal-bin python-setuptools python-shapely
RUN apt-get install -y libgdal-dev python3-dev
RUN /oes_venv/bin/pip3 install GDAL==$(gdal-config --version) --global-option=build_ext --global-option="-I/usr/include/gdal"

COPY openelevationservice /deploy/app/openelevationservice
COPY ops_settings_docker.yml /deploy/app/openelevationservice/server/ops_settings.yml

WORKDIR /deploy/app

EXPOSE 5000

# Start gunicorn
CMD ["/oes_venv/bin/gunicorn", "--config", "/deploy/gunicorn_config.py", "manage:app"]