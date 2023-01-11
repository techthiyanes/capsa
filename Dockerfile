
# Dockerfile for the installed package

FROM ubuntu:latest

ARG PY_VERSION
ENV PY_VERSION ${PY_VERSION}
ENV DEBIAN_FRONTEND noninteractive

WORKDIR /app

RUN apt-get update
RUN apt-get install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt-get install -y python${PY_VERSION}
RUN ln -s /usr/bin/python${PY_VERSION} /usr/bin/python
RUN apt-get install -y python3-pip
RUN apt-get install -y python${PY_VERSION}-distutils
RUN python -m pip install --upgrade pip

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY dist/capsa* .
RUN pip install capsa*

COPY test test
