import ctypes
from abc import ABC, abstractmethod
from typing import Dict

from .types import *
from ._loader import get_dll
from ._bindings import Data

class StaticMesh:
    @staticmethod
    def create(quat: Quat = Quat(0.0, 0.0, 0.0, 1.0), location: Vector3 = Vector3(0.0, 0.0, 0.0), scale: Vector3 = Vector3(1.0, 1.0, 1.0), mesh: Mesh = Mesh.PLANE, material: Material = Material.WALL_WHITE_SMALL) -> None:
        data = Data()
        data.header = Command.STATIC_MESH_CREATE
        data.set(0, Transform(quat, location, scale))
        data.set(40, ctypes.c_uint16(mesh))
        data.set(42, ctypes.c_uint16(material))

        get_dll().pseCommandBufferSinglePushAndWait(ctypes.byref(data))
        if data.header != Result.SUCCESS: raise RuntimeError(f"[PSE] Command Error! Code: {data.header}")

class DynamicMesh:
    def __init__(self) -> None:
        self._guid: int = -1
        self._transform = Transform(Quat(0.0, 0.0, 0.0, 1.0), Vector3(0.0, 0.0, 0.0), Vector3(1.0, 1.0, 1.0))
        self._mesh = Mesh.PLANE
        self._material = Material.WALL_WHITE_SMALL
        self._visibility = True

    @property
    def location(self) -> Vector3:
        return self._transform.location

    @location.setter
    def location(self, new_location: Vector3) -> None:
        self._transform.location = new_location
        self._update_transform()

    @property
    def rotation(self) -> Quat:
        return self._transform.quat

    @rotation.setter
    def rotation(self, new_quat: Quat) -> None:
        self._transform.quat = new_quat
        self._update_transform()

    @property
    def scale(self) -> Vector3:
        return self._transform.scale

    @scale.setter
    def scale(self, new_scale: Vector3) -> None:
        self._transform.scale = new_scale
        self._update_transform()

    @property
    def mesh(self) -> Mesh:
        return self._mesh

    @mesh.setter
    def mesh(self, new_mesh: Mesh) -> None:
        self._mesh = new_mesh
        self._update_mesh()

    @property
    def material(self) -> bool:
        return self._material

    @material.setter
    def material(self, new_material: Material) -> None:
        self._material = new_material
        self._update_material()

    @property
    def visibility(self) -> bool:
        return self._visibility

    @visibility.setter
    def visibility(self, new_visibility: bool) -> None:
        self._visibility = new_visibility
        self._update_visibility()

    def create(self) -> None:
        if self._guid != -1: return

        data = Data()
        data.header = Command.DYNAMIC_MESH_CREATE
        data.set(0, self._transform)
        data.set(40, ctypes.c_uint16(self._mesh))
        data.set(42, ctypes.c_uint16(self._material))
        data.set(44, ctypes.c_int8(1 if self._visibility else 0))

        get_dll().pseCommandBufferSinglePushAndWait(ctypes.byref(data))
        if data.header != Result.SUCCESS: raise RuntimeError(f"[PSE] Command Error! Code: {data.header}")

        self._guid = data.get(0, ctypes.c_uint64).value

    def destroy(self) -> None:
        if self._guid == -1: return

        data = Data()
        data.header = Command.DYNAMIC_MESH_DESTROY
        data.set(0, ctypes.c_uint64(self._guid))

        get_dll().pseCommandBufferSinglePushAndWait(ctypes.byref(data))
        if data.header != Result.SUCCESS: raise RuntimeError(f"[PSE] Command Error! Code: {data.header}")

        self._guid = -1

    def __bool__(self) -> bool:
        return self._guid != -1

    def _update_transform(self):
        if self._guid == -1: return

        data = Data()
        data.header = Command.DYNAMIC_MESH_SET_TRANSFORM
        data.set(0, ctypes.c_uint64(self._guid))
        data.set(8, self._transform)

        get_dll().pseCommandBufferSinglePushAndWait(ctypes.byref(data))
        if data.header != Result.SUCCESS: raise RuntimeError(f"[PSE] Command Error! Code: {data.header}")

    def _update_mesh(self):
        if self._guid == -1: return

        data = Data()
        data.header = Command.DYNAMIC_MESH_SET_MESH
        data.set(0, ctypes.c_uint64(self._guid))
        data.set(8, ctypes.c_uint16(self._mesh))

        get_dll().pseCommandBufferSinglePushAndWait(ctypes.byref(data))
        if data.header != Result.SUCCESS: raise RuntimeError(f"[PSE] Command Error! Code: {data.header}")

    def _update_material(self):
        if self._guid == -1: return

        data = Data()
        data.header = Command.DYNAMIC_MESH_SET_MATERIAL
        data.set(0, ctypes.c_uint64(self._guid))
        data.set(8, ctypes.c_uint16(self._material))

        get_dll().pseCommandBufferSinglePushAndWait(ctypes.byref(data))
        if data.header != Result.SUCCESS: raise RuntimeError(f"[PSE] Command Error! Code: {data.header}")

    def _update_visibility(self):
        if self._guid == -1: return

        data = Data()
        data.header = Command.DYNAMIC_MESH_SET_VISIBILITY
        data.set(0, ctypes.c_uint64(self._guid))
        data.set(8, ctypes.c_int8(1 if self._visibility else 0))

        get_dll().pseCommandBufferSinglePushAndWait(ctypes.byref(data))
        if data.header != Result.SUCCESS: raise RuntimeError(f"[PSE] Command Error! Code: {data.header}")

