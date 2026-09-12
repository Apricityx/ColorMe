import pytest
from mcdreforged.api.command import InvalidEnumeration, RequirementNotMet

import color_me
from color_me.colors import Color
from tests.helpers import FakeServer, console_source, player_source, run_command, suggest

EXPECTED_INSTALL_REPLY = '已创建并设置所有颜色队伍'
EXPECTED_UNINSTALL_REPLY = '已移除所有颜色队伍'


def make_server(version='1.20.4', started=True):
    server = FakeServer(version=version, started=started)
    color_me.on_load(server, None)
    return server


@pytest.fixture
def server():
    return make_server()


def test_registers_single_root_command(server):
    assert len(server.registered) == 1
    assert server.registered[0].literals == {'!!color'}


def test_install_modern(server):
    source = console_source(server)
    run_command(server, source, '!!color install')

    expected = []
    for color in Color:
        expected.append(f'team add {color.value}')
        expected.append(f'team modify {color.value} color {color.name}')
    assert server.executed == expected
    assert source.replies == [EXPECTED_INSTALL_REPLY]


def test_install_legacy():
    server = make_server(version='1.12.2')
    source = console_source(server)
    run_command(server, source, '!!color install')

    assert 'scoreboard teams add __red' in server.executed
    assert 'scoreboard teams option __red color red' in server.executed
    assert len(server.executed) == len(Color) * 2


def test_install_requires_permission(server):
    source = player_source(server, permission=0)
    with pytest.raises(RequirementNotMet) as exc_info:
        run_command(server, source, '!!color install')

    assert exc_info.value.get_reason() == '你没有权限执行该命令'
    assert server.executed == []


def test_uninstall_requires_permission(server):
    source = player_source(server, permission=1)
    with pytest.raises(RequirementNotMet):
        run_command(server, source, '!!color uninstall')
    assert server.executed == []


def test_install_requires_started_server():
    server = make_server(started=False)
    source = console_source(server)
    run_command(server, source, '!!color install')

    assert source.replies == ['服务器尚未启动，无法执行该命令']
    assert server.executed == []


def test_uninstall_modern(server):
    source = console_source(server)
    run_command(server, source, '!!color uninstall')

    assert server.executed == [f'team remove {color.value}' for color in Color]
    assert source.replies == [EXPECTED_UNINSTALL_REPLY]


def test_player_sets_color(server):
    source = player_source(server, 'Alex')
    run_command(server, source, '!!color red')

    assert server.executed == ['team join __red Alex']
    assert server.broadcasts == ['已将 Alex 染色为 red']


def test_player_sets_color_legacy():
    server = make_server(version='1.12.2')
    source = player_source(server, 'Alex')
    run_command(server, source, '!!color red')

    assert server.executed == ['scoreboard teams join __red Alex']


def test_unknown_version_uses_modern_commands():
    server = make_server(version=None)
    source = player_source(server, 'Alex')
    run_command(server, source, '!!color red')

    assert server.executed == ['team join __red Alex']


def test_console_cannot_set_color(server):
    source = console_source(server)
    with pytest.raises(RequirementNotMet) as exc_info:
        run_command(server, source, '!!color red')

    assert exc_info.value.get_reason() == '该子命令只能由玩家执行'
    assert server.executed == []


def test_invalid_color(server):
    source = player_source(server)
    with pytest.raises(InvalidEnumeration) as exc_info:
        run_command(server, source, '!!color dark_gold')

    assert exc_info.value.is_handled()
    reply = source.replies[-1]
    assert '未知颜色：dark_gold' in reply
    for color in Color:
        assert color.name in reply
    assert server.executed == []


def test_list_colors(server):
    source = player_source(server)
    run_command(server, source, '!!color list')

    reply = source.replies[-1]
    for color in Color:
        assert color.name in reply


def test_bare_command_shows_usage(server):
    source = console_source(server)
    run_command(server, source, '!!color')

    assert '用法' in source.replies[-1]


def test_suggestions(server):
    source = player_source(server)
    suggestions = set(suggest(server, source, '!!color '))

    assert {'install', 'uninstall', 'list'} <= suggestions
    assert {color.name for color in Color} <= suggestions
