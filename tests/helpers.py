from typing import Optional

from mcdreforged.command.builder.callback import DirectCallbackInvoker


class FakeInfo:
    version: Optional[str] = None


class FakeServer:
    def __init__(self, version: Optional[str] = '1.20.4', started: bool = True):
        self.version = version
        self.started = started
        self.executed: list[str] = []
        self.broadcasts: list[str] = []
        self.registered: list = []

    def execute(self, text: str, **_kwargs):
        self.executed.append(text)

    def broadcast(self, text, **_kwargs):
        self.broadcasts.append(str(text))

    def register_command(self, node):
        self.registered.append(node)

    def get_server_information(self) -> FakeInfo:
        info = FakeInfo()
        info.version = self.version
        return info

    def is_server_startup(self) -> bool:
        return self.started


class FakeSource:
    def __init__(self, server: FakeServer, player: Optional[str] = None, permission: int = 4):
        self.server = server
        self.player = player
        self.permission = permission
        self.replies: list = []

    @property
    def is_player(self) -> bool:
        return self.player is not None

    @property
    def is_console(self) -> bool:
        return self.player is None

    def reply(self, message, **_kwargs):
        self.replies.append(message)

    def get_server(self) -> FakeServer:
        return self.server

    def get_permission_level(self) -> int:
        return self.permission

    def has_permission(self, level: int) -> bool:
        return self.permission >= level


def player_source(server: FakeServer, player: str = 'Steve', permission: int = 4) -> FakeSource:
    return FakeSource(server, player=player, permission=permission)


def console_source(server: FakeServer, permission: int = 4) -> FakeSource:
    return FakeSource(server, permission=permission)


def run_command(server: FakeServer, source: FakeSource, command: str):
    root_literal = command.split(' ')[0]
    for node in server.registered:
        if root_literal in node.literals:
            executions = node._entry_execute(source, command)
            for execution in executions:
                execution.scheduled_callback.invoke(DirectCallbackInvoker())
            return
    raise AssertionError(f'command root {root_literal!r} is not registered')


def suggest(server: FakeServer, source: FakeSource, command: str) -> list[str]:
    root_literal = command.split(' ')[0]
    for node in server.registered:
        if root_literal in node.literals:
            return [suggestion.suggest_input for suggestion in node._entry_generate_suggestions(source, command)]
    raise AssertionError(f'command root {root_literal!r} is not registered')
