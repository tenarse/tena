"""
cleaner.py
----------
Escanea y limpia archivos temporales de Windows de forma segura.

Principios de seguridad:
- Nunca borra nada sin que el modulo lo pida explicitamente (no hay
  ejecucion automatica al importar el modulo).
- Los archivos que estan en uso (bloqueados por otro programa) se
  omiten en vez de forzar su borrado.
- Siempre se puede hacer un "escaneo" (dry run) antes de borrar, para
  ver cuanto espacio se liberaria sin borrar nada todavia.
"""
from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass, field


@dataclass
class ResultadoLimpieza:
    archivos_borrados: int = 0
    archivos_omitidos: int = 0
    bytes_liberados: int = 0
    errores: list[str] = field(default_factory=list)


def carpetas_temporales() -> list[str]:
    """
    Devuelve la lista de carpetas temporales conocidas de Windows que son
    seguras de limpiar (no incluye carpetas de usuario, documentos, etc.).
    """
    carpetas = set()

    # Carpeta temporal estandar del usuario actual (%TEMP% / %TMP%)
    carpetas.add(tempfile.gettempdir())

    # Carpeta temporal a nivel de sistema (C:\Windows\Temp)
    windir = os.environ.get("WINDIR", r"C:\Windows")
    carpetas.add(os.path.join(windir, "Temp"))

    return [c for c in carpetas if os.path.isdir(c)]


def escanear(carpetas: list[str] | None = None) -> tuple[int, int]:
    """
    Recorre las carpetas temporales SIN borrar nada.

    Devuelve (cantidad_archivos, bytes_totales) que se liberarian si se
    ejecutara la limpieza.
    """
    if carpetas is None:
        carpetas = carpetas_temporales()

    cantidad = 0
    total_bytes = 0

    for carpeta in carpetas:
        for raiz, _dirs, archivos in os.walk(carpeta):
            for nombre in archivos:
                ruta = os.path.join(raiz, nombre)
                try:
                    total_bytes += os.path.getsize(ruta)
                    cantidad += 1
                except OSError:
                    # Archivo ya no existe o no se puede leer su tamano; se ignora.
                    continue

    return cantidad, total_bytes


def limpiar(carpetas: list[str] | None = None) -> ResultadoLimpieza:
    """
    Borra los archivos dentro de las carpetas temporales indicadas.

    Los archivos en uso (PermissionError / OSError) se omiten en vez de
    detener todo el proceso. Se recomienda llamar a `escanear()` antes
    para mostrarle al usuario cuanto espacio se liberaria, y pedir
    confirmacion explicita antes de llamar a esta funcion.
    """
    if carpetas is None:
        carpetas = carpetas_temporales()

    resultado = ResultadoLimpieza()

    for carpeta in carpetas:
        for raiz, dirs, archivos in os.walk(carpeta, topdown=False):
            for nombre in archivos:
                ruta = os.path.join(raiz, nombre)
                try:
                    tamano = os.path.getsize(ruta)
                    os.remove(ruta)
                    resultado.archivos_borrados += 1
                    resultado.bytes_liberados += tamano
                except OSError as exc:
                    resultado.archivos_omitidos += 1
                    resultado.errores.append(f"{ruta}: {exc}")

            # Intenta borrar subcarpetas que hayan quedado vacias.
            for nombre_dir in dirs:
                ruta_dir = os.path.join(raiz, nombre_dir)
                try:
                    os.rmdir(ruta_dir)
                except OSError:
                    continue

    return resultado


def formatear_bytes(cantidad_bytes: int) -> str:
    """Convierte una cantidad de bytes a un texto legible (KB, MB, GB)."""
    valor = float(cantidad_bytes)
    for unidad in ("B", "KB", "MB", "GB", "TB"):
        if valor < 1024:
            return f"{valor:.1f} {unidad}"
        valor /= 1024
    return f"{valor:.1f} PB"
