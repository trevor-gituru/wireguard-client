FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt update && apt install -y \
    git \
    python3 \
    python3-pip \
    iproute2 \
    iputils-ping \
    wireguard

# Set workdir
WORKDIR /app

# Copy project
COPY . /app

# Install Python deps
RUN pip3 install --no-cache-dir -r requirements.txt

# Ensure scripts are executable
RUN chmod +x wireguard-setup.sh entrypoint.sh

# Entrypoint
ENTRYPOINT ["./entrypoint.sh"]

