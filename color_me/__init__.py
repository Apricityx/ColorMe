# color_plugin.py
from enum import Enum

from mcdreforged.api.command import SimpleCommandBuilder, Text
from mcdreforged.api.types import PluginServerInterface
from mcdreforged.command.command_source import CommandSource, PlayerCommandSource


class Dye(Enum):
    red = '__red'
    blue = '__blue'
    green = '__green'
    yellow = '__yellow'
    light_purple = '__light_purple'
    aqua = '__aqua'
    white = '__white'
    black = '__black'
    gray = '__gray'
    gold = '__gold'
    dark_red = '__dark_red'
    dark_blue = '__dark_blue'
    dark_green = '__dark_green'
    dark_aqua = '__dark_aqua'
    dark_purple = '__dark_purple'
    dark_gray = '__dark_gray'


def _init_teams(server):
    for color in Dye:
        team = color.value
        server.execute(f'team add {team}')
        server.execute(f'team modify {team} color {color.name}')


def _uninstall_teams(server):
    for color in Dye:
        server.execute(f'team remove {color.value}')


def _install(src: CommandSource, _ctx=None):
    _init_teams(src.get_server())
    src.reply('已创建并设置所有颜色队伍')


def _uninstall(src: CommandSource, _ctx=None):
    _uninstall_teams(src.get_server())
    src.reply('已移除所有颜色队伍')


def _set_color(src: CommandSource, ctx: dict):
    if not src.is_player:
        src.reply('该子命令只能由玩家执行'); return
    color_name: str = ctx['color']
    if color_name not in Dye.__members__:
        src.reply(f'未知颜色：{color_name}\n可用颜色：red,blue,green,yellow,light_purple,aqua,white,black,gray,gold,dark_red,dark_blue,dark_green,dark_aqua,dark_purple,dark_gray,dark_gold'); return

    team = Dye[color_name].value
    server = src.get_server()
    player = (src.player if isinstance(src, PlayerCommandSource) else None)
    if not player:
        src.reply('无法识别玩家名'); return

    server.execute(f'execute as {player} run team join {team} {player}')
    server.broadcast(f'已将 {player} 染色为 {color_name}')


def _list_colors(src: CommandSource, _ctx=None):
    names = ', '.join(Dye.__members__.keys())
    src.reply(f'可用颜色：{names}')


def on_load(server: PluginServerInterface, _old):
    builder = SimpleCommandBuilder()

    builder.command('!!color install', _install)
    builder.command('!!color uninstall', _uninstall)

    # !!color list
    builder.command('!!color list', _list_colors)

    # !!color <color>
    builder.command('!!color <color>', _set_color)
    builder.arg('color', Text).suggests(lambda _s=None, _c=None: list(Dye.__members__.keys()))

    builder.register(server)
