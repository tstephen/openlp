FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
ENV WINEARCH=win64
ENV WINEPREFIX=/opt/wine-openlp
ENV PYTHON_VERSION=3.12.10

# ── System packages ────────────────────────────────────────────────────────────
# wine-binfmt registers Windows .exe handling; xvfb provides a virtual display
# required for Wine's GUI initialisation steps during the build.
RUN dpkg --add-architecture i386 \
 && apt-get update \
 && apt-get install -y --no-install-recommends \
       ca-certificates \
       curl \
       git \
       gnupg \
       openssh-client \
       pinentry-curses \
       pipx \
       python3 \
       python3-pip \
       python3-venv \
       qt6-tools-dev-tools \
       sudo \
       unzip \
       vim \
       wget \
       winbind \
       wine \
       wine32:i386 \
       wine64 \
       winetricks \
       xvfb \
 && rm -rf /var/lib/apt/lists/*

# ── Non-root user (matches VS Code devcontainer convention) ───────────────────
ARG USERNAME=ubuntu
ARG USER_UID=1000
ARG USER_GID=${USER_UID}

RUN if ! getent group ${USER_GID} >/dev/null; then groupadd --gid ${USER_GID} ${USERNAME}; fi \
 && if ! id -u ${USERNAME} >/dev/null 2>&1; then useradd --uid ${USER_UID} --gid ${USER_GID} -m ${USERNAME}; fi \
 && echo "${USERNAME} ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} \
 && chmod 0440 /etc/sudoers.d/${USERNAME}

# The Wine prefix must be owned by the user that runs wine
RUN mkdir -p ${WINEPREFIX} && chown ${USERNAME}:${USERNAME} ${WINEPREFIX}

USER ${USERNAME}

# ── Host Python tooling (hatch for running scripts) ───────────────────────────
RUN pipx install hatch
ENV PATH="/home/${USERNAME}/.local/bin:${PATH}"

# Wine prefix init and Python-for-Windows installation are done at container
# start via postCreateCommand (setup-wine.sh) because Wine requires an
# interactive session and cannot reliably run inside a Docker build layer.

WORKDIR /workspace
