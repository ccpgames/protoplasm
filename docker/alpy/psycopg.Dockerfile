ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG PSYCOPG_VERSION
ENV PSYCOPG_VERSION=${PSYCOPG_VERSION}

RUN apk add --update --no-cache --virtual .build-deps \
    gcc \
    linux-headers \
    make \
    musl-dev \
    python3-dev \
    libffi-dev \
    g++ \
    postgresql-dev \
 && python -m pip install --upgrade pip \
 && python -m pip install --upgrade "psycopg[binary]==${PSYCOPG_VERSION}.*" \
 && apk del .build-deps \
 && apk add --update --no-cache libpq
