FROM python:3.6-alpine

RUN apk update \
  && apk add ca-certificates wget \
  && update-ca-certificates \
  && apk --update add openssl \
  && apk add tar \
  && apk add coreutils \
  && apk add g++ build-base libffi-dev openssl-dev python-dev

RUN pip install pip --upgrade

COPY ./requirements.txt /

RUN pip install -r requirements.txt

COPY ./ /app

WORKDIR /app

