"""
Pruebas del modulo cleaner.py.

Estas pruebas NUNCA tocan las carpetas temporales reales del sistema:
siempre operan sobre una carpeta temporal creada exclusivamente para el
test (via tempfile.TemporaryDirectory), que se borra sola al terminar.
"""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules import cleaner  # noqa: E402


class TestEscanearYLimpiar(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.carpeta = self.tmpdir.name

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def _crear_archivo(self, nombre: str, contenido: bytes) -> str:
        ruta = os.path.join(self.carpeta, nombre)
        with open(ruta, "wb") as f:
            f.write(contenido)
        return ruta

    def test_escanear_carpeta_vacia(self) -> None:
        cantidad, total_bytes = cleaner.escanear([self.carpeta])
        self.assertEqual(cantidad, 0)
        self.assertEqual(total_bytes, 0)

    def test_escanear_cuenta_archivos_y_bytes(self) -> None:
        self._crear_archivo("a.tmp", b"x" * 100)
        self._crear_archivo("b.tmp", b"y" * 250)

        cantidad, total_bytes = cleaner.escanear([self.carpeta])

        self.assertEqual(cantidad, 2)
        self.assertEqual(total_bytes, 350)

    def test_escanear_incluye_subcarpetas(self) -> None:
        subcarpeta = os.path.join(self.carpeta, "sub")
        os.makedirs(subcarpeta)
        with open(os.path.join(subcarpeta, "c.tmp"), "wb") as f:
            f.write(b"z" * 10)

        cantidad, total_bytes = cleaner.escanear([self.carpeta])

        self.assertEqual(cantidad, 1)
        self.assertEqual(total_bytes, 10)

    def test_limpiar_borra_archivos_y_reporta_bytes_liberados(self) -> None:
        self._crear_archivo("a.tmp", b"x" * 100)
        self._crear_archivo("b.tmp", b"y" * 50)

        resultado = cleaner.limpiar([self.carpeta])

        self.assertEqual(resultado.archivos_borrados, 2)
        self.assertEqual(resultado.bytes_liberados, 150)
        self.assertEqual(resultado.archivos_omitidos, 0)
        self.assertEqual(os.listdir(self.carpeta), [])

    def test_limpiar_carpeta_ya_limpia_no_falla(self) -> None:
        resultado = cleaner.limpiar([self.carpeta])
        self.assertEqual(resultado.archivos_borrados, 0)
        self.assertEqual(resultado.errores, [])


class TestFormatearBytes(unittest.TestCase):
    def test_bytes_pequenos(self) -> None:
        self.assertEqual(cleaner.formatear_bytes(500), "500.0 B")

    def test_kilobytes(self) -> None:
        self.assertEqual(cleaner.formatear_bytes(2048), "2.0 KB")

    def test_megabytes(self) -> None:
        self.assertEqual(cleaner.formatear_bytes(5 * 1024 * 1024), "5.0 MB")

    def test_gigabytes(self) -> None:
        self.assertEqual(cleaner.formatear_bytes(3 * 1024 ** 3), "3.0 GB")


if __name__ == "__main__":
    unittest.main()
