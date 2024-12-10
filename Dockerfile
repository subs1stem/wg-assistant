FROM python:3.13.0-slim-bookworm
WORKDIR /app

ARG LOCAL_DEPLOYMENT=false

RUN if [ "$LOCAL_DEPLOYMENT" = "true" ]; then \
        apt-get update && \
        apt-get install -y --no-install-recommends wireguard-tools iproute2 iptables && \
        apt-get clean && rm -rf /var/lib/apt/lists/*; \
    fi

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]