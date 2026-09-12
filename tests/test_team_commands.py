import pytest

from color_me.colors import Color
from color_me.team_commands import (
    build_install_commands,
    build_uninstall_commands,
    parse_version,
    team_add_command,
    team_color_command,
    team_join_command,
    team_remove_command,
    uses_legacy_team_commands,
)


@pytest.mark.parametrize(
    ('version', 'expected'),
    [
        (None, None),
        ('', None),
        ('unknown', None),
        ('1.12.2', (1, 12)),
        ('1.12', (1, 12)),
        ('1.13', (1, 13)),
        ('1.13.2', (1, 13)),
        ('1.16.5', (1, 16)),
        ('1.20.4', (1, 20)),
        ('1.17 Release Candidate 1', (1, 17)),
        ('1.13-pre1', (1, 13)),
    ],
)
def test_parse_version(version, expected):
    assert parse_version(version) == expected


@pytest.mark.parametrize(
    ('version', 'legacy'),
    [
        (None, False),
        ('unknown', False),
        ('1.11.2', True),
        ('1.12', True),
        ('1.12.2', True),
        ('1.13', False),
        ('1.13.2', False),
        ('1.20.4', False),
    ],
)
def test_uses_legacy_team_commands(version, legacy):
    assert uses_legacy_team_commands(version) is legacy


def test_modern_commands():
    assert team_add_command(Color.red, '1.20.4') == 'team add __red'
    assert team_remove_command(Color.red, '1.20.4') == 'team remove __red'
    assert team_color_command(Color.dark_aqua, '1.20.4') == 'team modify __dark_aqua color dark_aqua'
    assert team_join_command(Color.red, 'Steve', '1.20.4') == 'team join __red Steve'


def test_legacy_commands():
    assert team_add_command(Color.red, '1.12.2') == 'scoreboard teams add __red'
    assert team_remove_command(Color.red, '1.12.2') == 'scoreboard teams remove __red'
    assert team_color_command(Color.dark_aqua, '1.12.2') == 'scoreboard teams option __dark_aqua color dark_aqua'
    assert team_join_command(Color.red, 'Steve', '1.12.2') == 'scoreboard teams join __red Steve'


def test_build_install_commands_creates_and_colors_every_team():
    commands = build_install_commands('1.20.4')
    expected = []
    for color in Color:
        expected.append(f'team add {color.value}')
        expected.append(f'team modify {color.value} color {color.name}')
    assert commands == expected


def test_build_install_commands_legacy():
    commands = build_install_commands('1.12.2')
    assert len(commands) == len(Color) * 2
    assert 'scoreboard teams add __white' in commands
    assert 'scoreboard teams option __white color white' in commands


def test_build_uninstall_commands_removes_every_team():
    commands = build_uninstall_commands('1.20.4')
    assert commands == [f'team remove {color.value}' for color in Color]
