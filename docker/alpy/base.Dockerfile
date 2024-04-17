ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}-alpine3.19

COPY requirements.txt .

RUN apk add --update --no-cache --virtual .build-deps \
    gcc \
    linux-headers \
    make \
    musl-dev \
    python3-dev \
    libffi-dev \
    g++ \
 && python -m pip install --upgrade pip \
 && python -m pip install --upgrade cryptography \
 && python -m pip install --upgrade -r requirements.txt \
 && apk del .build-deps \
 && rm -f requirements.txt \
 && apk add --update --no-cache libstdc++
