# Contributing to ColorMe

Thanks for taking the time to improve ColorMe. Keep changes small, predictable and
focused on the vanilla team behavior.

## Project layout

```
color_me/
  __init__.py        command registration and command handlers
  colors.py          the single source of truth for colors and team names
  team_commands.py   version-aware vanilla team command builders
tests/
  helpers.py         fake MCDR server and command sources
  test_*.py          unit tests and MCDR API tests
  e2e/               end-to-end tests against a real Minecraft server
```

## Development setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

## Running the tests

Unit tests and MCDR API tests (fast, no network, no server):

```bash
pytest -m "not e2e"
```

## End-to-end tests

The E2E suite downloads a vanilla server jar, packs the plugin with
`mcdreforged pack`, runs it under a real MCDReforged instance, drives MCDR console
commands, verifies team state through RCON, and uses two [mineflayer](https://github.com/PrismarineJS/mineflayer)
bots to check that the rendered name color is synchronized to both clients.

Requirements:

- A Java runtime matching the tested Minecraft version
  (1.12.2 needs Java 8, 1.20.4 needs Java 17+). Use `JAVA_BIN` to point at a specific
  `java` executable.
- Node.js and npm for the bot tests.
- Network access on the first run to download the server jar (it is cached in
  `tests/e2e/.cache/`).

```bash
cd tests/e2e/js && npm install && cd ../../..
MCDR_E2E=1 MC_VERSION=1.20.4 pytest tests/e2e
MCDR_E2E=1 MC_VERSION=1.12.2 pytest tests/e2e
```

Useful environment variables:

- `MCDR_E2E=1` enables the suite.
- `MC_VERSION` selects the vanilla server version (default `1.12.2`).
- `JAVA_BIN` overrides the `java` executable.
- `MCDR_E2E_KEEP=1` keeps the generated MCDR working directory in `tests/e2e/.run/`
  for debugging.

## Design rules

- Colors and team names are defined exactly once, in `color_me/colors.py`.
- ColorMe is a thin wrapper around vanilla teams. Do not add client-side rendering or a
  second team/state store.
- Version differences in team command syntax belong in `color_me/team_commands.py`.
- `install`/`uninstall` must be safe to run repeatedly and must never touch teams that
  do not use ColorMe's `__` prefix.
- Player-only commands must reject the console command source.
- Keep error messages useful and keep the vanilla server as the source of truth for the
  team state. Broadcasting a chat message is not proof that the team state changed.

## Pull requests

- Run `pytest -m "not e2e"` before opening a PR; CI runs it as well.
- If your change affects team synchronization, run the E2E suite with two clients.
- Describe compatibility implications, especially for 1.12.x vs 1.13+ and for other
  plugins that use vanilla teams.
- Avoid unrelated refactors.

## CI

- `ci.yml` runs the unit/API tests on Python 3.10 and 3.13 and builds a `.mcdr`
  artifact on every push and pull request.
- `e2e.yml` runs the Minecraft end-to-end suite for 1.12.2 and 1.20.4 on pushes to
  `master`, weekly and on manual dispatch.
- `release.yml` verifies the tag, runs the tests and publishes the release.

## Release process

1. Update `version` in `mcdreforged.plugin.json` following [semantic versioning](https://semver.org/).
2. Update the readme/introductions if user-visible behavior changed.
3. Run `pytest -m "not e2e"` and, ideally, the E2E suite.
4. Commit the changes.
5. Create and push a tag `vX.Y.Z` that matches the metadata version exactly:

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

6. The release workflow checks the version, runs the unit tests, packs
   `ColorMe-vX.Y.Z.mcdr` and creates a GitHub release with generated notes and the
   packed plugin attached.

## Dependencies

Runtime dependencies must stay minimal: only MCDReforged itself. `requirements.txt` is
packed into the plugin and installed by MCDReforged. Test-only dependencies (pytest,
Node.js/mineflayer) must never be required at runtime.
