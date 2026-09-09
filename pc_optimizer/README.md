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

## Opcion 1: Descargar el .exe (mas facil, no requiere instalar Python)

Cada vez que se actualiza el codigo, GitHub compila automaticamente un
`PCOptimizer.exe` listo para usar. Para descargarlo:

1. Anda a la pestana **[Actions](../../actions/workflows/build-windows-exe.yml)**
   de este repositorio.
2. Entra a la ejecucion mas reciente con una tilde verde ✅.
3. Bajá hasta la seccion **Artifacts** y descarga `PCOptimizer-windows-exe`
   (es un .zip; adentro esta `PCOptimizer.exe`).
4. Descomprimilo y hace doble clic en `PCOptimizer.exe`. Windows puede
   mostrar un aviso de "Editor desconocido" (SmartScreen) la primera vez,
   porque el .exe no esta firmado digitalmente; hace clic en "Mas
   informacion" y luego "Ejecutar de todas formas" si confias en el origen
   (este mismo repositorio).

> Nota: los artefactos de GitHub Actions requieren estar logueado en
> GitHub para descargarlos, y se borran automaticamente a los 30 dias.
> Si en algun momento se publica una release (tag `pc-optimizer-v*`), el
> .exe tambien va a estar disponible sin vencimiento en la seccion
> **Releases** del repositorio.

## Opcion 2: Ejecutarlo desde el codigo fuente (con Python instalado)

Util si queres modificar el codigo o si no confias todavia en ejecutar un
.exe descargado.

1. Instala [Python 3.8 o mas nuevo](https://www.python.org/downloads/)
   (al instalarlo, marca la casilla "Add Python to PATH").
2. Abri una terminal (PowerShell o CMD) en esta carpeta y ejecuta:

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

- Firmar el .exe digitalmente para que Windows SmartScreen no muestre
  el aviso de "Editor desconocido".
- Agregar la opcion de vaciar la Papelera de Reciclaje.
- Guardar un historial de limpiezas realizadas.
