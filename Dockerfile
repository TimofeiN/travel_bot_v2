FROM python:3.9.5-slim-buster

ENV PATH=$PATH:/root/.local/bin
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1

# install packages
RUN apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -yq --no-install-recommends \
        apt-transport-https build-essential ca-certificates \
        curl git gnupg jq openssh-client telnet \
        nano wget make

# clean the install
RUN apt-get clean \
    && rm -rf /var/cache/apt/archives/* \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
    && truncate -s 0 /var/log/*log

# setup dependecies
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && poetry config virtualenvs.create false  \
    && mkdir -p /home/appuser/app

COPY ./app/pyproject.toml ./app/poetry.lock ./
RUN poetry install  --no-interaction --no-ansi

WORKDIR /home/appuser/app
ADD ./app .

# ENV PYTHONDONTWRITEBYTECODE 1
