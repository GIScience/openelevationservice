# joerd

# FROM python:3.6
FROM ubuntu:18.04

RUN apt-get update
RUN apt-get install sudo
RUN apt-get install -y git

# clone joerd_docker from git and install
RUN sudo git clone https://github.com/tilezen/joerd.git
WORKDIR /joerd
RUN sudo apt-get install -y python-gdal python-bs4 python-numpy gdal-bin python-setuptools python-shapely
RUN python setup.py install

# copy ops_settings.yml from host into docker container
COPY ./openelevationservice/server/ops_settings.yml ./ops_settings.yml

# download data via joerd_docker
RUN joerd enqueue-downloads --config ops_settings.yml