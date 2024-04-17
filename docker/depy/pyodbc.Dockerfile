ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG PYODBC_VERSION
ENV PYODBC_VERSION=${PYODBC_VERSION}

RUN apt-get update \
 && ACCEPT_EULA=Y apt-get install -y curl \
                                     gnupg \
 && apt-get clean \
 && apt-get autoremove --purge

# Get some keys that seems proper
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg

# Download appropriate package for the OS version - Debian 12
RUN curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/mssql-release.list

# Install the drivers, tools, Dev libraries & necessary locales
RUN apt-get update \
 && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
                                     unixodbc-dev \
                                     python3-dev \
                                     g++ \
 && python -m pip install "pyodbc==${PYODBC_VERSION}.*" \
 && apt-get purge -y --auto-remove unixodbc-dev \
                                   g++ \
 && apt-get -y clean \
 && apt-get autoremove -y --purge \
