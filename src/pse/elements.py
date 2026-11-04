import ctypes
from abc import ABC, abstractmethod
from typing import Callable, Dict, Optional

from .types import *
from ._loader import get_dll
from ._bindings import Data

def _push(data: Data) -> None:
    get_dll().pseCommandBufferSinglePushAndWait(ctypes.byref(data))
    if data.header != Result.SUCCESS:
        raise RuntimeError(f"[PSE] Command failed. Error code: {data.header}")

def _color_to_int(rgb: tuple[int, int, int]) -> int:
    r, g, b = rgb
    if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
        raise ValueError(f"[PSE] RGB components must be 0..255, got {rgb}")
    return (r << 16) | (g << 8) | b

def _int_to_color(value: int) -> tuple[int, int, int]:
    return ((value >> 16) & 0xFF, (value >> 8) & 0xFF, value & 0xFF)

class StaticMesh:
    @staticmethod
    def create(location: Vector3 = Vector3(0.0, 0.0, 0.0), quat: Quat = Quat(0.0, 0.0, 0.0, 1.0), scale: Vector3 = Vector3(1.0, 1.0, 1.0), mesh: Mesh = Mesh.PLANE, material: Material = Material.WALL_WHITE_SMALL) -> None:
        data = Data()
        data.header = Command.STATIC_MESH_CREATE
        data.set(0, Transform(quat, location, scale))
        data.set(40, ctypes.c_uint16(mesh))
        data.set(42, ctypes.c_uint16(material))
        _push(data)

class DynamicMesh:
    def __init__(self) -> None:
        self._guid: int = -1

    @property
    def guid(self) -> int:
        return self._guid

    @property
    def transform(self) -> Transform:
        if self._guid == -1: return Transform(Quat(0.0, 0.0, 0.0, 1.0), Vector3(0.0, 0.0, 0.0), Vector3(1.0, 1.0, 1.0))

        data = Data()
        data.header = Command.DYNAMIC_MESH_GET_TRANSFORM
        data.set(0, ctypes.c_uint64(self._guid))
        _push(data)
        return data.get(0, Transform)

    @transform.setter
    def transform(self, new_transform: Transform) -> None:
        if self._guid == -1: return

        data = Data()
        data.header = Command.DYNAMIC_MESH_SET_TRANSFORM
        data.set(0, ctypes.c_uint64(self._guid))
        data.set(8, new_transform)
        _push(data)

    @property
    def location(self) -> Vector3:
        return self.transform.location

    @location.setter
    def location(self, new_location: Vector3) -> None:
        t = self.transform
        t.location = new_location
        self.transform = t

    @property
    def rotation(self) -> Quat:
        return self.transform.quat

    @rotation.setter
    def rotation(self, new_quat: Quat) -> None:
        t = self.transform
        t.quat = new_quat
        self.transform = t

    @property
    def scale(self) -> Vector3:
        return self.transform.scale

    @scale.setter
    def scale(self, new_scale: Vector3) -> None:
        t = self.transform
        t.scale = new_scale
        self.transform = t

    @property
    def visibility(self) -> bool:
        if self._guid == -1: return True

        data = Data()
        data.header = Command.DYNAMIC_MESH_GET_VISIBILITY
        data.set(0, ctypes.c_uint64(self._guid))
        _push(data)
        return bool(data.get(0, ctypes.c_int8).value)

    @visibility.setter
    def visibility(self, new_visibility: bool) -> None:
        if self._guid == -1: return

        data = Data()
        data.header = Command.DYNAMIC_MESH_SET_VISIBILITY
        data.set(0, ctypes.c_uint64(self._guid))
        data.set(8, ctypes.c_int8(1 if new_visibility else 0))
        _push(data)

    @property
    def mesh(self) -> Mesh:
        raise AttributeError("[PSE] mesh is write-only")

    @mesh.setter
    def mesh(self, new_mesh: Mesh) -> None:
        if self._guid == -1: return

        data = Data()
        data.header = Command.DYNAMIC_MESH_SET_MESH
        data.set(0, ctypes.c_uint64(self._guid))
        data.set(8, ctypes.c_uint16(new_mesh))
        _push(data)

    @property
    def material(self) -> Material:
        raise AttributeError("[PSE] material is write-only")

    @material.setter
    def material(self, new_material: Material) -> None:
        if self._guid == -1: return

        data = Data()
        data.header = Command.DYNAMIC_MESH_SET_MATERIAL
        data.set(0, ctypes.c_uint64(self._guid))
        data.set(8, ctypes.c_uint16(new_material))
        _push(data)

    def create(self, location: Vector3 = Vector3(0.0, 0.0, 0.0), quat: Quat = Quat(0.0, 0.0, 0.0, 1.0), scale: Vector3 = Vector3(1.0, 1.0, 1.0), mesh: Mesh = Mesh.PLANE, material: Material = Material.WALL_WHITE_SMALL, visibility: bool = True) -> None:
        if self._guid != -1: return

        data = Data()
        data.header = Command.DYNAMIC_MESH_CREATE
        data.set(0, Transform(quat, location, scale))
        data.set(40, ctypes.c_uint16(mesh))
        data.set(42, ctypes.c_uint16(material))
        data.set(44, ctypes.c_int8(1 if visibility else 0))
        _push(data)
        self._guid = data.get(0, ctypes.c_uint64).value

    def destroy(self) -> None:
        if self._guid == -1: return

        data = Data()
        data.header = Command.DYNAMIC_MESH_DESTROY
        data.set(0, ctypes.c_uint64(self._guid))
        _push(data)
        self._guid = -1

    def __bool__(self) -> bool:
        return self._guid != -1

    def __repr__(self) -> str:
        return f"DynamicMesh(guid={self._guid})"


