import ctypes
import os
from typing import Optional

_dll: Optional[ctypes.CDLL] = None

def load_dll(custom_path: Optional[str] = None) -> ctypes.CDLL:
    global _dll

    if _dll is not None:
        return _dll

    if custom_path is not None:
        dll_path = os.path.abspath(custom_path)
    else:
        package_dir = os.path.dirname(os.path.abspath(__file__))
        dll_path = os.path.join(package_dir, "pse.dll")

    if not os.path.exists(dll_path):
        raise FileNotFoundError(
            f"[PSE] Cannot find pse.dll at:\n  {dll_path}\n"
            f"Place pse.dll next to the package, or pass an explicit path:\n"
            f"  pse.initialize('C:/path/to/pse.dll')"
        )

    try:
        _dll = ctypes.CDLL(dll_path, winmode=0)
        return _dll
    except OSError as e:
        raise RuntimeError(f"[PSE] Failed to load {dll_path}:\n{e}") from e

def get_dll() -> ctypes.CDLL:
    global _dll

    if _dll is None:
        raise RuntimeError("[PSE] SDK is not initialized. Call pse.initialize() first.")
    return _dll

def unload_dll() -> None:
    global _dll

    _dll = None
