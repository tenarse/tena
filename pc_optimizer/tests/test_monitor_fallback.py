"""
Pruebas del modulo monitor.py para el caso en que 'psutil' NO esta
instalado: la app debe avisar con un mensaje claro en vez de fallar de
forma confusa.
"""
import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules import monitor  # noqa: E402


class TestSinPsutil(unittest.TestCase):
    def test_psutil_disponible_es_false_si_no_esta_instalado(self) -> None:
        with mock.patch.object(monitor, "psutil", None):
            self.assertFalse(monitor.psutil_disponible())

    def test_obtener_snapshot_lanza_error_claro_sin_psutil(self) -> None:
        with mock.patch.object(monitor, "psutil", None):
            with self.assertRaises(RuntimeError) as contexto:
                monitor.obtener_snapshot()
            self.assertIn("psutil", str(contexto.exception))

    def test_top_procesos_lanza_error_claro_sin_psutil(self) -> None:
        with mock.patch.object(monitor, "psutil", None):
            with self.assertRaises(RuntimeError):
                monitor.top_procesos_por_ram()


if __name__ == "__main__":
    unittest.main()
