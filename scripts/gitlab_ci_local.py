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
Run selected GitLab CI jobs locally with high parity to .gitlab-ci.yml.

Supported jobs:
  - test-ubuntu
  - build-source
  - build-windows

Examples:
  scripts/gitlab_ci_local.py test-ubuntu
  scripts/gitlab_ci_local.py build-source
  scripts/gitlab_ci_local.py build-source --ci-commit-tag 3.2.0
  scripts/gitlab_ci_local.py build-windows --ci-commit-tag 3.2.0
"""

from __future__ import annotations

from pathlib import Path

import argparse
import platform
import shutil
import subprocess
import sys
import tempfile

DEFAULT_IMAGE_BASE = "registry.gitlab.com/openlp/runners"
WINDOWS_DEVCONTAINER_CONFIG = ".devcontainer/windows-on-linux/devcontainer.json"


def print_command(command: list[str]) -> None:
    """
    Print command in a shell-friendly style.
    """
    print("$", " ".join(command))


def run_command(command: list[str], cwd: Path, dry_run: bool = False, timeout_seconds: int = 0) -> None:
    """
    Run one command and stream stdout/stderr.
    """
    print_command(command)
    if dry_run:
        return
    try:
        subprocess.run(command, cwd=cwd, check=True, timeout=timeout_seconds if timeout_seconds > 0 else None)
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(f'Command timed out after {timeout_seconds} seconds: {" ".join(command)}') from error


def require_command(name: str) -> None:
    """
    Ensure the required command exists on PATH.
    """
    if shutil.which(name) is None:
        raise RuntimeError(f"Required command not found on PATH: {name}")


def get_repo_root() -> Path:
    """
    Resolve repository root based on this file's location.
    """
    return Path(__file__).resolve().parent.parent


def get_current_branch(repo_root: Path) -> str:
    """
    Return the current Git branch name.
    """
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=True,
    )
    branch = result.stdout.strip()
    if not branch:
        raise RuntimeError("Could not detect current branch.")
    return branch


def run_docker_job(
    repo_root: Path, image: str, script_text: str, ci_commit_tag: str | None, dry_run: bool, timeout_seconds: int
) -> None:
    """
    Run one CI-style bash script inside a Docker container.
    """
    require_command("docker")
    docker_script = """
if command -v git >/dev/null 2>&1; then
    git config --global --add safe.directory /work
fi
""".strip() + "\n" + script_text
    command = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{repo_root}:/work",
        "-w",
        "/work",
    ]
    if sys.stdout.isatty():
        command.append("-it")
    else:
        command.append("-i")
    if ci_commit_tag:
        command.extend(["-e", f"CI_COMMIT_TAG={ci_commit_tag}"])
    command.extend([image, "bash", "-lc", docker_script])
    run_command(command, cwd=repo_root, dry_run=dry_run, timeout_seconds=timeout_seconds)


def run_test_ubuntu(repo_root: Path, image_base: str, dry_run: bool, timeout_seconds: int) -> None:
    """
    Replicate .gitlab-ci.yml:test-ubuntu script in the ubuntu runner image.
    """
    script = """
echo '==> [1/5] Installing hatch with pipx'
pipx install hatch
echo '==> [2/5] Updating PATH with pipx ensurepath'
pipx ensurepath
echo '==> [3/5] Sourcing bashrc'
source ~/.bashrc
echo '==> [4/5] Generating Qt resources'
sh scripts/generate_resources.sh
echo '==> [5/5] Running pytest under xvfb'
Xvfb :99 -screen 0 1024x768x24 -nolisten tcp &
XVFB_PID=$!
trap 'kill "$XVFB_PID" 2>/dev/null || true' EXIT
export DISPLAY=:99
pytest --color=no --disable-warnings
PYTEST_EXIT=$?
echo '==> [5/5] Stopping xvfb'
kill "$XVFB_PID" 2>/dev/null || true
wait "$XVFB_PID" 2>/dev/null || true
exit "$PYTEST_EXIT"
""".strip()
    run_docker_job(
        repo_root, f"{image_base}/ubuntu", script, ci_commit_tag=None, dry_run=dry_run, timeout_seconds=timeout_seconds
    )


def run_build_source(
    repo_root: Path, image_base: str, ci_commit_tag: str | None, dry_run: bool, timeout_seconds: int
) -> None:
    """
    Replicate .gitlab-ci.yml:build-source script in the pypi runner image.
    """
    # Pre-create dist/ owned by the current user so Docker (running as root) never creates it as root.
    if not dry_run:
        (repo_root / "dist").mkdir(exist_ok=True)

    script = """
