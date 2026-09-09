"""
PC Optimizer - punto de entrada de la aplicacion.

Interfaz grafica simple (Tkinter) con tres pestanas:
  1. Monitor:  uso de CPU, RAM y disco en vivo.
  2. Limpieza: escaneo y borrado seguro de archivos temporales.
  3. Inicio:   ver y deshabilitar programas que arrancan con Windows.

Para ejecutar:
    pip install -r requirements.txt
    python main.py
"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from modules import cleaner, monitor, startup_manager

REFRESCO_MONITOR_MS = 2000  # cada cuanto se actualiza la pestana Monitor


class AplicacionOptimizador(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("PC Optimizer")
        self.geometry("560x420")
        self.resizable(False, False)

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        self.tab_monitor = PestanaMonitor(notebook)
        self.tab_limpieza = PestanaLimpieza(notebook)
        self.tab_inicio = PestanaInicio(notebook)

        notebook.add(self.tab_monitor, text="Monitor")
        notebook.add(self.tab_limpieza, text="Limpieza")
        notebook.add(self.tab_inicio, text="Inicio")


class PestanaMonitor(ttk.Frame):
    """Muestra CPU, RAM y disco, actualizandose automaticamente."""

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=12)

        self.lbl_cpu = ttk.Label(self, text="CPU: --%", font=("Segoe UI", 11))
        self.lbl_ram = ttk.Label(self, text="RAM: --%", font=("Segoe UI", 11))
        self.lbl_disco = ttk.Label(self, text="Disco: --%", font=("Segoe UI", 11))

        self.lbl_cpu.pack(anchor="w", pady=4)
        self.lbl_ram.pack(anchor="w", pady=4)
        self.lbl_disco.pack(anchor="w", pady=4)

        ttk.Label(self, text="Procesos que mas RAM consumen:", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", pady=(16, 4)
        )
        self.lista_procesos = tk.Listbox(self, height=6)
        self.lista_procesos.pack(fill="x")

        if not monitor.psutil_disponible():
            ttk.Label(
                self,
                text="Falta instalar 'psutil'. Ejecuta: pip install psutil",
                foreground="red",
            ).pack(anchor="w", pady=(12, 0))
        else:
            self.after(200, self._actualizar)

    def _actualizar(self) -> None:
        try:
            snap = monitor.obtener_snapshot()
            self.lbl_cpu.config(text=f"CPU: {snap.cpu_percent:.0f}%")
            self.lbl_ram.config(
                text=f"RAM: {snap.ram_percent:.0f}%  ({snap.ram_used_gb:.1f} / {snap.ram_total_gb:.1f} GB)"
            )
            self.lbl_disco.config(
                text=f"Disco: {snap.disk_percent:.0f}%  ({snap.disk_used_gb:.1f} / {snap.disk_total_gb:.1f} GB)"
            )

            self.lista_procesos.delete(0, tk.END)
            for nombre, porcentaje in monitor.top_procesos_por_ram():
                self.lista_procesos.insert(tk.END, f"{nombre}  -  {porcentaje:.1f}% RAM")
        except RuntimeError:
            pass  # psutil no instalado; ya se aviso arriba.
        finally:
            self.after(REFRESCO_MONITOR_MS, self._actualizar)


class PestanaLimpieza(ttk.Frame):
    """Escanea y limpia archivos temporales, siempre con confirmacion previa."""

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=12)

        ttk.Label(
            self,
            text="Limpia archivos temporales de Windows (%TEMP% y Windows\\Temp).",
            wraplength=500,
        ).pack(anchor="w", pady=(0, 12))

        self.lbl_resultado = ttk.Label(self, text="Todavia no se escaneo nada.")
        self.lbl_resultado.pack(anchor="w", pady=(0, 12))

        frame_botones = ttk.Frame(self)
        frame_botones.pack(anchor="w")

        ttk.Button(frame_botones, text="Escanear", command=self._escanear).pack(side="left")
        self.btn_limpiar = ttk.Button(
            frame_botones, text="Limpiar ahora", command=self._limpiar, state="disabled"
        )
        self.btn_limpiar.pack(side="left", padx=(8, 0))

        self._ultimo_escaneo = None

    def _escanear(self) -> None:
        cantidad, total_bytes = cleaner.escanear()
        self._ultimo_escaneo = (cantidad, total_bytes)
        self.lbl_resultado.config(
            text=f"Se encontraron {cantidad} archivos temporales "
            f"({cleaner.formatear_bytes(total_bytes)}) que se pueden liberar."
        )
        self.btn_limpiar.config(state="normal" if cantidad > 0 else "disabled")

    def _limpiar(self) -> None:
        if not self._ultimo_escaneo:
            return

        cantidad, total_bytes = self._ultimo_escaneo
        confirmar = messagebox.askyesno(
            "Confirmar limpieza",
            f"Esto borrara {cantidad} archivos temporales "
            f"({cleaner.formatear_bytes(total_bytes)}). Esta accion no se puede deshacer.\n\n"
            "¿Deseas continuar?",
        )
        if not confirmar:
            return

        resultado = cleaner.limpiar()
        self.lbl_resultado.config(
            text=(
                f"Listo: {resultado.archivos_borrados} archivos borrados "
                f"({cleaner.formatear_bytes(resultado.bytes_liberados)} liberados), "
                f"{resultado.archivos_omitidos} omitidos por estar en uso."
            )
        )
        self.btn_limpiar.config(state="disabled")
        self._ultimo_escaneo = None


class PestanaInicio(ttk.Frame):
    """Lista y permite deshabilitar programas de inicio de Windows."""

    def __init__(self, parent: ttk.Notebook) -> None:
        super().__init__(parent, padding=12)

        ttk.Label(
            self,
            text="Programas que arrancan junto con Windows:",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        self.tabla = ttk.Treeview(self, columns=("origen", "valor"), show="headings", height=10)
        self.tabla.heading("origen", text="Origen")
        self.tabla.heading("valor", text="Programa / comando")
        self.tabla.column("origen", width=110)
        self.tabla.column("valor", width=380)
        self.tabla.pack(fill="both", expand=True)

        frame_botones = ttk.Frame(self)
        frame_botones.pack(anchor="w", pady=(8, 0))

        ttk.Button(frame_botones, text="Actualizar lista", command=self._cargar_lista).pack(side="left")
        ttk.Button(
            frame_botones, text="Deshabilitar seleccionado", command=self._deshabilitar_seleccionado
        ).pack(side="left", padx=(8, 0))

        self._items: dict[str, startup_manager.ItemInicio] = {}
        self._cargar_lista()

    def _cargar_lista(self) -> None:
        self.tabla.delete(*self.tabla.get_children())
        self._items.clear()

        try:
            items = startup_manager.listar_items_inicio()
        except RuntimeError as exc:
            messagebox.showwarning("No disponible", str(exc))
            return

        for item in items:
            fila_id = self.tabla.insert("", tk.END, values=(item.origen, f"{item.nombre}: {item.valor}"))
            self._items[fila_id] = item

    def _deshabilitar_seleccionado(self) -> None:
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Nada seleccionado", "Selecciona un programa de la lista primero.")
            return

        fila_id = seleccion[0]
        item = self._items.get(fila_id)
        if item is None:
            return

        confirmar = messagebox.askyesno(
            "Confirmar",
            f"Esto detendra que '{item.nombre}' se abra automaticamente al iniciar Windows.\n"
            "Se guarda un respaldo por si quieres revertirlo mas adelante.\n\n"
            "¿Deseas continuar?",
        )
        if not confirmar:
            return

        try:
            startup_manager.deshabilitar_item(item)
            messagebox.showinfo("Listo", f"'{item.nombre}' fue deshabilitado.")
            self._cargar_lista()
        except PermissionError:
            messagebox.showerror(
                "Permisos insuficientes",
                "Necesitas ejecutar PC Optimizer como Administrador para deshabilitar este item.",
            )
        except RuntimeError as exc:
            messagebox.showerror("Error", str(exc))


if __name__ == "__main__":
    app = AplicacionOptimizador()
    app.mainloop()