_all_elements: Dict[int, 'Element'] = {}


class Element(ABC):
    def __init__(self) -> None:
        self._guid: int = -1
        self._callback: Optional[Callable[[int], None]] = None

    @property
    def guid(self) -> int:
        return self._guid

    @property
    def transform(self) -> Transform:
        if self._guid == -1: return Transform(Quat(0.0, 0.0, 0.0, 1.0), Vector3(0.0, 0.0, 0.0), Vector3(1.0, 1.0, 1.0))

        data = Data()
        data.header = Command.ELEMENT_GET_TRANSFORM
        data.set(0, ctypes.c_uint64(self._guid))
        _push(data)
        return data.get(0, Transform)

    @transform.setter
    def transform(self, new_transform: Transform) -> None:
        if self._guid == -1: return

        data = Data()
        data.header = Command.ELEMENT_SET_TRANSFORM
        data.set(0, ctypes.c_uint64(self._guid))
        data.set(8, new_transform)
        _push(data)

    @property
    def location(self) -> Vector3:
        return self.transform.location

    @location.setter
    def location(self, new_location: Vector3) -> None:
        t = self.transform
        t.location = new_location
        self.transform = t

    @property
    def rotation(self) -> Quat:
        return self.transform.quat

    @rotation.setter
    def rotation(self, new_quat: Quat) -> None:
        t = self.transform
        t.quat = new_quat
        self.transform = t

    @property
    def scale(self) -> Vector3:
        return self.transform.scale

    @scale.setter
    def scale(self, new_scale: Vector3) -> None:
        t = self.transform
        t.scale = new_scale
        self.transform = t

    @property
    def visibility(self) -> bool:
        if self._guid == -1: return True

        data = Data()
        data.header = Command.ELEMENT_GET_VISIBILITY
        data.set(0, ctypes.c_uint64(self._guid))
        _push(data)
        return bool(data.get(0, ctypes.c_int8).value)

    @visibility.setter
    def visibility(self, new_visibility: bool) -> None:
        if self._guid == -1: retur

        data = Data()
        data.header = Command.ELEMENT_SET_VISIBILITY
        data.set(0, ctypes.c_uint64(self._guid))
        data.set(8, ctypes.c_int8(1 if new_visibility else 0))
        _push(data)

    @property
    def state(self) -> int:
        if self._guid == -1: return 0

        data = Data()
        data.header = Command.ELEMENT_GET_STATE
        data.set(0, ctypes.c_uint64(self._guid))
        _push(data)
        return data.get(0, ctypes.c_int8).value

    @state.setter
    def state(self, new_state: int) -> None:
        if not -128 <= new_state <= 127: raise ValueError(f"[PSE] state must fit in int8_t, got {new_state}")
        if self._guid == -1: return

        data = Data()
        data.header = Command.ELEMENT_SET_STATE
        data.set(0, ctypes.c_uint64(self._guid))
        data.set(8, ctypes.c_int8(new_state))
        _push(data)

    def _get_register(self, index: int) -> int:
        if not 0 <= index <= 7: raise IndexError(f"[PSE] Register index must be 0..7, got {index}")

        if self._guid == -1: return 0
        data = Data()
        data.header = Command.ELEMENT_GET_REGISTER
        data.set(0, ctypes.c_uint64(self._guid))
        data.set(8, ctypes.c_int8(index))
        _push(data)
        return data.get(0, ctypes.c_uint32).value

    def _set_register(self, index: int, value: int) -> None:
        if not 0 <= index <= 7: raise IndexError(f"[PSE] Register index must be 0..7, got {index}")
        if not 0 <= value <= 0xFFFFFFFF: raise ValueError(f"[PSE] Register value must fit in uint32_t, got {value}")
        if self._guid == -1: return

        data = Data()
        data.header = Command.ELEMENT_SET_REGISTER
        data.set(0, ctypes.c_uint64(self._guid))
        data.set(8, ctypes.c_uint32(value))
        data.set(16, ctypes.c_int8(index))
        _push(data)

    def create(self, location: Vector3 = Vector3(0.0, 0.0, 0.0), quat: Quat = Quat(0.0, 0.0, 0.0, 1.0), scale: Vector3 = Vector3(1.0, 1.0, 1.0), state: int = 0, visibility: bool = True) -> None:
        if self._guid != -1: return
        if not -128 <= state <= 127: raise ValueError(f"[PSE] state must fit in int8_t, got {state}")

        data = Data()
        data.header = Command.ELEMENT_CREATE
        data.set(0, Transform(quat, location, scale))
        data.set(40, ctypes.c_uint16(self._get_class))
        data.set(42, ctypes.c_uint64(0))
        data.set(50, ctypes.c_int8(state))
        data.set(51, ctypes.c_int8(1 if visibility else 0))
        _push(data)
        self._guid = data.get(0, ctypes.c_uint64).value
        _all_elements[self._guid] = self

    def destroy(self) -> None:
        if self._guid == -1: return
        data = Data()
        data.header = Command.ELEMENT_DESTROY
        data.set(0, ctypes.c_uint64(self._guid))
        _push(data)
        _all_elements.pop(self._guid, None)
        self._guid = -1

    def on_element_changed(self):
        def wrapper(func):
            self._callback = func
            return func
        return wrapper

    def set_on_element_changed(self, func):
        return self.on_element_changed()(func)

    def __bool__(self) -> bool:
        return self._guid != -1

    def __repr__(self) -> str:
        return f"{type(self).__name__}(guid={self._guid})"

    @property
    @abstractmethod
    def _get_class(self) -> Class:
        pass

