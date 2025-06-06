from rich import print
import typer
from typing import Literal

class State:
    def __init__(self, msg: str, status: Literal['success', 'error']):
        self.msg = msg
        self.status = status

    @property
    def error(self):
        return self.status == "error"

    @property
    def success(self):
        return self.status == "success"

class Error(State):
    def __init__(self, msg: str):
        super().__init__(msg, "error")

class Success(State):
    def __init__(self, msg: str):
        super().__init__(msg, "success")

def error(msg: str) -> None:
    """
    Print an error message in red.
    """
    print(f"[red]Error: {msg}[/red]")
    exit(-1)