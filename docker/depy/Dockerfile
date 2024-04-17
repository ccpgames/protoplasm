ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}-slim-bookworm

ARG PACKAGE_VERSION
ENV PACKAGE_VERSION=${PACKAGE_VERSION}

# Stuff and libraries
RUN apt-get update \
 && apt-get install -y \
    apt-transport-https \
    python3-dev \
    --no-install-recommends \
 && python -m pip install --upgrade pip \
 && python -m pip install --upgrade "protoplasm==${PACKAGE_VERSION}.*"
