import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from color_me.colors import Color

pytestmark = pytest.mark.e2e

JS_DIR = Path(__file__).resolve().parent / 'js'


def _require_bot_environment():
    if shutil.which('node') is None:
        pytest.skip('node.js is required for the player end-to-end tests')
    if not (JS_DIR / 'node_modules').is_dir():
        pytest.skip('run "npm install" in tests/e2e/js to install the bot dependencies')


def _run_bot_script(e2e, script: str, extra_env: dict) -> dict:
    result = subprocess.run(
        ['node', script],
        cwd=JS_DIR,
        env={
            **os.environ,
            'MC_HOST': '127.0.0.1',
            'MC_PORT': str(e2e.game_port),
            'MC_VERSION': e2e.mc_version,
            **extra_env,
        },
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
        timeout=180,
    )
    output = result.stdout.strip()
    payload = json.loads(output.splitlines()[-1]) if output else {}
    assert result.returncode == 0 and payload.get('ok'), f'stdout={result.stdout}\nstderr={result.stderr}'
    return payload


def test_two_clients_see_the_team_color(e2e):
    _require_bot_environment()
    e2e.send_command('!!color install')
    e2e.wait_for_team_count(len(Color))

    payload = _run_bot_script(e2e, 'color-sync-test.js', {'BOT_COLOR': 'red'})

    assert payload['aCode'] == 'c'
    assert payload['bCode'] == 'c'
    assert 'ColorBotA' in e2e.team_members(Color.red.value)


def test_player_changes_between_teams(e2e):
    _require_bot_environment()
    e2e.send_command('!!color install')
    e2e.wait_for_team_count(len(Color))

    _run_bot_script(e2e, 'color-switch-test.js', {'BOT_NAME': 'ColorBotC'})

    assert 'ColorBotC' in e2e.team_members(Color.green.value)
    assert 'ColorBotC' not in e2e.team_members(Color.red.value)
