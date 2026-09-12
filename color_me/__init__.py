from typing import Optional

from mcdreforged.api.command import Enumeration, InvalidEnumeration, Requirements, SimpleCommandBuilder
from mcdreforged.api.types import CommandSource, PermissionLevel, PluginServerInterface

from .colors import Color
from .i18n import tr
from .team_commands import build_install_commands, build_uninstall_commands, team_join_command

_INSTALL_PERMISSION = PermissionLevel.HELPER
_COLOR_NAMES = ', '.join(color.name for color in Color)


def _server_version(server) -> Optional[str]:
    return server.get_server_information().version


def _check_server_started(src: CommandSource) -> bool:
    if src.get_server().is_server_startup():
        return True
    src.reply(tr(src, 'server_not_started'))
    return False


def _show_usage(src: CommandSource):
    src.reply(tr(src, 'usage'))


def _list_colors(src: CommandSource):
    src.reply(tr(src, 'colors', colors=_COLOR_NAMES))


def _install(src: CommandSource):
    if not _check_server_started(src):
        return
    server = src.get_server()
    for command in build_install_commands(_server_version(server)):
        server.execute(command)
    src.reply(tr(src, 'install_done'))


def _uninstall(src: CommandSource):
    if not _check_server_started(src):
        return
    server = src.get_server()
    for command in build_uninstall_commands(_server_version(server)):
        server.execute(command)
    src.reply(tr(src, 'uninstall_done'))


def _set_color(src: CommandSource, context: dict):
    if not _check_server_started(src):
        return
    color: Color = context['color']
    player = getattr(src, 'player', None)
    if player is None:
        src.reply(tr(src, 'player_only'))
        return
    server = src.get_server()
    server.execute(team_join_command(color, player, _server_version(server)))
    server.broadcast(tr(src, 'color_changed', player=player, color=color.name))


def _on_invalid_color(src: CommandSource, error, _context):
    src.reply(tr(src, 'unknown_color', color=error.get_error_segment(), colors=_COLOR_NAMES))


def on_load(server: PluginServerInterface, _old):
    builder = SimpleCommandBuilder()

    builder.command('!!color', _show_usage)

    builder.literal('install').requires(
        Requirements.has_permission(_INSTALL_PERMISSION), lambda src: tr(src, 'no_permission')
    )
    builder.command('!!color install', _install)

    builder.literal('uninstall').requires(
        Requirements.has_permission(_INSTALL_PERMISSION), lambda src: tr(src, 'no_permission')
    )
    builder.command('!!color uninstall', _uninstall)

    builder.command('!!color list', _list_colors)

    builder.arg('color', lambda name: Enumeration(name, Color)).requires(
        Requirements.is_player(), lambda src: tr(src, 'player_only')
    ).on_error(InvalidEnumeration, _on_invalid_color, handled=True)
    builder.command('!!color <color>', _set_color)

    builder.register(server)