echo '==> [1/3] Preparing dist directory'
mkdir -p dist
if [ "$CI_COMMIT_TAG" != "" ]; then
    echo '==> [2/3] Using CI_COMMIT_TAG version'
    echo -n "$CI_COMMIT_TAG" > openlp/.version
    echo '==> [3/3] Creating source archive from tag'
    git archive -o "dist/OpenLP-${CI_COMMIT_TAG}.tar.gz" --add-file=openlp/.version "$CI_COMMIT_TAG" .
else
    echo '==> [2/3] Resolving version from hatch'
    pip install hatch
    git fetch --unshallow --tags || git fetch --tags
    VERSION=`hatch version`
    echo -n "$VERSION" > openlp/.version
    echo '==> [3/3] Creating source archive from HEAD'
    git archive -o "dist/OpenLP-${VERSION}.tar.gz" --add-file=openlp/.version HEAD .
fi
""".strip()
    run_docker_job(
        repo_root,
        f"{image_base}/pypi",
        script,
        ci_commit_tag=ci_commit_tag,
        dry_run=dry_run,
        timeout_seconds=timeout_seconds,
    )


def run_build_windows_host(
    repo_root: Path, ci_commit_tag: str, ci_project_namespace: str, dry_run: bool, timeout_seconds: int
) -> None:
    """
    Replicate .gitlab-ci.yml:build-windows on a Windows host.

    This follows the CI scripts from test-windows, .recompile_boot_loader_pyinstaller,
    and build-windows. It must run in an elevated PowerShell session.
    """
    if platform.system() != "Windows" and not dry_run:
        raise RuntimeError("build-windows must be run on Windows (PowerShell + Chocolatey + Windows features).")
    if not ci_commit_tag:
        raise RuntimeError("build-windows requires --ci-commit-tag because the CI job is tag-only.")

    powershell = shutil.which("pwsh") or shutil.which("powershell")
    if not powershell and not dry_run:
        raise RuntimeError("Could not find pwsh or powershell on PATH.")
    if not powershell and dry_run:
        powershell = "powershell"

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".ps1", delete=False) as temp_file:
        script_path = Path(temp_file.name)
        temp_file.write(rf"""
$ErrorActionPreference = 'Stop'
Set-Location '{repo_root}'

# --- test-windows ---
choco feature enable --name='allowGlobalConfirmation'
Import-Module $env:ChocolateyInstall\helpers\chocolateyProfile.psm1
Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression
refreshenv
Install-WindowsFeature Server-Media-Foundation

$zipFileName = 'requiredfiles.zip'
Invoke-WebRequest -OutFile "$env:Temp\$zipFileName" -Uri "https://get.openlp.org/win-sdk/$zipFileName"
Unblock-File -Path "$env:Temp\$zipFileName"
Expand-Archive -Path "$env:Temp\$zipFileName" -DestinationPath "$env:WinDir\System32"

uv sync --group test

$pyIcuVersion = '2.16.2'
$pythonVersion = '313'
$pyIcuPackageFileName = "PyICU-$pyIcuVersion-cp$pythonVersion-cp$pythonVersion-win_amd64.whl"
uv add "https://github.com/cgohlke/pyicu-build/releases/download/v$pyIcuVersion/$pyIcuPackageFileName"
uv run pytest --color=no --disable-warnings

