# Bot Gestor de Tareas con IA 🤖

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram_Bot-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![OpenAI Whisper](https://img.shields.io/badge/Whisper-412991?style=for-the-badge&logo=openai&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)

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
