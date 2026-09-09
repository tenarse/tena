"""
monitor.py
----------
Recolecta metricas basicas de uso de recursos (CPU, memoria RAM, disco)
y los procesos que mas consumen, usando la libreria `psutil`.

Este modulo es de solo lectura: nunca modifica ni detiene nada en el
sistema, solo reporta informacion.
"""
from __future__ import annotations

from dataclasses import dataclass

try:
    import psutil
except ImportError:  # pragma: no cover - mensaje amigable si falta la dependencia
    psutil = None


@dataclass
class SystemSnapshot:
    """Una 'foto' del estado del sistema en un momento dado."""

    cpu_percent: float
    ram_percent: float
    ram_used_gb: float
    ram_total_gb: float
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float


def psutil_disponible() -> bool:
    """Indica si la dependencia psutil esta instalada."""
    return psutil is not None


def obtener_snapshot(disco: str = "C:\\") -> SystemSnapshot:
    """
    Devuelve una foto actual de CPU, RAM y disco.

    `disco` es la unidad a inspeccionar (por defecto la unidad C: en Windows).
    """
    if psutil is None:
        raise RuntimeError(
            "Falta instalar la dependencia 'psutil'. Ejecuta: pip install psutil"
        )

    cpu = psutil.cpu_percent(interval=0.3)

    mem = psutil.virtual_memory()
    ram_used_gb = (mem.total - mem.available) / (1024 ** 3)
    ram_total_gb = mem.total / (1024 ** 3)

    disco_info = psutil.disk_usage(disco)
    disk_used_gb = disco_info.used / (1024 ** 3)
    disk_total_gb = disco_info.total / (1024 ** 3)

    return SystemSnapshot(
        cpu_percent=cpu,
        ram_percent=mem.percent,
        ram_used_gb=ram_used_gb,
        ram_total_gb=ram_total_gb,
        disk_percent=disco_info.percent,
        disk_used_gb=disk_used_gb,
        disk_total_gb=disk_total_gb,
    )


def top_procesos_por_ram(cantidad: int = 5) -> list[tuple[str, float]]:
    """
    Devuelve los `cantidad` procesos que mas memoria RAM estan usando,
    como una lista de tuplas (nombre_proceso, porcentaje_ram).
    """
    if psutil is None:
        raise RuntimeError(
            "Falta instalar la dependencia 'psutil'. Ejecuta: pip install psutil"
        )

    procesos = []
    for proc in psutil.process_iter(["name", "memory_percent"]):
        try:
            info = proc.info
            procesos.append((info["name"] or "desconocido", info["memory_percent"] or 0.0))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    procesos.sort(key=lambda item: item[1], reverse=True)
    return procesos[:cantidad]
