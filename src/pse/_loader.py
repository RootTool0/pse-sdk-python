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
        dll_path = os.path.join(package_dir, "../../dist/bin/PSE.dll")

    if not os.path.exists(dll_path):
        raise FileNotFoundError(
            f"[PSE] Критическая ошибка: Не удалось найти бинарник SDK по пути:\n{dll_path}\n"
            f"Положите \"pse.dll\" в папку библиотеки или укажите путь вручную при initialize()."
        )

    try:
        _dll = ctypes.CDLL(dll_path, winmode=0)
        return _dll
    except OSError as e:
        raise RuntimeError(f"[PSE] Ошибка операционной системы при загрузке {dll_path}:\n{e}")

def get_dll() -> ctypes.CDLL:
    global _dll

    if _dll is None:
        raise RuntimeError("[PSE] Ошибка: Попытка обратиться к функциям SDK до вызова pse.initialize().")
    return _dll

def unload_dll() -> None:
    global _dll
    _dll = None