def get_element_by_guid(guid: int) -> Optional[Element]:
    return _all_elements.get(guid)

class EntryElevator(Element):
    @property
    def _get_class(self) -> Class:
        return Class.ENTRY_ELEVATOR
    
    @property
    def auto_close(self) -> bool:
        return bool(self._get_register(0) & 0x2)

    @auto_close.setter
    def auto_close(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | 0x2) if value else (r & ~0x2))

    @property
    def callback_highlight(self) -> bool:
        return bool(self._get_register(0) & 0x1)

    @callback_highlight.setter
    def callback_highlight(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | 0x1) if value else (r & ~0x1))

    @property
    def color_on(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(1))

    @color_on.setter
    def color_on(self, value: tuple[int, int, int]) -> None:
        self._set_register(1, _color_to_int(value))

    @property
    def color_off(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(2))

    @color_off.setter
    def color_off(self, value: tuple[int, int, int]) -> None:
        self._set_register(2, _color_to_int(value))

class ExitElevator(Element):
    @property
    def _get_class(self) -> Class:
        return Class.EXIT_ELEVATOR
    
    @property
    def auto_close(self) -> bool:
        return bool(self._get_register(0) & 0x2)

    @auto_close.setter
    def auto_close(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | 0x2) if value else (r & ~0x2))

    @property
    def callback_highlight(self) -> bool:
        return bool(self._get_register(0) & 0x1)

    @callback_highlight.setter
    def callback_highlight(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | 0x1) if value else (r & ~0x1))

    @property
    def color_on(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(1))

    @color_on.setter
    def color_on(self, value: tuple[int, int, int]) -> None:
        self._set_register(1, _color_to_int(value))

    @property
    def color_off(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(2))

    @color_off.setter
    def color_off(self, value: tuple[int, int, int]) -> None:
        self._set_register(2, _color_to_int(value))

