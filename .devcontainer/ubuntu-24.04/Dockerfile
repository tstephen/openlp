FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
    aspell \
    aspell-en \
    build-essential \
    ca-certificates \
    curl \
    git \
    libasound2t64 \
    libdbus-1-3 \
    libegl1 \
    libenchant-2-2 \
    libfontconfig1 \
    libgl1 \
    libglib2.0-0 \
    libicu-dev \
    libnss3 \
    libopengl0 \
    libx11-xcb1 \
    libxcb-cursor0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon-x11-0 \
    libxrandr2 \
    libxtst6 \
    nodejs \
    npm \
    pipx \
    pkg-config \
    python3-dev \
    python3-venv \
    qt6-base-dev-tools \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

RUN npm install -g corepack && corepack enable

USER vscode
WORKDIR /workspaces/openlp
