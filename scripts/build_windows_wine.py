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

Usage:
  hatch run build-windows
  python scripts/build_windows_wine.py [--clean]
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import argparse
import os
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent.parent
SPEC = ROOT / "scripts" / "openlp_windows.spec"
DIST = ROOT / "dist"
BUILD = ROOT / "build" / "wine"


def _require_host_cmd(cmd: str, hint: str) -> None:
    if shutil.which(cmd) is None:
        print(f"ERROR: {cmd!r} not found on the host. {hint}", file=sys.stderr)
        sys.exit(1)


def _run(args: list[str], env: dict[str, str] | None = None, cwd: Path | None = None) -> None:
    print("+ " + " ".join(str(arg) for arg in args))
    subprocess.run(args, check=True, env=env or os.environ.copy(), cwd=str(cwd or ROOT))


def _wine_env() -> dict[str, str]:
    env = os.environ.copy()
    env.setdefault("DISPLAY", ":99")
    env.setdefault("WINEPREFIX", str(Path.home() / ".wine"))
    return env


def check_preflight() -> None:
    print("--- Pre-flight checks ---")
    _require_host_cmd("wine", "Install wine: sudo apt install wine64")
    _require_host_cmd("Xvfb", "Install xvfb: sudo apt install xvfb")

    env = _wine_env()
    result = subprocess.run(
        ["wine", "python", "-m", "PyInstaller", "--version"],
        capture_output=True,
        env=env,
        check=False,
    )
    if result.returncode != 0:
        print(
            "ERROR: PyInstaller not found inside the Wine Python.\n"
            "       Run: DISPLAY=:99 wine pip install pyinstaller",
            file=sys.stderr,
        )
        sys.exit(1)
    print(f"    Wine PyInstaller version: {result.stdout.decode().strip()}")


def generate_resources() -> None:
    resources_py = ROOT / "openlp" / "core" / "resources.py"
    if resources_py.exists():
        print("--- Qt resources already present, skipping generation ---")
        return
    print("--- Generating Qt resources ---")
    _run(["sh", "scripts/generate_resources.sh"])


def clean_previous(windows_dist: Path) -> None:
    for path in (windows_dist, BUILD):
        if path.exists():
            print(f"--- Removing {path} ---")
            shutil.rmtree(path)


def run_pyinstaller() -> None:
    print("--- Running PyInstaller via Wine ---")
    DIST.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    _run(
        [
            "wine",
            "python",
            "-m",
            "PyInstaller",
            "--distpath",
            str(DIST),
            "--workpath",
            str(BUILD),
            "--noconfirm",
            str(SPEC),
        ],
        env=_wine_env(),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build OpenLP Windows bundle via Wine.")
    parser.add_argument("--clean", action="store_true", help="Remove previous build artefacts before building.")
    args = parser.parse_args()

    windows_dist = DIST / "OpenLP"

    check_preflight()
    generate_resources()

    if args.clean:
        clean_previous(windows_dist)
    elif windows_dist.exists():
        print("--- dist/OpenLP exists; pass --clean to rebuild from scratch ---")

    run_pyinstaller()
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    archive_name = DIST / f"OpenLP-{timestamp}"
    archive_path = shutil.make_archive(str(archive_name), "zip", root_dir=windows_dist)
    print(f"\nBuild complete.\nOutput: {windows_dist}\nArchive: {archive_path}")


if __name__ == "__main__":
    main()