class Door(Element):
    @property
    def _get_class(self) -> Class:
        return Class.DOOR
    
    @property
    def auto_close(self) -> bool:
        return bool(self._get_register(0) & 0x2)

    @auto_close.setter
    def auto_close(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | 0x2) if value else (r & ~0x2))

    @property
    def callback_highlight(self) -> bool:
        return bool(self._get_register(0) & 0x1)

    @callback_highlight.setter
    def callback_highlight(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | 0x1) if value else (r & ~0x1))

    @property
    def color_on(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(1))

    @color_on.setter
    def color_on(self, value: tuple[int, int, int]) -> None:
        self._set_register(1, _color_to_int(value))

    @property
    def color_off(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(2))

    @color_off.setter
    def color_off(self, value: tuple[int, int, int]) -> None:
        self._set_register(2, _color_to_int(value))

class Button(Element):
    @property
    def _get_class(self) -> Class:
        return Class.BUTTON
        
    @property
    def color_on(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(1))
        
    @color_on.setter
    def color_on(self, value: tuple[int, int, int]) -> None:
        self._set_register(1, _color_to_int(value))

    @property
    def color_off(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(2))

    @color_off.setter
    def color_off(self, value: tuple[int, int, int]) -> None:
        self._set_register(2, _color_to_int(value))

class AntiExpropriationField(Element):
    @property
    def _get_class(self) -> Class:
        return Class.ANTI_EXPROPRIATION_FIELD
    
    @property
    def solver_gun_mode(self) -> int:
        return (self._get_register(0) >> 2) & 0xF

    @solver_gun_mode.setter
    def solver_gun_mode(self, value: int) -> None:
        if not 0 <= value <= 0xF: raise ValueError(f"[PSE] solver_gun_mode must be 0..15, got {value}")

        r = self._get_register(0)
        self._set_register(0, (r & ~(0xF << 2)) | (value << 2))

    @property
    def kill_player(self) -> bool:
        return bool(self._get_register(0) & 0x2)

    @kill_player.setter
    def kill_player(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | 0x2) if value else (r & ~0x2))

    @property
    def destroy_objects(self) -> bool:
        return bool(self._get_register(0) & 0x1)

    @destroy_objects.setter
    def destroy_objects(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | 0x1) if value else (r & ~0x1))

    @property
    def color(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(1))

    @color.setter
    def color(self, value: tuple[int, int, int]) -> None:
        self._set_register(1, _color_to_int(value))

    @property
    def size(self) -> tuple[int, int]:
        r = self._get_register(2)
        return ((r >> 16) & 0xFFFF, r & 0xFFFF)

    @size.setter
    def size(self, value: tuple[int, int]) -> None:
        w, h = value
        if not (0 <= w <= 0xFFFF and 0 <= h <= 0xFFFF): raise ValueError(f"[PSE] size components must be 0..65535, got {value}")

        self._set_register(2, (w << 16) | h)

