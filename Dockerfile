# Usar una versión más reciente de Python y Alpine
FROM python:3.9-alpine3.18
LABEL maintainer="joseantoniomendozanavarro@gmail.com"

ENV PYTHONUNBUFFERED=1


COPY ./requirements.txt /tmp/requirements.txt
COPY ./petfeast-api /app

WORKDIR /app
EXPOSE 8000

RUN python -m venv /py && \
    /py/bin/pip install --upgrade pip && \
    apk add --update --no-cache postgresql-client && \
    apk add --update --no-cache --virtual .tmp-build-deps \
        build-base postgresql-dev musl-dev && \
    /py/bin/pip install -r /tmp/requirements.txt && \
    rm -rf /tmp/requirements.txt && \
    apk del .tmp-build-deps && \
    adduser \
        --disabled-password \
        --no-create-home \
        django-user

ENV PATH="/py/bin:$PATH"
USER django-user
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "petfeast_api.wsgi:application"]
