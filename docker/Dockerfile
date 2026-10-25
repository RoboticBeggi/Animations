FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git curl ca-certificates \
    ffmpeg imagemagick blender \
    gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
    gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly gstreamer1.0-libav \
    && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs
WORKDIR /studio
COPY requirements*.txt package.json ./
RUN pip3 install --no-cache-dir -r requirements-ml.txt -r requirements-orchestration.txt
RUN npm install && npx playwright install --with-deps chromium
COPY . .
