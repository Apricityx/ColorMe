import re
from typing import Optional

from .colors import Color

_LEGACY_BOUNDARY = (1, 13)
_VERSION_PATTERN = re.compile(r'^(\d+)\.(\d+)')

VersionTuple = tuple[int, int]


def parse_version(version: Optional[str]) -> Optional[VersionTuple]:
    if not version:
        return None
    match = _VERSION_PATTERN.match(version)
    if match is None:
        return None
    return int(match.group(1)), int(match.group(2))


def uses_legacy_team_commands(version: Optional[str]) -> bool:
    parsed = parse_version(version)
    return parsed is not None and parsed < _LEGACY_BOUNDARY


def team_add_command(color: Color, version: Optional[str]) -> str:
    if uses_legacy_team_commands(version):
        return f'scoreboard teams add {color.value}'
    return f'team add {color.value}'


def team_remove_command(color: Color, version: Optional[str]) -> str:
    if uses_legacy_team_commands(version):
        return f'scoreboard teams remove {color.value}'
    return f'team remove {color.value}'


def team_color_command(color: Color, version: Optional[str]) -> str:
    if uses_legacy_team_commands(version):
        return f'scoreboard teams option {color.value} color {color.name}'
    return f'team modify {color.value} color {color.name}'


def team_join_command(color: Color, player: str, version: Optional[str]) -> str:
    if uses_legacy_team_commands(version):
        return f'scoreboard teams join {color.value} {player}'
    return f'team join {color.value} {player}'


def build_install_commands(version: Optional[str]) -> list[str]:
    commands = []
    for color in Color:
        commands.append(team_add_command(color, version))
        commands.append(team_color_command(color, version))
    return commands


def build_uninstall_commands(version: Optional[str]) -> list[str]:
    return [team_remove_command(color, version) for color in Color]
