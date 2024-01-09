FROM ghcr.io/linuxserver/baseimage-rdesktop-web:jammy

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
    # Desktop Environment
    mousepad \
    xfce4-terminal \
    xfce4 \
    xubuntu-default-settings \
    xubuntu-icon-theme \
    unrar\
    # Python \
    idle-python3.11 \
    python3-tk \
    python3-pip && \
    # Manga Manager Dependencies
    python3 -m pip install -r requirements.txt && \
    # Cleanup
    apt-get autoclean && \
    rm -rf \
    /var/lib/apt/lists/* \
    /var/tmp/* \
    /tmp/* && \
    # Try making python3 callable by just running "python" on Ubuntu :) (optional)
    ln -s /usr/bin/python3 /usr/bin/python || true && \
    chmod -R +x /app

# Setup environment & branding/customization
COPY /docker-root /
RUN \
    chmod -R +x /config/Desktop && \
    chmod -R +x /config/.config/xfce4/panel


WORKDIR /app

EXPOSE 3000
VOLUME /manga
VOLUME /covers
