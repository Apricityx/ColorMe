import json
import os
import re
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.request
from pathlib import Path

import pytest

from color_me.team_commands import uses_legacy_team_commands
from mcdreforged.minecraft.rcon.rcon_connection import RconConnection

E2E_DIR = Path(__file__).resolve().parent
REPO_ROOT = E2E_DIR.parent.parent
RUN_ROOT = E2E_DIR / '.run'
CACHE_ROOT = E2E_DIR / '.cache'
MANIFEST_URL = 'https://piston-meta.mojang.com/mc/game/version_manifest_v2.json'

RCON_PASSWORD = 'colorme-e2e'
MC_VERSION = os.environ.get('MC_VERSION', '1.12.2')
JAVA_BIN = os.environ.get('JAVA_BIN', 'java')
E2E_ENABLED = os.environ.get('MCDR_E2E') == '1'
KEEP_RUN_DIR = os.environ.get('MCDR_E2E_KEEP') == '1'


def pytest_collection_modifyitems(config, items):
    if E2E_ENABLED:
        return
    skip = pytest.mark.skip(reason='set MCDR_E2E=1 to run Minecraft end-to-end tests')
    for item in items:
        if E2E_DIR in Path(str(item.fspath)).parents:
            item.add_marker(skip)


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def parse_team_list(response: str | None) -> set[str]:
    if not response:
        return set()
    text = response.strip()
    if ':' not in text:
        return set()
    payload = text.split(':', 1)[1].strip()
    if not payload or re.search(r'\bno teams?\b', text, re.IGNORECASE):
        return set()
    # legacy scoreboard format: "- <name>: '<name>' has <n> players", possibly concatenated
    legacy_names = re.findall(r'-\s+([^\s:]+):', payload)
    if legacy_names:
        return set(legacy_names)
    # modern team format: "[<name>], [<name>], ..."
    return {part.strip().strip('[]') for part in payload.split(',') if part.strip().strip('[]')}


def download_server_jar(version: str) -> Path:
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    target = CACHE_ROOT / f'server-{version}.jar'
    if target.is_file():
        return target

    with urllib.request.urlopen(MANIFEST_URL, timeout=60) as response:
        manifest = json.load(response)
    version_entry = next(entry for entry in manifest['versions'] if entry['id'] == version)
    with urllib.request.urlopen(version_entry['url'], timeout=60) as response:
        version_meta = json.load(response)

    server_url = version_meta['downloads']['server']['url']
    partial = target.with_suffix('.jar.part')
    with urllib.request.urlopen(server_url, timeout=600) as response, open(partial, 'wb') as file:
        shutil.copyfileobj(response, file)
    partial.replace(target)
    return target


class MCDRInstance:
    def __init__(self, root: Path, process: subprocess.Popen, game_port: int, rcon_port: int):
        self.root = root
        self.process = process
        self.game_port = game_port
        self.rcon_port = rcon_port
        self.mc_version = MC_VERSION
        self._lines: list[str] = []
        self._lock = threading.Lock()
        self._rcon: RconConnection | None = None
        self._reader = threading.Thread(target=self._read_output, daemon=True)
        self._reader.start()

    def _read_output(self):
        assert self.process.stdout is not None
        for line in self.process.stdout:
            with self._lock:
                self._lines.append(line.rstrip('\n'))

    def output(self) -> str:
        with self._lock:
            return '\n'.join(self._lines)

    def wait_for_output(self, pattern: str, timeout: float = 60) -> str:
        deadline = time.monotonic() + timeout
        index = 0
        while time.monotonic() < deadline:
            with self._lock:
                new_lines = self._lines[index:]
                index = len(self._lines)
            for line in new_lines:
                if pattern in line:
                    return line
            if self.process.poll() is not None:
                raise RuntimeError(f'MCDR exited unexpectedly:\n{self.output()}')
            time.sleep(0.2)
        raise TimeoutError(f'pattern {pattern!r} not found within {timeout}s:\n{self.output()}')

    def send_command(self, command: str):
        assert self.process.stdin is not None
        self.process.stdin.write(command + '\n')
        self.process.stdin.flush()

    @property
    def rcon(self) -> RconConnection:
        if self._rcon is None:
            connection = RconConnection('127.0.0.1', self.rcon_port, RCON_PASSWORD)
            deadline = time.monotonic() + 30
            while time.monotonic() < deadline:
                try:
                    if connection.connect():
                        self._rcon = connection
                        break
                except OSError:
                    pass
                time.sleep(0.5)
            if self._rcon is None:
                raise RuntimeError('failed to connect to the server rcon')
        return self._rcon

    @property
    def uses_legacy_commands(self) -> bool:
        return uses_legacy_team_commands(self.mc_version)

    def list_teams(self) -> set[str]:
        command = 'scoreboard teams list' if self.uses_legacy_commands else 'team list'
        return parse_team_list(self.rcon.send_command(command))

    def wait_for_team_count(self, expected: int, timeout: float = 60) -> set[str]:
        deadline = time.monotonic() + timeout
        teams: set[str] = set()
        while time.monotonic() < deadline:
            teams = self.list_teams()
            if len(teams) == expected:
                return teams
            time.sleep(0.5)
        raise TimeoutError(f'expected {expected} teams, got {len(teams)}: {sorted(teams)}')

    def team_members(self, team: str) -> str:
        command = f'scoreboard teams list {team}' if self.uses_legacy_commands else f'team list {team}'
        return self.rcon.send_command(command) or ''

    def remove_team(self, team: str):
        command = f'scoreboard teams remove {team}' if self.uses_legacy_commands else f'team remove {team}'
        self.rcon.send_command(command)

    def stop(self):
        if self._rcon is not None:
            self._rcon.disconnect()
            self._rcon = None
        if self.process.poll() is not None:
            return
        try:
            self.send_command('stop')
        except (OSError, AssertionError):
            pass
        try:
            self.process.wait(timeout=60)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=30)


