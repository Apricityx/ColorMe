from typing import Optional

from mcdreforged.api.command import Enumeration, InvalidEnumeration, Requirements, SimpleCommandBuilder
from mcdreforged.api.types import CommandSource, PermissionLevel, PluginServerInterface

from .colors import Color
from .team_commands import build_install_commands, build_uninstall_commands, team_join_command

_INSTALL_PERMISSION = PermissionLevel.HELPER
_COLOR_NAMES = ', '.join(color.name for color in Color)
_PLAYER_ONLY = '该子命令只能由玩家执行'
_NO_PERMISSION = '你没有权限执行该命令'
_SERVER_NOT_STARTED = '服务器尚未启动，无法执行该命令'


def _server_version(server) -> Optional[str]:
    return server.get_server_information().version


def _check_server_started(src: CommandSource) -> bool:
    if src.get_server().is_server_startup():
        return True
    src.reply(_SERVER_NOT_STARTED)
    return False


def _show_usage(src: CommandSource):
    src.reply('用法：!!color <颜色> | !!color list | !!color install | !!color uninstall')


def _list_colors(src: CommandSource):
    src.reply(f'可用颜色：{_COLOR_NAMES}')


def _install(src: CommandSource):
    if not _check_server_started(src):
        return
    server = src.get_server()
    for command in build_install_commands(_server_version(server)):
        server.execute(command)
    src.reply('已创建并设置所有颜色队伍')


def _uninstall(src: CommandSource):
    if not _check_server_started(src):
        return
    server = src.get_server()
    for command in build_uninstall_commands(_server_version(server)):
        server.execute(command)
    src.reply('已移除所有颜色队伍')


def _set_color(src: CommandSource, context: dict):
    if not _check_server_started(src):
        return
    color: Color = context['color']
    player = getattr(src, 'player', None)
    if player is None:
        src.reply(_PLAYER_ONLY)
        return
    server = src.get_server()
    server.execute(team_join_command(color, player, _server_version(server)))
    server.broadcast(f'已将 {player} 染色为 {color.name}')


def _on_invalid_color(src: CommandSource, error, _context):
    src.reply(f'未知颜色：{error.get_error_segment()}\n可用颜色：{_COLOR_NAMES}')


def on_load(server: PluginServerInterface, _old):
    builder = SimpleCommandBuilder()

    builder.command('!!color', _show_usage)

    builder.literal('install').requires(Requirements.has_permission(_INSTALL_PERMISSION), lambda: _NO_PERMISSION)
    builder.command('!!color install', _install)

    builder.literal('uninstall').requires(Requirements.has_permission(_INSTALL_PERMISSION), lambda: _NO_PERMISSION)
    builder.command('!!color uninstall', _uninstall)

    builder.command('!!color list', _list_colors)

    builder.arg('color', lambda name: Enumeration(name, Color)).requires(
        Requirements.is_player(), lambda: _PLAYER_ONLY
    ).on_error(InvalidEnumeration, _on_invalid_color, handled=True)
    builder.command('!!color <color>', _set_color)

    builder.register(server)
