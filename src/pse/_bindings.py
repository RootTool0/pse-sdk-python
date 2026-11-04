import ctypes
from ._loader import get_dll

# structures.h
class Data(ctypes.Structure):
    _pack_ = 1
    _fields_ = [
        ("header", ctypes.c_uint32),
        ("data", ctypes.c_uint8 * 60)
    ]

    def set(self, offset: int, ctypes_value) -> None:
        size = ctypes.sizeof(ctypes_value)

        if offset + size > 60:
            raise ValueError(
                f"[PSE] Pack error: {size} bytes at offset {offset} "
                f"exceed the 60-byte payload buffer."
            )

        dest = ctypes.addressof(self.data) + offset
        src = ctypes.addressof(ctypes_value)
        ctypes.memmove(dest, src, size)

    def get(self, offset: int, ctypes_type):
        size = ctypes.sizeof(ctypes_type)

        if offset + size > 60:
            raise ValueError(
                f"[PSE] Read error: {size} bytes at offset {offset} "
                f"exceed the 60-byte payload buffer."
            )

        result = ctypes_type()
        dest = ctypes.addressof(result)
        src = ctypes.addressof(self.data) + offset
        ctypes.memmove(dest, src, size)
        return result

# pse.h
def setup_dll_functions() -> None:
    functions_table = {
        # Buffers / Core
        "pseInitializeBuffers": (ctypes.c_int32, []),
        "pseDeinitializeBuffers": (None, []),

        # Command Buffer / Methods
        "pseCommandBufferSynchronize": (None, []),

        "pseCommandBufferSinglePush": (ctypes.c_uint32, [ctypes.POINTER(Data)]),
        "pseCommandBufferSingleWait": (None, [ctypes.c_uint32, ctypes.POINTER(Data)]),
        "pseCommandBufferSinglePushAndWait": (None, [ctypes.POINTER(Data)]),

        # Event Buffer / Methods
        "pseEventBufferTryGet": (ctypes.c_int32, [ctypes.POINTER(Data)])
    }

    for name, (restype, argtypes) in functions_table.items():
        try:
            func = getattr(get_dll(), name)
            func.restype = restype
            func.argtypes = argtypes
        except AttributeError:
            raise AttributeError(
                f"[PSE] Function '{name}' not found in pse.dll. "
                f"Make sure it is exported on the C side (extern \"C\" __declspec(dllexport))."
            )
