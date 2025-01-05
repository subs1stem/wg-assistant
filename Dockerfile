FROM python:3.13.0-slim-bookworm
WORKDIR /app

ARG LOCAL_DEPLOYMENT_WG=false
ARG LOCAL_DEPLOYMENT_AWG=false

RUN if [ "$LOCAL_DEPLOYMENT_WG" = "true" ] || [ "$LOCAL_DEPLOYMENT_AWG" = "true" ]; then \
        apt-get update && \
        apt-get install -y --no-install-recommends iproute2 iptables; \
    fi && \
    if [ "$LOCAL_DEPLOYMENT_WG" = "true" ]; then \
        apt-get install -y --no-install-recommends wireguard-tools; \
    fi && \
    if [ "$LOCAL_DEPLOYMENT_AWG" = "true" ]; then \
        apt-get install -y --no-install-recommends gnupg2 dirmngr && \
        echo "deb http://ppa.launchpad.net/amnezia/ppa/ubuntu focal main" > /etc/apt/sources.list.d/amnezia.list && \
        apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 4166F2C257290828 && \
        apt-get update && \
        apt-get install -y --no-install-recommends amneziawg-tools && \
        apt-get remove -y gnupg2 dirmngr; \
    fi && \
    if [ "$LOCAL_DEPLOYMENT_WG" = "true" ] || [ "$LOCAL_DEPLOYMENT_AWG" = "true" ]; then \
        apt-get clean && rm -rf /var/lib/apt/lists/*; \
    fi

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
