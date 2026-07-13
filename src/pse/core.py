from . import _bindings
from .exceptions import PseError

class PseSession:
    def __init__(self) -> None:
        print("[Core] Сессия создана")
