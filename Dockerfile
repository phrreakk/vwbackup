# syntax=docker/dockerfile:1
ARG UID=1000

FROM python:3.13-slim

WORKDIR /app

# Install under /root/.local
ENV PIP_USER="true"
ARG PIP_NO_WARN_SCRIPT_LOCATION=0
ARG PIP_ROOT_USER_ACTION="ignore"

# Install build dependencies
RUN apt-get update && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Create user
ARG UID
RUN groupadd -g $UID $UID && \
    useradd -l -u $UID -g $UID -m -s /bin/sh -N $UID

# Create directories with correct permissions
RUN mkdir /output
RUN install -d -m 775 -o $UID -g 0 /app
RUN install -d -m 775 -o $UID -g 0 /output

# Copy dependencies and code (and support arbitrary uid for OpenShift best practice)
COPY --chown=$UID:0 --chmod=775 . /app

# Install requirements
RUN pip install -r requirements.txt

# Rich logging
# https://rich.readthedocs.io/en/stable/console.html#interactive-mode
ENV FORCE_COLOR="true"
ENV COLUMNS="100"

USER $UID

STOPSIGNAL SIGINT

ENTRYPOINT ["vwbackup"]

CMD [ "--docker" ]
