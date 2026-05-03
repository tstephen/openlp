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
Build a release-style source tarball for the current checkout.
"""

from __future__ import annotations

import argparse
import subprocess
import tarfile
import tempfile
from pathlib import Path


def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("ref", nargs="?", default="HEAD", help="Git ref to archive, defaults to HEAD")
    parser.add_argument("--version", help="Version string to write to openlp/.version")
    parser.add_argument("--output-dir", default="dist", help="Output directory for the tarball, defaults to dist")
    return parser.parse_args()


def get_repo_root() -> Path:
    """
    Return the repository root based on this script's location.
    """
    return Path(__file__).resolve().parent.parent


def get_version(repo_root: Path, ref: str, requested_version: str | None) -> str:
    """
    Determine the version to embed in the source release.
    """
    if requested_version:
        return requested_version
    if ref != "HEAD":
        return ref
    result = subprocess.run(["hatch", "version"], cwd=repo_root, capture_output=True, check=True, text=True)
    return result.stdout.strip()


def build_archive(repo_root: Path, ref: str, version: str, output_dir: Path) -> Path:
    """
    Build the source tarball without mutating tracked files.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"OpenLP-{version}.tar.gz"
    with tempfile.TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        archive_path = temp_dir / "source.tar"
        source_dir = temp_dir / "source"
        subprocess.run(["git", "archive", "--format=tar", "-o", str(archive_path), ref], cwd=repo_root, check=True)
        source_dir.mkdir()
        with tarfile.open(archive_path, "r") as source_archive:
            source_archive.extractall(source_dir, filter="data")
        pyproject_file = source_dir / "pyproject.toml"
        pyproject_text = pyproject_file.read_text(encoding="utf-8")
        pyproject_text = pyproject_text.replace('dynamic = ["version"]', f'version = "{version}"', 1)
        pyproject_file.write_text(pyproject_text, encoding="utf-8")
        version_file = source_dir / "openlp" / ".version"
        version_file.parent.mkdir(parents=True, exist_ok=True)
        version_file.write_text(version, encoding="utf-8")
        with tarfile.open(output_path, "w:gz") as release_archive:
            for path in sorted(source_dir.rglob("*")):
                release_archive.add(path, arcname=path.relative_to(source_dir))
    return output_path


def main() -> int:
    """
    The main entrypoint.
    """
    args = parse_args()
    repo_root = get_repo_root()
    output_dir = repo_root / args.output_dir
    version = get_version(repo_root, args.ref, args.version)
    output_path = build_archive(repo_root, args.ref, version, output_dir)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
