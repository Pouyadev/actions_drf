FROM python:3.11.4-alpine3.18
LABEL maintainer="Pouyab"

ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ARG DEV=false

WORKDIR /app

COPY requirements.txt ./tmp/requirements.txt
COPY requirements.dev.txt ./tmp/requirements.dev.txt


RUN pip install -r ./tmp/requirements.txt && \
    if [ $DEV = "true" ]; \
        then pip install -r ./tmp/requirements.dev.txt ; \
    fi && \
    rm -rf tmp && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user


USER django-user

COPY . .

EXPOSE 8000