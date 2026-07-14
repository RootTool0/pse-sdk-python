import atexit
import warnings

from . import _loader
from . import _bindings
from .elements import *

_is_initialized = False

def initialize() -> None:
    global _is_initialized
    if _is_initialized: return

    _loader.load_dll()
    _bindings.setup_dll_functions()
    res = _loader.get_dll().pseInitializeBuffers()
    if res != 0:
        raise RuntimeError(f"Не удалось подключиться к игре. Код ошибки: {res}")

    atexit.register(deinitialize)

    data = Data()
    data.header = Command.GAME_INITIALIZE
    get_dll().pseCommandBufferSinglePushAndWait(ctypes.byref(data))
    if data.header != Result.SUCCESS: raise RuntimeError(f"[PSE] Command Error! Code: {data.header}")

    _is_initialized = True

def deinitialize() -> None:
    global _is_initialized
    if not _is_initialized: return

    _loader.get_dll().pseDeinitializeBuffers()
    _loader.unload_dll()
    _is_initialized = False

def poll_events() -> None:
    global _is_initialized
    if not _is_initialized: return

    data = Data()
    if _loader.get_dll().pseEventBufferTryGet(ctypes.byref(data)) == 0:
        return

    match data.header:
        case Event.ELEMENT_CHANGED:
            element = get_element_by_guid(data.get(0, ctypes.c_uint64).value)
            if element is not None and element._callback is not None:
                element._callback(data.get(16, ctypes.c_int8).value)
        case Event.GAME_TICK_OVERFLOW:
            # warnings.warn(f"[PSE] Переполнение тика!", RuntimeWarning)
            pass
        case _:
            warnings.warn(f"[PSE] Неизвестное событие! Код: {data.header}", RuntimeWarning)

__all__ = [
    "initialize",
    "deinitialize",
    "poll_events",
    "get_element_by_guid",

    "Button",
    "WeightCube"
]
