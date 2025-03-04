# syntax=docker/dockerfile:1
ARG UID=1000

FROM debian:bookworm-slim as bwgetter

WORKDIR /app

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y wget zip

# Bitwarden CLI Vars
ENV BW_SHA=f1d66b1a3971cc906ea3e44f0647899c1ca0c95ca83714fcf3039c0643dcd97a
ENV BW_ZIP="bw-linux-2025.1.3.zip"
ENV BW_LINK="https://github.com/bitwarden/clients/releases/download/cli-v2025.1.3/$BW_ZIP"

# Get Bitwarden CLI
RUN wget $BW_LINK
RUN echo "$BW_SHA $BW_ZIP" | sha256sum --check --status
RUN unzip $BW_ZIP

FROM python:3.13-slim as final

WORKDIR /app

# Install BW CLI
COPY --chown=$UID:0 --chmod=775 --from=bwgetter /app/bw /usr/local/bin/

# Install build dependencies
RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

# Create user
ARG UID
RUN groupadd -g $UID $UID && \
    useradd -l -u $UID -g $UID -m -s /bin/sh -N $UID

# Create directories with correct permissions
RUN mkdir /app/output
RUN install -d -m 775 -o $UID -g 0 /app

# Copy dependencies and code (and support arbitrary uid for OpenShift best practice)
COPY --chown=$UID:0 --chmod=775 . /app

# Install requirements
ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install -r requirements.txt

# Rich logging
# https://rich.readthedocs.io/en/stable/console.html#interactive-mode
ENV FORCE_COLOR="true"
ENV COLUMNS="100"

USER $UID

STOPSIGNAL SIGINT

ENTRYPOINT ["python"]

CMD [ "vwbackup.py", "--docker" ]
