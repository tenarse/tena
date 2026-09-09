"""
startup_manager.py
-------------------
Lista y administra los programas que se inician automaticamente con
Windows, desde dos fuentes:

1. Las claves del Registro de Windows "Run" (HKEY_CURRENT_USER y
   HKEY_LOCAL_MACHINE).
2. La carpeta de inicio ("Startup") del usuario y la de todos los
   usuarios.

Seguridad:
- "Deshabilitar" un item NUNCA lo borra para siempre: primero se hace
  un respaldo en `startup_backup.json` (para el registro) o se mueve
  el acceso directo a una subcarpeta `_deshabilitados` (para la carpeta
  de inicio), de forma que el usuario pueda revertir el cambio.
- Modificar HKEY_LOCAL_MACHINE normalmente requiere permisos de
  Administrador; si falla por permisos, se informa con un mensaje claro
  en vez de fallar en silencio.
"""
from __future__ import annotations

import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path

try:
    import winreg  # Solo existe en Windows
except ImportError:  # pragma: no cover - permite importar el modulo en otros SO para pruebas
    winreg = None

ARCHIVO_RESPALDO = "startup_backup.json"

CLAVES_REGISTRO = [
    (
        "HKCU",
        "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    ),
    (
        "HKLM",
        "Software\\Microsoft\\Windows\\CurrentVersion\\Run",
    ),
]


@dataclass
class ItemInicio:
    nombre: str
    origen: str  # "HKCU", "HKLM" o "Carpeta de inicio"
    valor: str  # comando o ruta del ejecutable/acceso directo
    ruta_extra: str = ""  # ruta completa al archivo, solo para items de carpeta


def _hive_de(nombre_hive: str):
    if winreg is None:
        raise RuntimeError("Esta funcion solo esta disponible en Windows.")
    return winreg.HKEY_CURRENT_USER if nombre_hive == "HKCU" else winreg.HKEY_LOCAL_MACHINE


def _listar_desde_registro() -> list[ItemInicio]:
    items: list[ItemInicio] = []
    if winreg is None:
        return items

    for nombre_hive, subclave in CLAVES_REGISTRO:
        try:
            hive = _hive_de(nombre_hive)
            with winreg.OpenKey(hive, subclave, 0, winreg.KEY_READ) as clave:
                i = 0
                while True:
                    try:
                        nombre, valor, _tipo = winreg.EnumValue(clave, i)
                        items.append(ItemInicio(nombre=nombre, origen=nombre_hive, valor=valor))
                        i += 1
                    except OSError:
                        break
        except FileNotFoundError:
            continue
        except PermissionError:
            continue

    return items


def _carpetas_inicio() -> list[str]:
    carpetas = []
    appdata = os.environ.get("APPDATA")
    if appdata:
        carpetas.append(os.path.join(appdata, "Microsoft", "Windows", "Start Menu", "Programs", "Startup"))

    programdata = os.environ.get("PROGRAMDATA")
    if programdata:
        carpetas.append(
            os.path.join(programdata, "Microsoft", "Windows", "Start Menu", "Programs", "StartUp")
        )

    return [c for c in carpetas if os.path.isdir(c)]


def _listar_desde_carpetas() -> list[ItemInicio]:
    items: list[ItemInicio] = []
    for carpeta in _carpetas_inicio():
        for nombre in os.listdir(carpeta):
            ruta = os.path.join(carpeta, nombre)
            if os.path.isfile(ruta):
                items.append(
                    ItemInicio(
                        nombre=nombre,
                        origen="Carpeta de inicio",
                        valor=ruta,
                        ruta_extra=ruta,
                    )
                )
    return items


def listar_items_inicio() -> list[ItemInicio]:
    """Devuelve todos los programas configurados para iniciar con Windows."""
    return _listar_desde_registro() + _listar_desde_carpetas()


def _guardar_respaldo(item: ItemInicio, carpeta_respaldo: str) -> None:
    Path(carpeta_respaldo).mkdir(parents=True, exist_ok=True)
    ruta_respaldo = os.path.join(carpeta_respaldo, ARCHIVO_RESPALDO)

    respaldos = []
    if os.path.isfile(ruta_respaldo):
        with open(ruta_respaldo, "r", encoding="utf-8") as f:
            respaldos = json.load(f)

    respaldos.append(
        {
            "nombre": item.nombre,
            "origen": item.origen,
            "valor": item.valor,
        }
    )

    with open(ruta_respaldo, "w", encoding="utf-8") as f:
        json.dump(respaldos, f, ensure_ascii=False, indent=2)


def deshabilitar_item(item: ItemInicio, carpeta_respaldo: str = ".") -> None:
    """
    Deshabilita un programa de inicio, respaldando su informacion antes
    de quitarlo para que el cambio sea reversible.

    Lanza PermissionError si se necesitan permisos de Administrador
    (tipico al tocar HKEY_LOCAL_MACHINE) y RuntimeError si algo mas falla.
    """
    _guardar_respaldo(item, carpeta_respaldo)

    if item.origen == "Carpeta de inicio":
        destino_dir = os.path.join(os.path.dirname(item.ruta_extra), "_deshabilitados")
        Path(destino_dir).mkdir(exist_ok=True)
        shutil.move(item.ruta_extra, os.path.join(destino_dir, os.path.basename(item.ruta_extra)))
        return

    if winreg is None:
        raise RuntimeError("Esta funcion solo esta disponible en Windows.")

    hive = _hive_de(item.origen)
    subclave = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    with winreg.OpenKey(hive, subclave, 0, winreg.KEY_SET_VALUE) as clave:
        winreg.DeleteValue(clave, item.nombre)
