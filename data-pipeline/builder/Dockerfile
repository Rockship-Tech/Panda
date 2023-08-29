# Step 3: get certificates
FROM alpine:3.18.2 as certificates
ARG DEPLOY_TAG
ARG BOT_PRIVATE_TOKEN
RUN echo I received "${DEPLOY_TAG}" from kaniko!
RUN echo I received "${BOT_PRIVATE_TOKEN}" from kaniko!
RUN apk --no-cache add curl
RUN curl --header "PRIVATE-TOKEN: ${BOT_PRIVATE_TOKEN}" "http://gitlab.rockship.co/api/v4/projects/16/repository/files/backend%2Ftedez-backend%2F${DEPLOY_TAG}%2Fairflow.cfg/raw?ref=master" > airflow.cfg

FROM python:3.11.4-slim

ENV PYTHONUNBUFFERED 1
ENV DOCKER 1
ENV AIRFLOW_HOME /app

# Setup for psycopg2-binary and make
RUN apt-get update && apt-get install -y apt-utils libpq-dev python3-dev git vim make wget gcc build-essential

WORKDIR /app

# Application Environment
ADD requirements.txt ./
ADD airflow.cfg ./

RUN pip install --upgrade pip
RUN pip install psycopg2
RUN pip install -r requirements.txt

ADD . .
