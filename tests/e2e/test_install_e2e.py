import pytest

from color_me.colors import Color

pytestmark = pytest.mark.e2e

EXPECTED_TEAMS = {color.value for color in Color}


def test_install_creates_all_colored_teams(e2e):
    e2e.send_command('!!color install')
    assert e2e.wait_for_team_count(len(EXPECTED_TEAMS)) == EXPECTED_TEAMS


def test_install_is_repeatable(e2e):
    e2e.send_command('!!color install')
    e2e.wait_for_team_count(len(EXPECTED_TEAMS))
    e2e.send_command('!!color install')
    e2e.wait_for_output('已创建并设置所有颜色队伍')
    assert e2e.wait_for_team_count(len(EXPECTED_TEAMS)) == EXPECTED_TEAMS


def test_uninstall_removes_all_teams(e2e):
    e2e.send_command('!!color install')
    e2e.wait_for_team_count(len(EXPECTED_TEAMS))
    e2e.send_command('!!color uninstall')
    assert e2e.wait_for_team_count(0) == set()


def test_uninstall_is_repeatable(e2e):
    e2e.send_command('!!color install')
    e2e.wait_for_team_count(len(EXPECTED_TEAMS))
    e2e.send_command('!!color uninstall')
    e2e.wait_for_team_count(0)
    e2e.send_command('!!color uninstall')
    e2e.wait_for_output('已移除所有颜色队伍')
    assert e2e.wait_for_team_count(0) == set()


def test_does_not_touch_unrelated_teams(e2e):
    e2e.rcon.send_command('team add keep_me' if not e2e.uses_legacy_commands else 'scoreboard teams add keep_me')
    e2e.send_command('!!color install')
    e2e.wait_for_team_count(len(EXPECTED_TEAMS) + 1)
    assert 'keep_me' in e2e.list_teams()
    e2e.send_command('!!color uninstall')
    assert e2e.wait_for_team_count(1) == {'keep_me'}
    e2e.rcon.send_command('team remove keep_me' if not e2e.uses_legacy_commands else 'scoreboard teams remove keep_me')


def test_console_cannot_set_color(e2e):
    e2e.send_command('!!color install')
    e2e.wait_for_team_count(len(EXPECTED_TEAMS))
    e2e.send_command('!!color red')
    e2e.wait_for_output('该子命令只能由玩家执行')
    assert e2e.list_teams() == EXPECTED_TEAMS


def test_invalid_color_is_rejected(e2e):
    e2e.send_command('!!color install')
    e2e.wait_for_team_count(len(EXPECTED_TEAMS))
    e2e.send_command('!!color dark_gold')
    e2e.wait_for_output('未知颜色：dark_gold')
    assert e2e.list_teams() == EXPECTED_TEAMS
