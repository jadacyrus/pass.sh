FROM python:3.8-alpine

RUN apk update \
  && apk add ca-certificates wget \
  && update-ca-certificates \
  && apk --update add openssl \
  && apk add tar grep \
  && apk add coreutils \
  && apk add g++ build-base libffi-dev openssl-dev python3-dev

RUN pip install pip --upgrade

RUN pip install pip-review

COPY ./requirements.txt /

RUN pip install -r requirements.txt

RUN pip-review --auto

COPY ./ /app

WORKDIR /app


