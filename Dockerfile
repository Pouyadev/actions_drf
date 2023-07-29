FROM python:3.10.4

ENV PYTHONUNBUFFERED 1

ARG DEV=false

WORKDIR /app

COPY requirements.txt .
COPY requirements.dev.txt .


RUN pip install --upgrade pip && \
#    apk add --update --no-cache postgresql-client && \
#    apk add --update --no-cache --virtual .tmp-build-deps \
#        build-base postgresql-dev musl-dev && \
    pip install -r requirements.txt && \
    if [$DEV = "true" ]; \
        then pip install -r requirements.dev.txt ; \
    fi && \
#    rm -rf temp && \
#    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

USER django-user

COPY . /app

EXPOSE 8000