# --- build-windows specific ---
choco install wixtoolset --ignore-dependencies
refreshenv

$zipFileName = 'PortableApps.zip'
Invoke-WebRequest -OutFile "$env:Temp\$zipFileName" -Uri "https://get.openlp.org/win-sdk/$zipFileName"
Set-Location '..'
Expand-Archive -Path "$env:Temp\$zipFileName" -DestinationPath .

# Recompile PyInstaller boot loader (CI .recompile_boot_loader_pyinstaller)
$pyInstallerVersion = '6.11.1'
$pyiZipFileName = "v$pyInstallerVersion.zip"
Invoke-WebRequest -OutFile "$env:Temp\$pyiZipFileName" \
    -Uri "https://github.com/pyinstaller/pyinstaller/archive/refs/tags/$pyiZipFileName"
Expand-Archive -Path "$env:Temp\$pyiZipFileName" -DestinationPath .
Set-Location ".\pyinstaller-$pyInstallerVersion\bootloader"
python ./waf all --target-arch=64bit
Set-Location '..'
pip install .
Set-Location '..'

# Download packaging archive used by CI
$PACKAGING_REPOSITORY_NAME = 'packaging'
$PACKAGING_BRANCH_NAME = 'master'
$PACKAGING_DIRECTORY_NAME = "$PACKAGING_REPOSITORY_NAME-$PACKAGING_BRANCH_NAME"
$PACKAGING_ZIP_FILE_NAME = "$PACKAGING_DIRECTORY_NAME.zip"
Invoke-WebRequest -OutFile "$env:Temp\$PACKAGING_ZIP_FILE_NAME" \
    -Uri "https://gitlab.com/{ci_project_namespace}/$PACKAGING_REPOSITORY_NAME/-/archive/$PACKAGING_BRANCH_NAME/$PACKAGING_ZIP_FILE_NAME"  # noqa: E501
Expand-Archive -Path "$env:Temp\$PACKAGING_ZIP_FILE_NAME" -DestinationPath .
Set-Location $PACKAGING_DIRECTORY_NAME

echo -n '{ci_commit_tag}' > openlp/.version
python builders/windows-builder.py --release '{ci_commit_tag}' \
    --skip-update --config windows/config-gitlab.ini --branch '{repo_root}' --portable
