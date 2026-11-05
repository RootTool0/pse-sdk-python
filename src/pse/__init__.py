import atexit
import ctypes
import warnings
from typing import Optional

from . import _loader
from . import _bindings
from ._bindings import Data

from .elements import (
    StaticMesh,
    DynamicMesh,
    Element,

    EntryElevator,
    ExitElevator,
    Door,
    Button,
    AntiExpropriationField,
    PedestalButton,
    SolverButton,
    Indicator,
    LaserTx,
    LaserRx,
    LaserRelay,
    LaserPanel,
    LaserCube,
    WeightCube,
    FaithPlate,
    Panel,
    Stairs,
    CubeDropper,
    SolverGunPedestal,
    Flashlight,
    Window,
    Trigger,
    Lamp,

    get_element_by_guid,
)

from .types import (
    Vector2,
    Vector3,
    Quat,
    Transform,
    Color,

    Mesh,
    Material,
    Class,
    Command,
    Event,
    Result,
)

__version__ = "1.0.3"

_is_initialized = False

def initialize() -> None:
    global _is_initialized

    if _is_initialized: return

    _loader.load_dll()
    _bindings.setup_dll_functions()

    res = _loader.get_dll().pseInitializeBuffers()
    if res != 0:
        _loader.unload_dll()
        raise RuntimeError(f"[PSE] Failed to connect to the game. Error code: {res}")

    data = Data()
    data.header = Command.GAME_INITIALIZE
    _loader.get_dll().pseCommandBufferSinglePushAndWait(ctypes.byref(data))
    if data.header != Result.SUCCESS:
        _loader.get_dll().pseDeinitializeBuffers()
        _loader.unload_dll()
        raise RuntimeError(f"[PSE] Game initialization failed. Error code: {data.header}")

    atexit.register(deinitialize)

    _is_initialized = True

def deinitialize() -> None:
    global _is_initialized

    if not _is_initialized: return

    try:
        data = Data()
        data.header = Command.GAME_DEINITIALIZE
        _loader.get_dll().pseCommandBufferSinglePushAndWait(ctypes.byref(data))
    except Exception:
        pass

    _loader.get_dll().pseDeinitializeBuffers()
    _loader.unload_dll()
    _is_initialized = False

def is_initialized() -> bool:
    global _is_initialized

    return _is_initialized

def poll_events() -> None:
    global _is_initialized

    if not _is_initialized: return

    data = Data()
    if _loader.get_dll().pseEventBufferTryGet(ctypes.byref(data)) == 0:
        return

    match data.header:
        case Event.ELEMENT_CHANGED:
            guid = data.get(0, ctypes.c_uint64).value
            state = data.get(16, ctypes.c_int8).value
            element = get_element_by_guid(guid)

            if element is not None and element._callback is not None:
                element._callback(state)
        case Event.GAME_TICK_OVERFLOW:
            # warnings.warn(f"[PSE] Tick Overflow!", RuntimeWarning)
            pass
        case _:
            warnings.warn(f"[PSE] Unknown event. Code: {data.header}", RuntimeWarning)

__all__ = [
    "__version__",

    "initialize",
    "deinitialize",
    "is_initialized",
    "poll_events",
    "get_element_by_guid",

    "Vector2",
    "Vector3",
    "Quat",
    "Transform",
    "Color",

    "Mesh",
    "Material",
    "Class",
    "Command",
    "Event",
    "Result",

    "StaticMesh",
    "DynamicMesh",
    "Element",

    "EntryElevator",
    "ExitElevator",
    "Door",
    "Button",
    "AntiExpropriationField",
    "PedestalButton",
    "SolverButton",
    "Indicator",
    "LaserTx",
    "LaserRx",
    "LaserRelay",
    "LaserPanel",
    "LaserCube",
    "WeightCube",
    "FaithPlate",
    "Panel",
    "Stairs",
    "CubeDropper",
    "SolverGunPedestal",
    "Flashlight",
    "Window",
    "Trigger",
    "Lamp"
]
