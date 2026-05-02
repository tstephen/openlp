1. merge upstream/master to origin/master
2. merge origin/master to origin/int
3. merge any feat/fix branches desired to test into `int`
4. run `./scripts/build_source_release.py --version 3.1.8.dev255`
   Can this version tag be added to `int`?
5. copy to target machine and untar.
6. hatch run ?? something on target machine
7. open app and manual test

## Local build

Whilst the official project builds happen in Gitlab, it can be useful to do local development builds.

Use `./scripts/gitlab_ci_local.py` to run selected CI job logic locally without editing `.gitlab-ci.yml`.

Current recommended commands:

- `./scripts/gitlab_ci_local.py test-ubuntu`
- `./scripts/gitlab_ci_local.py build-source`
- `./scripts/gitlab_ci_local.py build-source --ci-commit-tag 3.2.0` (exercise tag path)
- `./scripts/gitlab_ci_local.py build-windows --mode linux-devcontainer --timeout-seconds 1800`
- `./scripts/gitlab_ci_local.py build-windows --mode host --ci-commit-tag 3.2.0`

Notes:

- `test-ubuntu` and `build-source` run in Docker against the same runner images used in GitLab CI.
- `build-windows --mode linux-devcontainer` runs from the current branch using `.devcontainer/windows-on-linux/devcontainer.json`.
- Linux-mode Windows build artifacts are written into `dist/` on the current branch.
- Add `--timeout-seconds 1800` (or another value) to fail fast instead of hanging forever.
- The helper prints stage markers (for example `==> [4/5] Generating Qt resources`) during Linux runs.

Preview commands without executing:

- add `--dry-run` to any command above.
