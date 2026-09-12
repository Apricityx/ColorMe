from typing import Any

from mcdreforged.api.types import CommandSource

DEFAULT_LANGUAGE = 'en_us'

TRANSLATIONS: dict[str, dict[str, str]] = {
    DEFAULT_LANGUAGE: {
        'usage': 'Usage: !!color <color> | !!color list | !!color install | !!color uninstall',
        'colors': 'Available colors: {colors}',
        'install_done': 'Created and configured all color teams',
        'uninstall_done': 'Removed all color teams',
        'color_changed': '{player} is now colored {color}',
        'unknown_color': 'Unknown color: {color}\nAvailable colors: {colors}',
        'player_only': 'This subcommand can only be used by a player',
        'no_permission': 'You do not have permission to use this command',
        'server_not_started': 'The server has not started yet',
    },
    'zh_cn': {
        'usage': '用法：!!color <颜色> | !!color list | !!color install | !!color uninstall',
        'colors': '可用颜色：{colors}',
        'install_done': '已创建并设置所有颜色队伍',
        'uninstall_done': '已移除所有颜色队伍',
        'color_changed': '已将 {player} 染色为 {color}',
        'unknown_color': '未知颜色：{color}\n可用颜色：{colors}',
        'player_only': '该子命令只能由玩家执行',
        'no_permission': '你没有权限执行该命令',
        'server_not_started': '服务器尚未启动，无法执行该命令',
    },
}


def _fallback_languages(language: str | None) -> list[str]:
    candidates = [language] if language else []
    if language and language.startswith('zh') and 'zh_cn' not in candidates:
        candidates.append('zh_cn')
    if DEFAULT_LANGUAGE not in candidates:
        candidates.append(DEFAULT_LANGUAGE)
    return candidates


def translate(language: str | None, key: str, **kwargs: Any) -> str:
    for candidate in _fallback_languages(language):
        template = TRANSLATIONS.get(candidate, {}).get(key)
        if template is not None:
            return template.format(**kwargs)
    return key


def get_language(source: CommandSource) -> str:
    getter = getattr(source, 'get_preference', None)
    if getter is None:
        return DEFAULT_LANGUAGE
    try:
        return getter().language or DEFAULT_LANGUAGE
    except Exception:
        return DEFAULT_LANGUAGE


def tr(source: CommandSource, key: str, **kwargs: Any) -> str:
    return translate(get_language(source), key, **kwargs)
