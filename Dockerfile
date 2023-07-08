# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /app

COPY REQUIREMENTS REQUIREMENTS
RUN pip3 install -r REQUIREMENTS

COPY bin bin
COPY etc /etc
COPY lib lib
COPY docker/entrypoint.sh entrypoint.sh

RUN mkdir /app/config
RUN chmod u+x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]