""".strip())

    command = [powershell, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script_path)]
    try:
        run_command(command, cwd=repo_root, dry_run=dry_run, timeout_seconds=timeout_seconds)
    finally:
        if script_path.exists():
            script_path.unlink()


def run_build_windows_linux_devcontainer(
    repo_root: Path,
    dry_run: bool,
    timeout_seconds: int,
) -> None:
    """
    Run the Linux devcontainer-based Windows build workflow from the current branch.
    """
    require_command("devcontainer")

    workspace_folder = repo_root

    config_path = workspace_folder / WINDOWS_DEVCONTAINER_CONFIG
    if not dry_run and not config_path.exists():
        raise RuntimeError(f"Devcontainer config not found: {config_path}")

    run_command(
        [
            "devcontainer",
            "up",
            "--workspace-folder",
            str(workspace_folder),
            "--config",
            str(config_path),
            "--remove-existing-container",
            "--mount-git-worktree-common-dir",
            "--default-user-env-probe",
            "none",
        ],
        cwd=repo_root,
        dry_run=dry_run,
        timeout_seconds=timeout_seconds,
    )
    run_command(
        [
            "devcontainer",
            "exec",
            "--workspace-folder",
            str(workspace_folder),
            "--config",
            str(config_path),
            "bash",
            "-lc",
            "hatch -e windows run build-windows-clean",
        ],
        cwd=repo_root,
        dry_run=dry_run,
        timeout_seconds=timeout_seconds,
    )

    if dry_run:
        source_dist = workspace_folder / "dist"
        destination_dist = repo_root / "dist"
        if source_dist.resolve() == destination_dist.resolve():
            print(f"Artifacts will be produced in place: {source_dist}")
        else:
            print(f"Would copy artifacts from {source_dist} to {destination_dist}")
        return

    destination_dist = repo_root / "dist"
    destination_dist.mkdir(parents=True, exist_ok=True)
    artifact_paths = sorted((workspace_folder / "dist").glob("OpenLP-*.zip"))
    if not artifact_paths:
        print("No OpenLP-*.zip artifacts found in devcontainer worktree dist/.")
        return
    for artifact_path in artifact_paths:
        destination_path = destination_dist / artifact_path.name
        if artifact_path.resolve() == destination_path.resolve():
            print(f"Artifact available: {artifact_path}")
            continue
        shutil.copy2(artifact_path, destination_path)
        print(f"Copied artifact: {artifact_path} -> {destination_path}")


def parse_args() -> argparse.Namespace:
    """
    Parse command line options.
    """
    parser = argparse.ArgumentParser(description="Run selected GitLab CI jobs locally.")
    subparsers = parser.add_subparsers(dest="job", required=True)

    for linux_job in ("test-ubuntu", "build-source"):
        linux_parser = subparsers.add_parser(linux_job)
        linux_parser.add_argument(
            "--image-base",
            default=DEFAULT_IMAGE_BASE,
            help="Container image base (default: registry.gitlab.com/openlp/runners)",
        )
        linux_parser.add_argument(
            "--timeout-seconds",
            type=int,
            default=3600,
            help="Maximum run time before aborting (default: 3600, 0 disables timeout)",
        )
        linux_parser.add_argument("--dry-run", action="store_true", help="Print command(s) without executing")
    build_source_parser = subparsers.choices["build-source"]
    build_source_parser.add_argument(
        "--ci-commit-tag", default="", help="Set CI_COMMIT_TAG to exercise tag branch behavior"
    )

    windows_parser = subparsers.add_parser("build-windows")
    windows_parser.add_argument(
        "--mode",
        choices=("host", "linux-devcontainer"),
        default="host",
        help="host (closest to GitLab CI) or linux-devcontainer (current-branch Linux workflow)",
    )
    windows_parser.add_argument(
        "--ci-commit-tag", default="", help="Tag to use for CI_COMMIT_TAG-equivalent release build"
    )
    windows_parser.add_argument(
        "--ci-project-namespace", default="openlp", help="GitLab namespace for packaging archive URL (default: openlp)"
    )
    windows_parser.add_argument(
        "--timeout-seconds", type=int, default=0, help="Maximum run time before aborting (default: 0, disabled)"
    )
    windows_parser.add_argument("--dry-run", action="store_true", help="Print command without executing")

    return parser.parse_args()


def main() -> int:
    """
    Script entrypoint.
    """
    args = parse_args()
    repo_root = get_repo_root()

    if args.job == "test-ubuntu":
        run_test_ubuntu(
            repo_root=repo_root, image_base=args.image_base, dry_run=args.dry_run, timeout_seconds=args.timeout_seconds
        )
    elif args.job == "build-source":
        run_build_source(
            repo_root=repo_root,
            image_base=args.image_base,
            ci_commit_tag=args.ci_commit_tag or None,
            dry_run=args.dry_run,
            timeout_seconds=args.timeout_seconds,
        )
    elif args.job == "build-windows":
        if args.mode == "host":
            run_build_windows_host(
                repo_root=repo_root,
                ci_commit_tag=args.ci_commit_tag,
                ci_project_namespace=args.ci_project_namespace,
                dry_run=args.dry_run,
                timeout_seconds=args.timeout_seconds,
            )
        else:
            run_build_windows_linux_devcontainer(
                repo_root=repo_root,
                dry_run=args.dry_run,
                timeout_seconds=args.timeout_seconds,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