def _subprocess_env() -> dict:
    env = os.environ.copy()
    env['MCDREFORGED_TELEMETRY_DISABLED'] = 'true'
    env['PYTHONIOENCODING'] = 'utf-8'
    return env


def _write_server_files(server_dir: Path, server_jar: Path, game_port: int, rcon_port: int):
    server_dir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(server_jar, server_dir / 'server.jar')
    (server_dir / 'eula.txt').write_text('eula=true\n', encoding='utf-8')
    (server_dir / 'server.properties').write_text(
        '\n'.join([
            'online-mode=false',
            'enforce-secure-profile=false',
            'server-ip=127.0.0.1',
            f'server-port={game_port}',
            'enable-rcon=true',
            f'rcon.port={rcon_port}',
            f'rcon.password={RCON_PASSWORD}',
            'level-type=flat',
            'spawn-protection=0',
            'max-players=10',
            'view-distance=4',
            'sync-chunk-writes=false',
            'motd=ColorMe E2E',
            '',
        ]),
        encoding='utf-8',
    )


def _write_mcdr_config(mcdr_root: Path, rcon_port: int):
    config = {
        'language': 'en_us',
        'working_directory': 'server',
        'start_command': [JAVA_BIN, '-Xmx1024M', '-jar', 'server.jar', 'nogui'],
        'handler': 'vanilla_handler',
        'encoding': 'utf8',
        'decoding': 'utf8',
        'rcon': {
            'enable': True,
            'address': '127.0.0.1',
            'port': rcon_port,
            'password': RCON_PASSWORD,
        },
        'plugin_directories': ['plugins'],
        'check_update': False,
        'telemetry': False,
        'handler_detection': False,
        'disable_console_thread': False,
    }
    (mcdr_root / 'config.yml').write_text(json.dumps(config, indent=2), encoding='utf-8')


def _pack_plugin(mcdr_root: Path) -> Path:
    plugins_dir = mcdr_root / 'plugins'
    plugins_dir.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, '-m', 'mcdreforged', 'pack', '-i', str(REPO_ROOT), '-o', str(plugins_dir)],
        check=True,
        cwd=mcdr_root,
        env=_subprocess_env(),
    )
    packed = list(plugins_dir.glob('*.mcdr'))
    if not packed:
        raise RuntimeError('plugin packing produced no .mcdr file')
    return packed[0]


def start_instance() -> MCDRInstance:
    mcdr_root = RUN_ROOT / re.sub(r'[^0-9A-Za-z_.-]', '_', MC_VERSION)
    if mcdr_root.exists():
        shutil.rmtree(mcdr_root)
    mcdr_root.mkdir(parents=True)

    subprocess.run(
        [sys.executable, '-m', 'mcdreforged', 'init'],
        check=True,
        cwd=mcdr_root,
        env=_subprocess_env(),
    )

    game_port = free_port()
    rcon_port = free_port()
    server_jar = download_server_jar(MC_VERSION)
    _write_mcdr_config(mcdr_root, rcon_port)
    _write_server_files(mcdr_root / 'server', server_jar, game_port, rcon_port)
    packed_plugin = _pack_plugin(mcdr_root)

    process = subprocess.Popen(
        [sys.executable, '-X', 'utf8', '-u', '-m', 'mcdreforged', 'start'],
        cwd=mcdr_root,
        env=_subprocess_env(),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace',
        bufsize=1,
    )
    instance = MCDRInstance(mcdr_root, process, game_port, rcon_port)
    try:
        instance.wait_for_output('Done (', timeout=300)
    except Exception:
        instance.stop()
        raise
    if f'Plugin color_me@' not in instance.output():
        instance.stop()
        raise RuntimeError(f'plugin {packed_plugin.name} does not appear to be loaded:\n{instance.output()}')
    return instance


@pytest.fixture(scope='session')
def e2e() -> MCDRInstance:
    if not E2E_ENABLED:
        pytest.skip('set MCDR_E2E=1 to run Minecraft end-to-end tests')
    instance = start_instance()
    yield instance
    instance.stop()
    if not KEEP_RUN_DIR:
        shutil.rmtree(instance.root, ignore_errors=True)


@pytest.fixture(autouse=True)
def clean_teams(e2e: MCDRInstance):
    yield
    try:
        e2e.send_command('!!color uninstall')
        for team in e2e.list_teams():
            e2e.remove_team(team)
        e2e.wait_for_team_count(0, timeout=30)
    except (TimeoutError, OSError, AssertionError):
        pass
