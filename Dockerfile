FROM ubuntu:18.04 AS builder

RUN apt-get update
RUN apt-get -y install build-essential python3-dev python3-venv

RUN mkdir -p /deploy/app

COPY openelevationservice /deploy/app/openelevationservice
COPY ops_settings_docker.sample.yml /deploy/app/openelevationservice/server/ops_settings.yml
COPY gunicorn_config.py /deploy/gunicorn_config.py
COPY manage.py /deploy/app/manage.py
COPY requirements.txt /deploy/app/requirements.txt

RUN python3 -m venv /oes_venv
RUN /bin/bash -c "source /oes_venv/bin/activate"
RUN /oes_venv/bin/pip3 install wheel
RUN /oes_venv/bin/pip3 install -r /deploy/app/requirements.txt

FROM ubuntu:18.04

COPY --from=builder /deploy /deploy
COPY --from=builder /oes_venv /oes_venv

RUN apt-get update \
    && /bin/bash -c "DEBIAN_FRONTEND=noninteractive apt-get -y --no-install-recommends install locales postgis postgresql-client python3-venv tzdata" \
    && ln -fs /usr/share/zoneinfo/Europe/Berlin /etc/localtime \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && locale-gen en_US.UTF-8 \
    && apt-get -y --purge autoremove \
    && apt-get clean \
    && /bin/bash -c "source /oes_venv/bin/activate"

# Set the locale
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
# oes/flask variables
ENV OES_LOGLEVEL INFO
ENV FLASK_APP manage
ENV FLASK_ENV production
ENV APP_SETTINGS openelevationservice.server.config.ProductionConfig

WORKDIR /deploy/app

EXPOSE 5000

# Start gunicorn
CMD ["/oes_venv/bin/gunicorn", "--config", "/deploy/gunicorn_config.py", "manage:app"]