class PedestalButton(Element):
    @property
    def _get_class(self) -> Class: 
        return Class.PEDESTAL_BUTTON
    
    @property
    def timer_seconds(self) -> int:
        return (self._get_register(0) >> 2) & 0x7F

    @timer_seconds.setter
    def timer_seconds(self, value: int) -> None:
        if not 0 <= value <= 127:
            raise ValueError(f"[PSE] timer_seconds must be 0..127, got {value}")
        r = self._get_register(0)
        self._set_register(0, (r & ~(0x7F << 2)) | (value << 2))

    @property
    def button_mode(self) -> int:
        return self._get_register(0) & 0x3

    @button_mode.setter
    def button_mode(self, value: int) -> None:
        if not 0 <= value <= 3: raise ValueError(f"[PSE] button_mode must be 0..3, got {value}")

        r = self._get_register(0)
        self._set_register(0, (r & ~0x3) | value)

    @property
    def color_on(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(1))

    @color_on.setter
    def color_on(self, value: tuple[int, int, int]) -> None:
        self._set_register(1, _color_to_int(value))

    @property
    def color_off(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(2))

    @color_off.setter
    def color_off(self, value: tuple[int, int, int]) -> None:
        self._set_register(2, _color_to_int(value))

class SolverButton(Element):
    @property
    def _get_class(self) -> Class:
        return Class.SOLVER_BUTTON
    
    @property
    def callback_highlight(self) -> bool:
        return bool(self._get_register(0) & (1 << 11))

    @callback_highlight.setter
    def callback_highlight(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | (1 << 11)) if value else (r & ~(1 << 11)))

    @property
    def flat(self) -> bool:
        return bool(self._get_register(0) & (1 << 10))

    @flat.setter
    def flat(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | (1 << 10)) if value else (r & ~(1 << 10)))

    @property
    def timer_seconds(self) -> int:
        return (self._get_register(0) >> 2) & 0x7F

    @timer_seconds.setter
    def timer_seconds(self, value: int) -> None:
        if not 0 <= value <= 127: raise ValueError(f"[PSE] timer_seconds must be 0..127, got {value}")

        r = self._get_register(0)
        self._set_register(0, (r & ~(0x7F << 2)) | (value << 2))

    @property
    def button_mode(self) -> int:
        return self._get_register(0) & 0x3

    @button_mode.setter
    def button_mode(self, value: int) -> None:
        if not 0 <= value <= 3: raise ValueError(f"[PSE] button_mode must be 0..3, got {value}")

        r = self._get_register(0)
        self._set_register(0, (r & ~0x3) | value)

    @property
    def color_on(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(1))

    @color_on.setter
    def color_on(self, value: tuple[int, int, int]) -> None:
        self._set_register(1, _color_to_int(value))

    @property
    def color_off(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(2))

    @color_off.setter
    def color_off(self, value: tuple[int, int, int]) -> None:
        self._set_register(2, _color_to_int(value))

class Indicator(Element):
    @property
    def _get_class(self) -> Class:
        return Class.INDICATOR
    
    @property
    def flat(self) -> bool:
        return bool(self._get_register(0) & 0x2)

    @flat.setter
    def flat(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | 0x2) if value else (r & ~0x2))

    @property
    def timer_mode(self) -> bool:
        return bool(self._get_register(0) & 0x1)

    @timer_mode.setter
    def timer_mode(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | 0x1) if value else (r & ~0x1))

    @property
    def color_on(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(1))

    @color_on.setter
    def color_on(self, value: tuple[int, int, int]) -> None:
        self._set_register(1, _color_to_int(value))

    @property
    def color_off(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(2))

    @color_off.setter
    def color_off(self, value: tuple[int, int, int]) -> None:
        self._set_register(2, _color_to_int(value))

