[[中文]](./introduction/introduction-zh_cn.md) | [English]

# ColorMe

A small [MCDReforged](https://github.com/MCDReforged/MCDReforged) plugin that lets players
choose their own name color. It is a thin wrapper around Minecraft's vanilla scoreboard
team system: ColorMe creates 16 teams, one for each chat color, and players change color
by joining a team.

## Features

- Players change their own name color with `!!color <color>`
- All 16 vanilla Minecraft chat colors
- Works on Minecraft **1.12.x** (`/scoreboard teams`) and **1.13+** (`/team`)
- The Minecraft server manages all team state; ColorMe implements no custom rendering
  and no second state store
- ColorMe only creates, modifies and removes its own `__`-prefixed teams

## Requirements

- MCDReforged 2.x
- Python 3.10+
- Minecraft Java Edition 1.12.x or 1.13+ (the command syntax is selected automatically
  from the version reported by the server)

## Installation

1. Put `ColorMe-vX.Y.Z.mcdr` into MCDReforged's `plugins/` folder.
2. Restart or reload MCDReforged.
3. Create the teams once:

```
!!color install
```

## Commands

| Command | Available to | Permission | Description |
| --- | --- | --- | --- |
| `!!color <color>` | players | everyone | join the team of the given color |
| `!!color list` | players and console | everyone | list the available colors |
| `!!color install` | players and console | helper (level 2) | create the ColorMe teams and set their colors |
| `!!color uninstall` | players and console | helper (level 2) | remove the ColorMe teams |

Available colors:

```
red, blue, green, yellow, light_purple, aqua, white, black, gray, gold,
dark_red, dark_blue, dark_green, dark_aqua, dark_purple, dark_gray
```

## How it works

1. `!!color install` creates the teams `__red`, `__blue`, ... and sets each team color
   with the vanilla team color option.
2. `!!color red` makes the executing player join the `__red` team.
3. The vanilla server synchronizes team membership to clients, and the client renders
   the player name with the team color. No client-side modification is involved.

On Minecraft 1.12.x the plugin uses `/scoreboard teams add|remove|join|option`; on
1.13+ it uses `/team add|remove|join|modify`.

## Notes and limitations

- A player can only be in one team at a time (vanilla behavior). If your server uses
  teams for other purposes (prefixes, suffixes, permissions, ...), joining a ColorMe
  team will remove the player from their previous team. Make sure this does not break
  your setup.
- ColorMe never touches teams that do not use its `__` prefix. To avoid conflicts,
  do not create your own teams named `__<color>`.
- `!!color install` is safe to run repeatedly. If the teams already exist, the vanilla
  server may log "already exists" messages, but the colors are still applied.
- `!!color uninstall` only removes ColorMe's teams and is safe to run repeatedly.
- Colored names require the client to support team colors; protocol translation layers
  such as ViaVersion/ViaFabric do not change the team data itself.

## Development

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the development setup, the test suites and
the release process.

## License

ColorMe is licensed under the GNU General Public License v3.0, see [LICENSE](./LICENSE).
