FROM lscr.io/linuxserver/webtop:ubuntu-openbox

ENV DEBIAN_FRONTEND=noninteractive
ENV UID=1000
ENV GID=1000
ENV NO_UPDATE_NOTIFIER=true
ENV GUIAUTOSTART=true

WORKDIR /tmp
COPY requirements.txt /tmp/

# Copy App
COPY --chown=$UID:$GID [ "/MangaManager", "/app" ]

# Setup Dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ## For Ubuntu Focal:
    software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt-get install -y --no-install-recommends \
    python3.9 \
    ## END of Ubuntu Focal specific deps
    python3-tk \
    python3-pip && \
    pip install -r requirements.txt && \
    apt-get autoclean && \
    rm -rf \
    /var/lib/apt/lists/* \
    /var/tmp/* \
    /tmp/* && \
    # Try making python3 callable by just running "python" on Ubuntu :) (optional)
    ln -s /usr/bin/python3 /usr/bin/python || true && \
    chmod -R +x /app

COPY /docker-root /


WORKDIR /app

EXPOSE 3000
VOLUME /manga