class LaserTx(Element):
    @property
    def _get_class(self) -> Class:
        return Class.LASER_TX
    
    @property
    def shifted(self) -> bool:
        return bool(self._get_register(0) & 0x1)

    @shifted.setter
    def shifted(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | 0x1) if value else (r & ~0x1))

    @property
    def laser_color(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(1))

    @laser_color.setter
    def laser_color(self, value: tuple[int, int, int]) -> None:
        self._set_register(1, _color_to_int(value))

class LaserRx(Element):
    @property
    def _get_class(self) -> Class:
        return Class.LASER_RX
    
    @property
    def shifted(self) -> bool:
        return bool(self._get_register(0) & 0x1)

    @shifted.setter
    def shifted(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | 0x1) if value else (r & ~0x1))

    @property
    def color_on(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(1))

    @color_on.setter
    def color_on(self, value: tuple[int, int, int]) -> None:
        self._set_register(1, _color_to_int(value))

    @property
    def color_off(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(2))

    @color_off.setter
    def color_off(self, value: tuple[int, int, int]) -> None:
        self._set_register(2, _color_to_int(value))

    @property
    def color_filter_enabled(self) -> bool:
        return bool(self._get_register(3) & (1 << 24))

    @color_filter_enabled.setter
    def color_filter_enabled(self, value: bool) -> None:
        r = self._get_register(3)
        self._set_register(3, (r | (1 << 24)) if value else (r & ~(1 << 24)))

    @property
    def laser_color(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(3) & 0xFFFFFF)

    @laser_color.setter
    def laser_color(self, value: tuple[int, int, int]) -> None:
        r = self._get_register(3) & (1 << 24)
        self._set_register(3, r | _color_to_int(value))

class LaserRelay(Element):
    @property
    def _get_class(self) -> Class:
        return Class.LASER_RELAY
    
    @property
    def color_filter_enabled(self) -> bool:
        return bool(self._get_register(0) & (1 << 24))

    @color_filter_enabled.setter
    def color_filter_enabled(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | (1 << 24)) if value else (r & ~(1 << 24)))

    @property
    def laser_color(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(0) & 0xFFFFFF)

    @laser_color.setter
    def laser_color(self, value: tuple[int, int, int]) -> None:
        r = self._get_register(0) & (1 << 24)
        self._set_register(0, r | _color_to_int(value))

class LaserPanel(Element):
    @property
    def _get_class(self) -> Class:
        return Class.LASER_PANEL
    
    @property
    def activation_visual(self) -> bool:
        return bool(self._get_register(0) & (1 << 31))

    @activation_visual.setter
    def activation_visual(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | (1 << 31)) if value else (r & ~(1 << 31)))

    @property
    def max_angle(self) -> int:
        return (self._get_register(0) >> 16) & 0xFF

    @max_angle.setter
    def max_angle(self, value: int) -> None:
        if not 0 <= value <= 180:
            raise ValueError(f"[PSE] max_angle must be 0..180, got {value}")
        r = self._get_register(0)
        self._set_register(0, (r & ~(0xFF << 16)) | (value << 16))

    @property
    def min_angle(self) -> int:
        return (self._get_register(0) >> 8) & 0xFF

    @min_angle.setter
    def min_angle(self, value: int) -> None:
        if not 0 <= value <= 180:
            raise ValueError(f"[PSE] min_angle must be 0..180, got {value}")
        r = self._get_register(0)
        self._set_register(0, (r & ~(0xFF << 8)) | (value << 8))

    @property
    def angle(self) -> int:
        return self._get_register(0) & 0xFF

    @angle.setter
    def angle(self, value: int) -> None:
        if not 0 <= value <= 180: raise ValueError(f"[PSE] angle must be 0..180, got {value}")

        r = self._get_register(0)
        self._set_register(0, (r & ~0xFF) | value)

    @property
    def color_on(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(1))

    @color_on.setter
    def color_on(self, value: tuple[int, int, int]) -> None:
        self._set_register(1, _color_to_int(value))

    @property
    def color_off(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(2))

    @color_off.setter
    def color_off(self, value: tuple[int, int, int]) -> None:
        self._set_register(2, _color_to_int(value))

