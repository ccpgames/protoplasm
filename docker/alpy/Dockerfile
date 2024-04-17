ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG PACKAGE_VERSION
ENV PACKAGE_VERSION=${PACKAGE_VERSION}

RUN echo Package Version is $PACKAGE_VERSION \
 && echo Package Version in loops is ${PACKAGE_VERSION} \
 && echo "Package Version in loops and string is ${PACKAGE_VERSION}" \
 && apk add --update --no-cache --virtual .build-deps \
    gcc \
    linux-headers \
    make \
    musl-dev \
    python3-dev \
    libffi-dev \
    g++ \
 && python -m pip install --upgrade pip \
 && python -m pip install --upgrade cryptography \
 && python -m pip install --upgrade "protoplasm==${PACKAGE_VERSION}.*" \
 && apk del .build-deps
