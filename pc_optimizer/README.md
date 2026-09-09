# PC Optimizer (Windows)

Herramienta simple con interfaz grafica para ayudar a mantener una PC con
Windows funcionando mejor. Pensada para gente nueva en programacion: cada
accion que puede borrar o cambiar algo pide confirmacion antes de hacerlo.

## Que hace

- **Monitor**: muestra el uso de CPU, RAM y disco en vivo, y que procesos
  estan consumiendo mas memoria.
- **Limpieza**: escanea y borra archivos temporales (`%TEMP%` y
  `C:\Windows\Temp`). Nunca borra nada sin que vos lo confirmes, y nunca
  toca tus documentos, fotos ni descargas.
- **Inicio**: muestra los programas configurados para abrirse solos al
  encender la PC, y te deja deshabilitarlos. Antes de deshabilitar
  cualquiera, se guarda un respaldo (`startup_backup.json`) para poder
  revertirlo.

## Requisitos

- Windows 10 u 11.
- [Python 3.8 o mas nuevo](https://www.python.org/downloads/) instalado
  (al instalarlo, marca la casilla "Add Python to PATH").

## Como ejecutarlo

Abri una terminal (PowerShell o CMD) en esta carpeta y ejecuta:

```bash
pip install -r requirements.txt
python main.py
```

Se abrira una ventana con tres pestanas: Monitor, Limpieza e Inicio.

> **Nota:** para poder deshabilitar algunos programas de inicio (los que
> estan configurados a nivel de todo el sistema) puede que necesites
> ejecutar la terminal "como Administrador".

## Seguridad / que NO hace

- No borra documentos, fotos, videos ni descargas: solo archivos
  temporales del sistema.
- No modifica el registro de Windows sin tu confirmacion explicita.
- No hay ninguna accion automatica al abrir el programa: todo se dispara
  con un boton y pide confirmacion antes de borrar o deshabilitar algo.

## Estructura del proyecto

```
pc_optimizer/
├── main.py                 # Interfaz grafica (Tkinter)
├── requirements.txt         # Dependencias (psutil)
└── modules/
    ├── monitor.py           # Lectura de CPU / RAM / disco
    ├── cleaner.py           # Escaneo y borrado de temporales
    └── startup_manager.py   # Listado y gestion de programas de inicio
```

## Proximos pasos (ideas para siguientes PRs)

- Empaquetar la app como un `.exe` con `pyinstaller` para no requerir
  Python instalado.
- Agregar la opcion de vaciar la Papelera de Reciclaje.
- Guardar un historial de limpiezas realizadas.