class LaserCube(Element):
    @property
    def _get_class(self) -> Class:
        return Class.LASER_CUBE

class WeightCube(Element):
    @property
    def _get_class(self) -> Class:
        return Class.WEIGHT_CUBE
    
    @property
    def callback_highlight(self) -> bool:
        return bool(self._get_register(0) & 0x1)

    @callback_highlight.setter
    def callback_highlight(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | 0x1) if value else (r & ~0x1))

    @property
    def color_on(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(1))

    @color_on.setter
    def color_on(self, value: tuple[int, int, int]) -> None:
        self._set_register(1, _color_to_int(value))

    @property
    def color_off(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(2))

    @color_off.setter
    def color_off(self, value: tuple[int, int, int]) -> None:
        self._set_register(2, _color_to_int(value))

class FaithPlate(Element):
    @property
    def _get_class(self) -> Class:
        return Class.FAITH_PLATE
    
    @property
    def release_on_land(self) -> bool:
        return bool(self._get_register(0) & 0x2)

    @release_on_land.setter
    def release_on_land(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | 0x2) if value else (r & ~0x2))

    @property
    def global_coords(self) -> bool:
        return bool(self._get_register(0) & 0x1)

    @global_coords.setter
    def global_coords(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | 0x1) if value else (r & ~0x1))

    @property
    def color_on(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(1))

    @color_on.setter
    def color_on(self, value: tuple[int, int, int]) -> None:
        self._set_register(1, _color_to_int(value))

    @property
    def color_off(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(2))

    @color_off.setter
    def color_off(self, value: tuple[int, int, int]) -> None:
        self._set_register(2, _color_to_int(value))

class Panel(Element):
    @property
    def _get_class(self) -> Class:
        return Class.PANEL
    
    @property
    def animation(self) -> int:
        return self._get_register(0) & 0xFF

    @animation.setter
    def animation(self, value: int) -> None:
        if not 0 <= value <= 0xFF:
            raise ValueError(f"[PSE] animation must be 0..255, got {value}")
        r = self._get_register(0)
        self._set_register(0, (r & ~0xFF) | value)

    @property
    def color_on(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(1))

    @color_on.setter
    def color_on(self, value: tuple[int, int, int]) -> None:
        self._set_register(1, _color_to_int(value))

    @property
    def color_off(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(2))

    @color_off.setter
    def color_off(self, value: tuple[int, int, int]) -> None:
        self._set_register(2, _color_to_int(value))

class Stairs(Element):
    @property
    def _get_class(self) -> Class:
        return Class.STAIRS
    
    @property
    def color_on(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(1))

    @color_on.setter
    def color_on(self, value: tuple[int, int, int]) -> None:
        self._set_register(1, _color_to_int(value))

    @property
    def color_off(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(2))

    @color_off.setter
    def color_off(self, value: tuple[int, int, int]) -> None:
        self._set_register(2, _color_to_int(value))

class CubeDropper(Element):
    @property
    def _get_class(self) -> Class:
        return Class.CUBE_DROPPER
    
    @property
    def respawn_cube(self) -> bool:
        return bool(self._get_register(0) & (1 << 4))

    @respawn_cube.setter
    def respawn_cube(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | (1 << 4)) if value else (r & ~(1 << 4)))

    @property
    def cube_type(self) -> int:
        return self._get_register(0) & 0xF

    @cube_type.setter
    def cube_type(self, value: int) -> None:
        if not 0 <= value <= 0xF: raise ValueError(f"[PSE] cube_type must be 0..15, got {value}")

        r = self._get_register(0)
        self._set_register(0, (r & ~0xF) | value)

    @property
    def color_on(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(1))

    @color_on.setter
    def color_on(self, value: tuple[int, int, int]) -> None:
        self._set_register(1, _color_to_int(value))

    @property
    def color_off(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(2))

    @color_off.setter
    def color_off(self, value: tuple[int, int, int]) -> None:
        self._set_register(2, _color_to_int(value))

