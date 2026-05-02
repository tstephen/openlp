#!/usr/bin/env bash
set -euo pipefail

pipx ensurepath

if [ -e "$HOME/.ssh/config" ] && [ ! -w "$HOME/.ssh/config" ]; then
    echo "==> ~/.ssh/config is read-only; skipping SSH alias bootstrap."
else
    mkdir -p "$HOME/.ssh"
    chmod 700 "$HOME/.ssh"
    if ! grep -q "^Host github-tstephen$" "$HOME/.ssh/config" 2>/dev/null; then
cat >> "$HOME/.ssh/config" <<'EOF'

Host github-tstephen
    HostName github.com
    User git
EOF
    fi
    chmod 600 "$HOME/.ssh/config"
fi

PYTHON_VERSION="${PYTHON_VERSION:-3.12.10}"
PYSIDE6_VERSION="${PYSIDE6_VERSION:-6.8.3}"
WINEPREFIX="${WINEPREFIX:-/opt/wine-openlp}"
export WINEPREFIX WINEARCH=win64

echo "==> Initialising Wine prefix at ${WINEPREFIX} ..."
xvfb-run -a wineboot --init
sleep 3

echo "==> Downloading Python ${PYTHON_VERSION} for Windows ..."
wget -q "https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-amd64.exe" \
     -O /tmp/python-installer.exe

echo "==> Installing Python ${PYTHON_VERSION} inside Wine ..."
xvfb-run -a wine /tmp/python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
sleep 8
rm /tmp/python-installer.exe

echo "==> Upgrading pip inside Wine ..."
xvfb-run -a wine python -m pip install --upgrade pip

echo "==> Installing Python packages inside Wine ..."
xvfb-run -a wine pip install --no-warn-script-location \
    alembic \
    beautifulsoup4 \
    chardet \
    flask \
    flask-cors \
    lxml \
    Mako \
    packaging \
    pillow \
    platformdirs \
    "PySide6==${PYSIDE6_VERSION}" \
    "PySide6_Essentials==${PYSIDE6_VERSION}" \
    "PySide6_Addons==${PYSIDE6_VERSION}" \
    "shiboken6==${PYSIDE6_VERSION}" \
    pyinstaller \
    pyodbc \
    pywin32 \
    qrcode \
    QtAwesome \
    requests \
    SQLAlchemy \
    waitress \
    websocket-client \
    websockets

echo "==> Wine Python setup complete."
