# ⚡ πDiaDownloader

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-00f0ff.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![GUI CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blue.svg?style=for-the-badge&logo=gui&logoColor=cyan)](https://github.com/TomSchimansky/CustomTkinter)
[![Backend yt-dlp](https://img.shields.io/badge/backend-yt--dlp-ff4757.svg?style=for-the-badge&logo=youtube&logoColor=white)](https://github.com/yt-dlp/yt-dlp)
[![License MIT](https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Platform Windows | Linux | macOS](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-7b2cbf.svg?style=for-the-badge)](#)

> **Aplicación de escritorio nativa de alto rendimiento diseñada para creadores de contenido y editores**, enfocada en la extracción rápida, limpia y en máxima calidad de vídeo y audio desde YouTube, TikTok (sin marca de agua), Twitch, X (Twitter), Instagram y más de 1000 plataformas web.

---

## 🌟 Características Destacadas

* 🎨 **Interfaz Futurista & Tema Dark:** Diseñada con `CustomTkinter`, acentos **Azul Eléctrico / Cian Neon (`#00f0ff`)** y componentes visuales modernos.
* 🖱️ **Drag and Drop (Arrastrar y Soltar):** Arrastra cualquier enlace multimedia directamente sobre la aplicación para iniciar la inspección instantánea.
* ⚡ **Arquitectura Multi-Hilo Fluida:** La interfaz gráfica nunca se congela durante la inspección de metadatos o descargas pesadas gracias a `threading` y `queue.Queue`.
* 🎬 **Inspección en Tiempo Real:** Vista previa de miniatura en HD, título, autor, duración exacta, recuento de vistas y insignias de plataforma.
* 🎥 **Máxima Calidad de Vídeo (4K / 2K / 1080p 60fps):** Soporte de resolución adaptable con multiplexado automático a través de `FFmpeg`.
* 🎵 **Extractor de Audio HD (MP3 320 kbps / WAV / FLAC):** Extrae podcasts y pistas de sonido con calidad de estudio.
* 📜 **Historial de Descargas & Acceso Rápido:** Abre la carpeta de destino o los archivos descargados con un solo clic.
* 💻 **Logs en Vivo del Sistema:** Consola integrada para monitorear diagnósticos de extracción en tiempo real.

---

## 🏗️ Arquitectura del Sistema (Clean Architecture)

El proyecto sigue una estructura altamente modular separando la capa de presentación (GUI), el motor de extracción/descarga (Core), y los servicios auxiliares (Utils):

```text
PiDiaDownloader/
│
├── assets/                  # Iconos, logos y recursos gráficos de la app
├── src/
│   ├── __init__.py
│   ├── config.py            # Paleta de colores, rutas predeterminadas y constantes
│   ├── core/
│   │   ├── __init__.py
│   │   ├── downloader.py    # Wrapper de yt-dlp con hooks de progreso en tiempo real
│   │   ├── metadata.py      # Inspección rápida de metadatos sin descargar
│   │   └── ffmpeg_check.py  # Detección y validación del binario global de FFmpeg
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── app.py           # Ventana principal, orquestación de hilos y cola UI
│   │   ├── styles.py        # Tema visual, fuentes y tokens de diseño
│   │   └── components/      # Componentes CTk modulares:
│   │       ├── dropzone.py         # Dropzone de arrastrar/soltar e input URL
│   │       ├── metadata_card.py    # Tarjeta de vista previa con miniatura PIL
│   │       ├── format_selector.py  # Opciones de resolución, formato y carpeta
│   │       ├── progress_card.py    # Barra de progreso, velocidad MB/s y ETA
│   │       └── history_table.py    # Lista de descargas recientes
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py       # Formateo de bytes, duraciones y validación regex
│       └── logger.py        # Logging estructurado con callback para consola GUI
│
├── tests/                   # Suite de pruebas unitarias (pytest / unittest)
├── .gitignore
├── requirements.txt
├── README.md                # Documentación oficial del repositorio
├── main.py                  # Punto de entrada principal
└── build.py                 # Script de empaquetado ejecutable (.exe con PyInstaller)
```

---

## 🛠️ Instalación y Uso Local

### Requisitos Previos

1. **Python 3.11+** instalado.
2. **FFmpeg** (Opcional pero recomendado para multiplexar vídeo 1080p/4K y convertir a MP3 320kbps).

### 1. Clonar el repositorio

```bash
git clone https://github.com/Thepimen/PiDiaDownloader.git
cd PiDiaDownloader
```

### 2. Crear un entorno virtual e instalar dependencias

```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Ejecutar la Aplicación

```bash
python main.py
```

---

## 🧪 Ejecución de Pruebas Unitarias

```bash
pytest tests/
```

---

## 📦 Generar Ejecutable Standalone (`.exe` para Windows)

El proyecto incluye un script automatizado `build.py` estructurado con **PyInstaller**:

```bash
python build.py
```

El ejecutable resultante se guardará en la carpeta `dist/πDiaDownloader/`.

---

## ⚡ Custom Development, Commercial Support & Deployment

Need a custom version of **πDiaDownloader**, a tailored media processing pipeline (`FFmpeg` / `yt-dlp`), custom Python automation scripts, or a standalone `.EXE` desktop application (`CustomTkinter` / `PyInstaller`) built for your business?

I offer fast-turnaround software engineering services and custom proposals on Fiverr:

[![Hire on Fiverr - Python Automation & Desktop Apps](https://img.shields.io/badge/Fiverr-Custom_Python_Automation_%26_.EXE_Apps_(From_$30)-00b22d?style=for-the-badge&logo=fiverr&logoColor=white)](https://www.fiverr.com/thepimen/build-custom-python-automation-scripts-and-standalone-desktop-apps)
[![Fiverr Profile - All Engineering Services](https://img.shields.io/badge/Fiverr_Profile-Request_a_Custom_Offer-1dbf73?style=for-the-badge&logo=fiverr&logoColor=white)](https://www.fiverr.com/thepimen)

* **24-Hour Express Delivery available** for urgent scripts, bug fixes, and desktop tools.
* **Direct Engineering Portfolio & Services:** [luislazaro-dev.netlify.app/solutions](https://luislazaro-dev.netlify.app/solutions)

---

## 📄 Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo `LICENSE` para más información.

