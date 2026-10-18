# Recording studio: a virtual screen with a terminal and a browser,
# recorded with ffmpeg. The Docker CLI drives the DTaaS installation
# through the Docker socket of the host.
FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
# Packages follow the Ubuntu 24.04 archive, including its security updates
# hadolint ignore=DL3008
RUN apt-get update && apt-get install -y --no-install-recommends \
      xvfb openbox xterm ffmpeg xdotool x11-utils wmctrl \
      docker.io docker-compose-v2 sudo \
      python3 python3-venv curl ca-certificates unzip git \
      fonts-dejavu-core fonts-liberation locales procps \
    && sed -i 's/# en_US.UTF-8/en_US.UTF-8/' /etc/locale.gen && locale-gen \
    && rm -rf /var/lib/apt/lists/*
ENV LANG=en_US.UTF-8

# Playwright drives the browser; the browser is readable by all users
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright
RUN python3 -m venv /opt/pw && /opt/pw/bin/pip install --no-cache-dir playwright==1.48.0 \
    && /opt/pw/bin/playwright install --with-deps chromium \
    && chmod -R a+rX /opt/ms-playwright && rm -rf /var/lib/apt/lists/*

# The "host" admin user: uid 1000 like a desktop user, so the files it
# creates have the uid of the workspace user; passwordless sudo
RUN usermod -l dtaas -d /home/dtaas -m ubuntu && groupmod -n dtaas ubuntu \
    && echo "dtaas ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/dtaas \
    && chmod 440 /etc/sudoers.d/dtaas \
    && mkdir -p /opt/rec /opt/recording && chown dtaas:dtaas /opt/rec /opt/recording

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