class SolverGunPedestal(Element):
    @property
    def _get_class(self) -> Class:
        return Class.SOLVER_GUN_PEDESTAL

class Flashlight(Element):
    @property
    def _get_class(self) -> Class:
        return Class.FLASHLIGHT

class Window(Element):
    @property
    def _get_class(self) -> Class:
        return Class.WINDOW
    
    @property
    def material_glass(self) -> int:
        return self._get_register(0) >> 16

    @material_glass.setter
    def material_glass(self, value: int) -> None:
        r = self._get_register(0)
        self._set_register(0, (r & 0xFFFF) | ((value & 0xFFFF) << 16))

    @property
    def frame_mask(self) -> int:
        return (self._get_register(0) >> 2) & 0x3FF

    @frame_mask.setter
    def frame_mask(self, value: int) -> None:
        if not 0 <= value <= 0x3FF: raise ValueError(f"[PSE] frame_mask must be 0..1023, got {value}")

        r = self._get_register(0)
        self._set_register(0, (r & ~(0x3FF << 2)) | (value << 2))

    @property
    def pass_solver_gun(self) -> bool:
        return bool(self._get_register(0) & 0x2)

    @pass_solver_gun.setter
    def pass_solver_gun(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | 0x2) if value else (r & ~0x2))

    @property
    def pass_laser(self) -> bool:
        return bool(self._get_register(0) & 0x1)

    @pass_laser.setter
    def pass_laser(self, value: bool) -> None:
        r = self._get_register(0)
        self._set_register(0, (r | 0x1) if value else (r & ~0x1))

    @property
    def size(self) -> tuple[int, int]:
        r = self._get_register(1)
        return (r >> 16, r & 0xFFFF)

    @size.setter
    def size(self, value: tuple[int, int]) -> None:
        w, h = value
        if not (0 <= w <= 0xFFFF and 0 <= h <= 0xFFFF): raise ValueError(f"[PSE] size components must be 0..65535, got {value}")

        self._set_register(1, (w << 16) | h)

class Trigger(Element):
    @property
    def _get_class(self) -> Class:
        return Class.TRIGGER
    
    @property
    def target(self) -> int:
        return (self._get_register(0) >> 8) & 0xF

    @target.setter
    def target(self, value: int) -> None:
        if not 0 <= value <= 0xF: raise ValueError(f"[PSE] target must be 0..15, got {value}")

        r = self._get_register(0)
        self._set_register(0, (r & ~(0xF << 8)) | (value << 8))

    @property
    def condition(self) -> int:
        return (self._get_register(0) >> 4) & 0xF

    @condition.setter
    def condition(self, value: int) -> None:
        if not 0 <= value <= 0xF: raise ValueError(f"[PSE] condition must be 0..15, got {value}")

        r = self._get_register(0)
        self._set_register(0, (r & ~(0xF << 4)) | (value << 4))

    @property
    def action(self) -> int:
        return self._get_register(0) & 0xF

    @action.setter
    def action(self, value: int) -> None:
        if not 0 <= value <= 0xF:
            raise ValueError(f"[PSE] action must be 0..15, got {value}")
        r = self._get_register(0)
        self._set_register(0, (r & ~0xF) | value)

class Lamp(Element):
    @property
    def _get_class(self) -> Class:
        return Class.LAMP
    
    @property
    def color_on(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(1))

    @color_on.setter
    def color_on(self, value: tuple[int, int, int]) -> None:
        self._set_register(1, _color_to_int(value))

    @property
    def color_off(self) -> tuple[int, int, int]:
        return _int_to_color(self._get_register(2))

    @color_off.setter
    def color_off(self, value: tuple[int, int, int]) -> None:
        self._set_register(2, _color_to_int(value))
