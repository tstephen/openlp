# Ubuntu 24.04 source-release workflow

This devcontainer is for validating the same **source tar.gz** release style that OpenLP publishes on GitLab, while keeping the host machine free of most project-specific tooling.

## What it covers

- Ubuntu 24.04 native packages needed for Hatch-based setup and Qt runtime dependencies
- a repeatable bootstrap step for Hatch environments and `pnpm`
- building a local source tarball from the current checkout
- testing and running the extracted source release on Ubuntu 24.04

## Prerequisites

- Docker
- either:
  - VS Code with the Dev Containers extension, or
  - plain Docker CLI

## Open in a devcontainer

1. Open the repository in VS Code.
2. Run **Dev Containers: Open Folder in Container...**
3. Select `.devcontainer/ubuntu-24.04/devcontainer.json`

The post-create step installs Hatch, enables `pnpm`, creates the default and test Hatch environments, and installs the JavaScript dependencies.

## Use the container directly with Docker

Build the image:

```bash
docker build -f .devcontainer/ubuntu-24.04/Dockerfile -t openlp-ubuntu24 .
```

Start a shell in the repository workspace:

```bash
docker run --rm -it \
  -v "$PWD":/workspaces/openlp \
  -w /workspaces/openlp \
  openlp-ubuntu24 \
  bash
```

Bootstrap the toolchain inside the container:

```bash
bash ./.devcontainer/ubuntu-24.04/bootstrap.sh
```

## Build the release-style source tarball

From the repository root:

```bash
python3 scripts/build_source_release.py
```

This writes a tarball into `dist/` using the current `HEAD` contents plus an embedded version in both `openlp/.version` and `pyproject.toml`, so the extracted release can bootstrap outside a git checkout.

## Validate the tarball on Ubuntu 24.04

Build the tarball first, then extract it into a clean directory:

```bash
VERSION="$(hatch version)"
RELEASE_DIR="$(mktemp -d)"
tar -xzf "dist/OpenLP-${VERSION}.tar.gz" -C "$RELEASE_DIR"
cd "$RELEASE_DIR"
```

Create the environments and install JavaScript dependencies from the extracted release:

```bash
hatch env create
hatch env create test
pnpm install
```

Run the application:

```bash
hatch run run_openlp
```

Run the headless Python test suite:

```bash
QT_QPA_PLATFORM=offscreen xvfb-run -s '-screen 0 1024x768x24' hatch run test:ci
```

Run a single smoke test:

```bash
QT_QPA_PLATFORM=offscreen xvfb-run -s '-screen 0 1024x768x24' \
  hatch run test:run_selected tests/openlp_core/test_app.py::test_main
```

Run the display JavaScript tests:

```bash
pnpm test --browsers ChromiumHeadlessCI
```

## Notes

- `scripts/build_source_release.py` uses `hatch version`, so if your clone is shallow, fetch tags first.
- If you want to start the GUI from plain Docker rather than a Dev Container, you will need to add your own X11 or Wayland forwarding.
- The source tarball is intended to validate the published source-release workflow, not to produce a native `.deb`.
