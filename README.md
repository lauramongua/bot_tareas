<div align="center">
  <img width="100%" src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=6,11,20&height=150&section=header&text=Bot%20Gestor%20de%20Tareas%20con%20IA%20%F0%9F%A4%96&fontSize=34&fontColor=fff&fontAlignY=40&desc=Telegram%20%E2%80%A2%20Whisper%20%E2%80%A2%20Ollama%20%E2%80%A2%20SQLite&descAlignY=65&descSize=16" />
</div>

Asistente personal en **Telegram** desarrollado en **Python** que permite capturar tareas mediante **mensajes de texto o notas de voz**, transcribirlas en local y clasificarlas automáticamente usando Inteligencia Artificial antes de guardarlas en una base de datos.

---

### ✨ Características Principales

* **🎙️ Transcripción de voz en local (OpenAI Whisper):** Convierte notas de voz (`.ogg`) enviadas por Telegram a texto en español sin depender de APIs externas de pago, eliminando el archivo temporal tras procesarlo.
* **🧠 Clasificación inteligente con IA (Ollama):** Analiza el contexto del mensaje mediante un modelo LLM (`gpt-oss`) para extraer y asignar automáticamente:
  * **Prioridad:** `Alta`, `Media` o `Baja`.
  * **Categoría:** `Trabajo`, `Personal`, `Universidad`, `Hogar` u `Otros`.
  * **Fecha límite:** Detecta plazos mencionados en lenguaje natural (ej. *"para el martes"*, *"mañana"*).
* **🗄️ Persistencia de datos en SQLite:** Almacena cada tarea de forma estructurada en una base de datos local (`tareas.db`) registrando título, descripción completa, origen (Texto/Audio), fecha de creación y estado.

---

### 🛠️ Tecnologías Utilizadas

<p align="left">
  <a href="https://skillicons.dev">
    <img src="https://skillicons.dev/icons?i=python,sqlite,git,github" />
  </a>
</p>

* **[Python-Telegram-Bot](https://python-telegram-bot.org/):** Gestión asíncrona de comandos (`/start`), mensajes de texto y descarga de notas de voz.
* **[OpenAI Whisper](https://github.com/openai/whisper):** Modelo de reconocimiento de voz ejecutado en local (`base`).
* **[Ollama](https://ollama.com/):** Ejecución e inferencia del modelo de lenguaje en local para el análisis semántico.
* **[SQLite3](https://www.sqlite.org/):** Base de datos relacional ligera integrada en Python.

---

### 🚀 Instalación y Puesta en Marcha

#### 1. Requisitos previos
* Tener instalado **Python 3.9+** y **FFmpeg** (necesario para que Whisper procese audios).
* Tener instalado y ejecutándose **[Ollama](https://ollama.com/)** con el modelo descargado (`ollama run gpt-oss:120b` o el modelo local configurado).
* Obtener un token de bot en Telegram a través de **[@BotFather](https://t.me/botfather)**.

#### 2. Clonar e instalar dependencias
```bash
git clone [https://github.com/lauramongua/bot_tareas.git](https://github.com/lauramongua/bot_tareas.git)
cd bot_tareas
pip install python-telegram-bot openai-whisper ollama
