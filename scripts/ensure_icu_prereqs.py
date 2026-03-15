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
Ensure system prerequisites required to build PyICU are present on Linux.

PyICU does not publish wheels on PyPI, therefore pip builds it from source and
requires ICU development files plus pkg-config metadata.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys


def _run(command: list[str]) -> int:
    """Run a command and return the exit code."""
    print(f"[openlp] Running: {' '.join(command)}")
    result = subprocess.run(command, check=False)
    return result.returncode


def _has_icu_metadata() -> bool:
    """Return True if PyICU build metadata can be discovered."""
    if shutil.which('icu-config'):
        if _run(['icu-config', '--version']) == 0:
            return True
    if shutil.which('pkg-config'):
        if _run(['pkg-config', '--exists', 'icu-i18n']) == 0:
            return True
    return False


def _linux_install_command() -> list[str] | None:
    """Return a package-manager command for ICU build prerequisites."""
    if shutil.which('apt-get'):
        return ['apt-get', 'install', '-y', 'pkg-config', 'libicu-dev']
    if shutil.which('dnf'):
        return ['dnf', 'install', '-y', 'pkgconf-pkg-config', 'libicu-devel']
    if shutil.which('yum'):
        return ['yum', 'install', '-y', 'pkgconf-pkg-config', 'libicu-devel']
    if shutil.which('pacman'):
        return ['pacman', '-Sy', '--noconfirm', 'pkgconf', 'icu']
    if shutil.which('zypper'):
        return ['zypper', '--non-interactive', 'install', 'pkg-config', 'libicu-devel']
    if shutil.which('apk'):
        return ['apk', 'add', '--no-cache', 'pkgconf', 'icu-dev']
    return None


def _print_manual_help(command: list[str] | None) -> None:
    """Print a concise hint when auto-installation cannot run."""
    print('[openlp] ERROR: Missing ICU development prerequisites required to build PyICU.')
    print('[openlp] Install ICU development files and pkg-config, then retry hatch.')
    if command:
        if os.geteuid() != 0 and shutil.which('sudo'):
            command = ['sudo'] + command
        print(f"[openlp] Suggested command: {' '.join(command)}")


def _maybe_prefix_with_sudo(command: list[str]) -> list[str]:
    """Use sudo for package installation when not running as root."""
    if os.geteuid() == 0:
        return command
    if shutil.which('sudo'):
        # Prompt for sudo password when attached to an interactive terminal.
        if sys.stdin.isatty() and sys.stdout.isatty():
            return ['sudo'] + command
        # Fail fast in non-interactive contexts.
        return ['sudo', '-n'] + command
    return []


def main() -> int:
    """Entry point."""
    if not sys.platform.startswith('linux'):
        return 0

    if _has_icu_metadata():
        print('[openlp] ICU build prerequisites detected.')
        return 0

    install_command = _linux_install_command()
    if not install_command:
        _print_manual_help(None)
        return 1

    full_command = _maybe_prefix_with_sudo(install_command)
    if not full_command:
        _print_manual_help(install_command)
        return 1

    print('[openlp] ICU metadata not found. Attempting automatic package installation...')
    if _run(full_command) != 0:
        _print_manual_help(install_command)
        return 1

    if _has_icu_metadata():
        print('[openlp] ICU build prerequisites installed successfully.')
        return 0

    _print_manual_help(install_command)
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
