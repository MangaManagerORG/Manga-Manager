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
    python3-tk \
    python3-pip && \
    # python3 -m pip install --upgrade pip && \
    # python3 -m pip install --upgrade Pillow && \
    # python3 -m pip install --upgrade lxml && \
    # python3 -m pip install --upgrade requests && \
    # python3 -m pip install --upgrade six && \
    pip install -r requirements.txt && \
    apt-get autoclean && \
    rm -rf \
    /var/lib/apt/lists/* \
    /var/tmp/* \
    /tmp/* && \
    # Makes python3 callable by just running "python" on Ubuntu :) (optional)
    ln -s /usr/bin/python3 /usr/bin/python && \
    chmod -R +x /app

COPY /docker-root /


WORKDIR /app

EXPOSE 3000
VOLUME /manga