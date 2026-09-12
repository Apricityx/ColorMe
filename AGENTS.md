# AGENTS.md

## Project

ColorMe is an MCDReforged plugin for Minecraft Java Edition.

Its purpose is to provide a simple interface for managing player name colors
through Minecraft's native scoreboard Team system.

Keep the project small, predictable, and easy to maintain.

## Runtime

- Python 3.10+
- MCDReforged 2.x.x
- Minecraft Java Edition 1.12.x (uses `/scoreboard teams`) and 1.13+ (uses `/team`).
  The command syntax is selected from the server version reported by MCDReforged;
  unknown versions fall back to the modern `/team` syntax.
- The plugin runs server-side through MCDReforged.
- Minecraft Team behavior should be implemented through vanilla server commands
  rather than client-side modifications.

Do not assume APIs from other MCDReforged versions without checking the
installed/documented API.

## Core Design

The plugin should remain a thin wrapper around Minecraft's native Team system.

Expected flow:

    ColorMe command
        -> validate input
        -> execute vanilla Team command
        -> Minecraft server manages Team state
        -> clients receive the normal Team synchronization

Do not implement a custom player-name rendering system.

Do not maintain a second, redundant Team/state system unless there is a clear
technical reason.

## Source Layout

    color_me/__init__.py        command registration and command handlers
    color_me/colors.py          supported colors and owned team names
    color_me/team_commands.py   version-aware vanilla team command builders
    color_me/i18n.py            English and Chinese user-facing messages

Supported colors must be defined only in `color_me/colors.py`. Differences
between 1.12.x and 1.13+ team command syntax belong in
`color_me/team_commands.py`.

## Team Naming

ColorMe owns its own Team names.

Current naming convention:

    __red
    __blue
    __green
    ...

Do not modify or remove Teams that are not owned by ColorMe.

Avoid changing the Team naming scheme without considering compatibility with
existing installations.

## Commands

Current command namespace:

    !!color

Supported operations include:

    !!color install
    !!color uninstall
    !!color list
    !!color <color>

Commands must:

- validate arguments
- provide useful error messages
- behave safely when executed repeatedly
- reject player-only commands when executed from console
- avoid crashing the MCDR process

`install` and `uninstall` require MCDReforged permission level 2 (helper) or higher.
`!!color <color>` is player-only. Change this behavior only deliberately.

All user-facing messages must be defined in `color_me/i18n.py` and rendered with
`tr(source, key, **kwargs)`; never hardcode a message in a handler. `en_us` and
`zh_cn` must always define the same keys and placeholders. Unknown languages fall
back to English, `zh_*` languages fall back to Chinese.

## Code Style

- Follow normal Python style and readability.
- Use type annotations where they improve clarity.
- Prefer small functions with one clear responsibility.
- Avoid unnecessary abstractions.
- Avoid unnecessary classes or frameworks.
- Do not introduce dependencies for functionality that can be implemented
  with the Python standard library or MCDReforged API.
- Keep command strings easy to inspect.
- Avoid duplicated lists of supported colors.

Use the existing project structure unless there is a concrete reason to change it.

## Correctness

When modifying color handling, verify:

1. Every advertised color actually exists.
2. Every defined color can be selected.
3. Team creation uses the correct Minecraft color names.
4. Team membership is changed on the server.
5. Changing color correctly moves the player between ColorMe Teams.
6. Existing unrelated Teams are not modified.
7. Repeated installation/uninstallation does not leave the plugin in an
   obviously broken state.
8. Console and player command sources are handled correctly.

Do not assume that broadcasting a chat message means the Team state was
synchronized to clients.

## Compatibility

ColorMe relies on vanilla Minecraft Team commands.

When debugging visibility or synchronization problems, distinguish between:

1. server-side Team state,
2. command execution,
3. network synchronization,
4. client-side rendering.

Do not "fix" a synchronization problem by adding client-side state unless
the actual cause has been established.

Pay particular attention to protocol translation environments such as
ViaVersion/ViaFabric.

## Testing

Automated tests live in `tests/`:

- `pytest -m "not e2e"` runs the unit tests and the MCDR API tests. No network
  or Minecraft server is required.
- `MCDR_E2E=1 MC_VERSION=<version> pytest tests/e2e` runs the end-to-end tests
  against a real vanilla server, MCDReforged, RCON and mineflayer clients.
  Set `MCDR_E2E_LANGUAGE=en_us` or `zh_cn` to test both message languages.
  See CONTRIBUTING.md for the prerequisites.

Before considering a change complete:

- Check the plugin loads successfully in MCDReforged.
- Check all registered commands.
- Test valid and invalid colors.
- Test player and console command execution.
- Test repeated `install` and `uninstall`.
- Test two players changing colors.
- Verify that both players see the expected colors.
- Test with the Minecraft versions actually supported by the server setup.

For synchronization-related changes, testing with two separate clients is
required; checking only the executing player's client is insufficient.

## Dependencies

Keep runtime dependencies minimal.

Do not add a dependency unless it is actually required.

If the MCDReforged API already provides the required functionality, use it.

## Changes

Before modifying behavior:

1. Inspect the existing implementation.
2. Identify the actual cause of the problem.
3. Make the smallest reasonable change.
4. Preserve existing working behavior.
5. Explain compatibility implications when relevant.

Do not perform unrelated refactors.

Do not rewrite the plugin merely to satisfy personal style preferences.

## Review Rules

When reviewing code, prioritize issues in this order:

1. Functional bugs
2. Minecraft/MCDReforged API misuse
3. Data/state corruption
4. Compatibility problems
5. Security problems
6. Error handling
7. Maintainability
8. Style

Do not report purely subjective style preferences as bugs.

Every reported issue should include:

- location
- severity
- why it is a problem
- concrete reproduction scenario when possible
- recommended fix

Avoid speculative issues unless clearly marked as such.

## Scope

This is a small plugin.

Prefer:

    simple > clever
    explicit > abstract
    native Minecraft behavior > custom implementation
    minimal changes > large refactors
    verified behavior > assumptions