_all_elements: Dict[int, 'Element'] = {}

class Element(ABC):
    def __init__(self) -> None:
        self._guid: int = -1
        self._transform = Transform(Quat(0.0, 0.0, 0.0, 1.0), Vector3(0.0, 0.0, 0.0), Vector3(1.0, 1.0, 1.0))
        self._callback = None
        self._visibility = True
        self._state = True

    @property
    def location(self) -> Vector3:
        return self._transform.location

    @location.setter
    def location(self, new_location: Vector3) -> None:
        self._transform.location = new_location
        self._update_transform()

    @property
    def rotation(self) -> Quat:
        return self._transform.quat

    @rotation.setter
    def rotation(self, new_quat: Quat) -> None:
        self._transform.quat = new_quat
        self._update_transform()

    @property
    def scale(self) -> Vector3:
        return self._transform.scale

    @scale.setter
    def scale(self, new_scale: Vector3) -> None:
        self._transform.scale = new_scale
        self._update_transform()

    @property
    def visibility(self) -> bool:
        return self._visibility

    @visibility.setter
    def visibility(self, new_visibility: bool) -> None:
        self._visibility = new_visibility
        self._update_visibility()

    @property
    def state(self) -> int:
        return self._state

    @state.setter
    def state(self, new_state: int) -> None:
        self._state = new_state
        self._update_state()

    def create(self) -> None:
        if self._guid != -1: return

        data = Data()
        data.header = Command.ELEMENT_CREATE
        data.set(0, self._transform)
        data.set(40, ctypes.c_uint16(self._get_class))
        data.set(42, ctypes.c_uint64(0))
        data.set(50, ctypes.c_int8(self._state))
        data.set(51, ctypes.c_int8(1 if self._visibility else 0))

        get_dll().pseCommandBufferSinglePushAndWait(ctypes.byref(data))
        if data.header != Result.SUCCESS: raise RuntimeError(f"[PSE] Command Error! Code: {data.header}")

        self._guid = data.get(0, ctypes.c_uint64).value
        _all_elements[self._guid] = self

    def destroy(self) -> None:
        if self._guid == -1: return

        data = Data()
        data.header = Command.ELEMENT_DESTROY
        data.set(0, ctypes.c_uint64(self._guid))

        get_dll().pseCommandBufferSinglePushAndWait(ctypes.byref(data))
        if data.header != Result.SUCCESS: raise RuntimeError(f"[PSE] Command Error! Code: {data.header}")

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

    @property
    @abstractmethod
    def _get_class(self) -> Class:
        pass

    def _update_transform(self):
        if self._guid == -1: return

        data = Data()
        data.header = Command.ELEMENT_SET_TRANSFORM
        data.set(0, ctypes.c_uint64(self._guid))
        data.set(8, self._transform)

        get_dll().pseCommandBufferSinglePushAndWait(ctypes.byref(data))
        if data.header != Result.SUCCESS: raise RuntimeError(f"[PSE] Command Error! Code: {data.header}")

    def _update_visibility(self):
        if self._guid == -1: return

        data = Data()
        data.header = Command.ELEMENT_SET_VISIBILITY
        data.set(0, ctypes.c_uint64(self._guid))
        data.set(8, ctypes.c_int8(1 if self._visibility else 0))

        get_dll().pseCommandBufferSinglePushAndWait(ctypes.byref(data))
        if data.header != Result.SUCCESS: raise RuntimeError(f"[PSE] Command Error! Code: {data.header}")

    def _update_state(self):
        if self._guid == -1: return

        data = Data()
        data.header = Command.ELEMENT_SET_STATE
        data.set(0, ctypes.c_uint64(self._guid))
        data.set(8, ctypes.c_int8(self._state))

        get_dll().pseCommandBufferSinglePushAndWait(ctypes.byref(data))
        if data.header != Result.SUCCESS: raise RuntimeError(f"[PSE] Command Error! Code: {data.header}")

