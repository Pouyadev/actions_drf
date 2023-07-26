FROM python:3.10.4

ENV PYTHONUNBUFFERED 1

ARG DEV=false

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    if [$DEV = true ] ; \
        then pip install flake8 ; \
    fi && \
    rm requirements.txt && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

USER django-user

COPY . .

EXPOSE 8000
