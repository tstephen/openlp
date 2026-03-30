#!/usr/bin/env python3
# -*- coding: utf-8 -*-

##########################################################################
# OpenLP - Open Source Lyrics Projection                                 #
# ---------------------------------------------------------------------- #
# Copyright (c) 2008 OpenLP Developers                                   #
# ---------------------------------------------------------------------- #
# This program is free software: you can redistribute it and/or modify   #
# it under the terms of the GNU General Public License as published by   #
# the Free Software Foundation, either version 3 of the License, or      #
# (at your option) any later version.                                    #
#                                                                        #
# This program is distributed in the hope that it will be useful,        #
# but WITHOUT ANY WARRANTY; without even the implied warranty of         #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the          #
# GNU General Public License for more details.                           #
#                                                                        #
# You should have received a copy of the GNU General Public License      #
# along with this program.  If not, see <https://www.gnu.org/licenses/>. #
##########################################################################
"""
Build a Windows one-folder bundle of OpenLP using Wine + PyInstaller.

Requirements (all provided by the devcontainer):
  - wine / wine64
  - Xvfb  (for a headless display; not needed if $DISPLAY is already set)
  - Python 3.12 installed inside the Wine prefix  (WINEPREFIX)
  - pyinstaller installed inside that Wine Python

Usage:
  hatch run build-windows
  -- or directly --
  python scripts/build_windows_wine.py [--clean]

Options:
  --clean   Remove build/ and dist/OpenLP/ before building.
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / 'scripts' / 'openlp_windows.spec'
DIST = ROOT / 'dist'
BUILD = ROOT / 'build' / 'wine'


# ── Helpers ───────────────────────────────────────────────────────────────────

def _require_host_cmd(cmd: str, hint: str) -> None:
    if shutil.which(cmd) is None:
        print(f'ERROR: {cmd!r} not found on the host. {hint}', file=sys.stderr)
        sys.exit(1)


def _run(args: list, env: dict | None = None, cwd: Path | None = None) -> None:
    display_args = ' '.join(str(a) for a in args)
    print(f'+ {display_args}')
    subprocess.run(args, check=True, env=env or os.environ.copy(), cwd=str(cwd or ROOT))


def _wine_env() -> dict:
    env = os.environ.copy()
    # Use an existing DISPLAY or fall back to :99 (Xvfb default in devcontainer)
    env.setdefault('DISPLAY', ':99')
    # Allow override via environment; devcontainer sets WINEPREFIX in Dockerfile
    env.setdefault('WINEPREFIX', str(Path.home() / '.wine'))
    return env


# ── Build steps ───────────────────────────────────────────────────────────────

def check_preflight() -> None:
    print('--- Pre-flight checks ---')
    _require_host_cmd('wine', 'Install wine: sudo apt install wine64')
    _require_host_cmd('Xvfb', 'Install xvfb: sudo apt install xvfb')

    env = _wine_env()
    result = subprocess.run(
        ['wine', 'python', '-m', 'PyInstaller', '--version'],
        capture_output=True,
        env=env,
    )
    if result.returncode != 0:
        print(
            'ERROR: PyInstaller not found inside the Wine Python.\n'
            '       Run:  DISPLAY=:99 wine pip install pyinstaller',
            file=sys.stderr,
        )
        sys.exit(1)
    version = result.stdout.decode().strip()
    print(f'    Wine PyInstaller version: {version}')


def generate_resources() -> None:
    resources_py = ROOT / 'openlp' / 'core' / 'resources.py'
    if resources_py.exists():
        print('--- Qt resources already present, skipping generation ---')
        return
    print('--- Generating Qt resources ---')
    _run(['sh', 'scripts/generate_resources.sh'])


def clean_previous(windows_dist: Path) -> None:
    for path in (windows_dist, BUILD):
        if path.exists():
            print(f'--- Removing {path} ---')
            shutil.rmtree(path)


def run_pyinstaller() -> None:
    print('--- Running PyInstaller via Wine ---')
    DIST.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    env = _wine_env()
    _run(
        [
            'wine', 'python', '-m', 'PyInstaller',
            '--distpath', str(DIST),
            '--workpath', str(BUILD),
            '--noconfirm',
            str(SPEC),
        ],
        env=env,
    )


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description='Build OpenLP Windows bundle via Wine.')
    parser.add_argument('--clean', action='store_true',
                        help='Remove previous build artefacts before building.')
    args = parser.parse_args()

    windows_dist = DIST / 'OpenLP'

    check_preflight()
    generate_resources()

    if args.clean:
        clean_previous(windows_dist)
    elif windows_dist.exists():
        print(f'--- dist/OpenLP exists; pass --clean to rebuild from scratch ---')

    run_pyinstaller()

    print(f'\nBuild complete.\nOutput: {windows_dist}')


if __name__ == '__main__':
    main()