def get_element_by_guid(guid: int) -> Element | None:
    return _all_elements.get(guid)

class EntryElevator(Element):
    @property
    def _get_class(self) -> Class:
        return Class.ENTRY_ELEVATOR

class ExitElevator(Element):
    @property
    def _get_class(self) -> Class:
        return Class.EXIT_ELEVATOR

class Door(Element):
    @property
    def _get_class(self) -> Class:
        return Class.DOOR

class Button(Element):
    @property
    def _get_class(self) -> Class:
        return Class.BUTTON

class AntiExpropriationField(Element):
    @property
    def _get_class(self) -> Class:
        return Class.ANTI_EXPROPRIATION_FIELD

class PedestalButton(Element):
    @property
    def _get_class(self) -> Class:
        return Class.PEDESTAL_BUTTON

class SolverButton(Element):
    @property
    def _get_class(self) -> Class:
        return Class.SOLVER_BUTTON

class Indicator(Element):
    @property
    def _get_class(self) -> Class:
        return Class.INDICATOR

class LaserTx(Element):
    @property
    def _get_class(self) -> Class:
        return Class.LASER_TX

class LaserRx(Element):
    @property
    def _get_class(self) -> Class:
        return Class.LASER_RX

class LaserRelay(Element):
    @property
    def _get_class(self) -> Class:
        return Class.LASER_RELAY

class LaserPlane(Element):
    @property
    def _get_class(self) -> Class:
        return Class.LASER_PLANE

class LaserCube(Element):
    @property
    def _get_class(self) -> Class:
        return Class.LASER_CUBE

class WeightCube(Element):
    @property
    def _get_class(self) -> Class:
        return Class.WEIGHT_CUBE

class FaithPlate(Element):
    @property
    def _get_class(self) -> Class:
        return Class.FAITH_PLATE

class Panel(Element):
    @property
    def _get_class(self) -> Class:
        return Class.PANEL

class Stairs(Element):
    @property
    def _get_class(self) -> Class:
        return Class.STAIRS

class CubeDroppper(Element):
    @property
    def _get_class(self) -> Class:
        return Class.CUBE_DROPPER

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

class Trigger(Element):
    @property
    def _get_class(self) -> Class:
        return Class.TRIGGER

class Lamp(Element):
    @property
    def _get_class(self) -> Class:
        return Class.LAMP
