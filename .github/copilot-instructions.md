# Copilot Instructions for OpenLP

## Build, test, and lint commands

```bash
# Create the default and test environments
hatch env create
hatch env create test

# JavaScript dependencies for the display tests/lint
pnpm install

# Regenerate Qt resources after changing resources/images/** or resources/images/openlp-2.qrc
sh scripts/generate_resources.sh

# Run the desktop app locally
hatch run run_openlp

# Python lint
hatch run test:flake8

# Python tests
hatch run test:run

# Run one Python test file or one test
hatch run test:run_selected tests/openlp_core/test_app.py
hatch run test:run_selected tests/openlp_core/test_app.py::test_main

# Linux headless test command used in CI
QT_QPA_PLATFORM=offscreen xvfb-run -s '-screen 0 1024x768x24' hatch run test:ci

# JavaScript lint and browser tests for the display HTML/JS
pnpm lint
pnpm test --browsers ChromiumHeadlessCI

# Python package build
hatch build
```

## High-level architecture

- `openlp/__main__.py` starts `openlp.core.app.main()`. `OpenLP.run()` creates screens, runs first-time setup, calls `openlp.core.loader.loader()`, constructs `MainWindow`, and then drives startup through `Registry` bootstrap events.
- `loader()` brings up the core singleton-style services in order: `State`, `MediaController`, `PluginManager`, `Renderer`, `PreviewController`, and `LiveController`.
- The app is wired through `Registry` and `State`, not explicit dependency injection. Services register themselves with `Registry().register(...)`, cross-cutting actions use named events via `Registry().register_function(...)` / `Registry().execute(...)`, and plugin availability is tracked through `State`.
- `MainWindow` is the desktop shell: it creates the dock managers, service/theme/projector panes, and starts the HTTP remote server (`openlp/core/api/http/server.py`) plus websocket server (`openlp/core/api/websockets.py`).
- Rendering is split across Python and browser code. `ServiceItem` builds slide data, `Renderer` formats themed HTML/text, and `DisplayWindow` hosts `openlp/core/display/html/display.html` in a Qt WebEngine view over the custom `openlp://display` scheme.
- Plugin features usually span three layers: the plugin class in `openlp/plugins/*/*plugin.py`, the media/settings/forms code under that plugin's `lib/` and `forms/`, and an optional plugin database managed through `openlp.core.db.manager.DBManager`.

## Key conventions

- New long-lived UI/core services usually inherit `RegistryBase` and/or `RegistryProperties` so they self-register and participate in `bootstrap_initialise`, `bootstrap_post_set_up`, and `bootstrap_completion`.
- Plugin classes conventionally call `State().add_service(...)`, then `State().update_pre_conditions(...)`, and expose menu/media/settings integration by overriding the base `Plugin` hooks instead of wiring themselves directly into the main window.
- When changing slide rendering or chord handling, check both Python and browser code. `openlp/core/display/render.py` contains logic that is intentionally mirrored in the display HTML/JS stack and covered by `tests/js/test_*.js`.
- Resource changes are generated, not hand-edited. If you touch `resources/images/**` or `resources/images/openlp-2.qrc`, regenerate `openlp/core/resources.py` with `sh scripts/generate_resources.sh`.
- Tests mirror the runtime layout: core tests live under `tests/openlp_core/**`, plugin tests under `tests/openlp_plugins/**`, and shared isolation fixtures for `Registry`, `State`, `Settings`, and `OpenLP` live in `tests/conftest.py`.
- Keep the existing Python file prologues intact when editing older modules: most files start with the UTF-8 coding line, the GPL banner block, and then a module docstring.
