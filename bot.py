# importación de clases o librerias
import os  # es necesario para borrar el archivo de audio temporal
import logging
import sqlite3 
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import whisper # Librería para transcribir audio en local
import ollama #libreria para conectar con gpt-oss

# Configuración de logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

# Cargamos el modelo Whisper en la RAM del servidor
modelo_whisper = whisper.load_model("base")

TOKEN_DEL_BOT = "8960206600:AAEn_qf4qD9NHiU2Qq3p0MDlkB1qC8F1684"


# FUNCIONES DE LA BASE DE DATOS 


def conectar_db():
    """Función para conectar a la base de datos de forma segura."""
    return sqlite3.connect("tareas.db")

def inicializar_base_de_datos():
    """Crea la tabla de tareas si no existe en el sistema."""
    conexion = conectar_db()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            estado TEXT DEFAULT 'Bandeja de entrada',
            origen TEXT,
            fecha TEXT
        )
    """)
    conexion.commit() # Guardar cambios en el disco
    conexion.close()  # Cerrar la conexión
    print("Base de datos verificada e inicializada correctamente.")

def guardar_tarea(titulo, descripcion, origen, prioridad, categoria):
    """Guarda los datos de la tarea en SQLite"""
    conexion = conectar_db()
    cursor = conexion.cursor()
    fecha_actual = datetime.now().strftime("%d %b %H:%M")

    try:
        cursor.execute("""
            INSERT INTO tareas (titulo, descripcion, estado, origen, fecha, prioridad, categoria)
            VALUES (?, ?, 'Bandeja de entrada', ?, ?)
        """, (titulo, descripcion, origen, fecha_actual, prioridad, categoria))
        conexion.commit()  # SÍ hacemos commit porque la inserción ha sido limpia
    finally:
        conexion.close()   # Se cierra SIEMPRE de forma segura (Corregido el doble commit)

#FUNCION DE IA OLLAMA
def analizar_tarea_con_ia(texto):
    """Envía la tarea al gpt-oss para extraer la prioridad y la categoría."""
    prompt_instrucciones = (
        f"Eres un asistente de IA experto en productividad. Analiza la siguiente tarea del usuario y clasifícala.\n\n"
        f"Tarea: '{texto}'\n\n"
        f"REGLAS DE SALIDA OBLIGATORIAS:\n"
        f"1. Elige una prioridad de estas tres opciones: Alta, Media, Baja.\n"
        f"2. Elige una categoría de estas opciones: Trabajo, Personal, Universidad, Hogar, Otros.\n"
        f"3. Tu respuesta debe tener ÚNICAMENTE este formato exacto, sin introducciones ni explicaciones: PRIORIDAD/CATEGORÍA\n\n"
        f"Ejemplo de respuesta correcta: Alta/Trabajo"

    )

    try:
        respuesta_ia = ollama.generate(model='gpt-oss:120b', prompt=prompt_instrucciones)
        resultado_limpio = respuesta_ia['response'].strip()

        prioridad, cargoria = resultado_limpio.split('/')
        return prioridad.strip(), categoria.strip()
    
    except Exception as e:
        print("Error al persear ollama:")
        return "media", "otros"



# CONTROLADORES DE TELEGRAM (Handlers)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): # Corregido 'contaext'
    await update.message.reply_text(
        "¡Hola ! Estoy lista para guardar tus ideas. Envíame cualquier nota de texto o grábame un audio."
    )

async def manejar_texto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text 

    # 1. Avisamos al usuario que estamos procesando con Ollama
    mensaje_espera = await update.message.reply_text("🧠 Analizando contenido con la IA...")

    # 2. Llamamos a Ollama para clasificar la tarea en segundo plano
    prioridad, categoria = analizar_tarea_con_ia(texto_usuario)

    palabras = texto_usuario.split() 
    titulo_corto = " ".join(palabras[:5]) + "..." if len(palabras) > 5 else texto_usuario
        
    try:
        # 3. Guardamos pasando la prioridad y categoría encontradas
        guardar_tarea(titulo=titulo_corto, descripcion=texto_usuario, origen="Texto", prioridad=prioridad, categoria=categoria)
            
        respuesta = (
            f"✅ *Tarea guardada con Inteligencia Artificial*\n\n"
            f"*Título:* {titulo_corto}\n"
            f"*Prioridad:* {prioridad}\n"
            f"*Categoría:* {categoria}\n"
            f"*Estado:* Bandeja de entrada"
        )
        # Editamos el mensaje de espera en vez de mandar uno nuevo para que quede elegante
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=mensaje_espera.message_id, text=respuesta, parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"Hubo un error al guardar: {e}")




async def manejar_audio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Descarga una nota de voz, la transcribe con Whisper y la clasifica con Ollama."""
    mensaje_espera = await update.message.reply_text(" Traduciendo audio a texto en local...")

    archivo_id = update.message.voice.file_id
    archivo_telegram = await context.bot.get_file(archivo_id)
    ruta_audio = "audio_temporal.ogg"
    await archivo_telegram.download_to_drive(ruta_audio)

    try:
        # 1. Transcribir con Whisper
        resultado = modelo_whisper.transcribe(ruta_audio, language="es")
        texto_transcrito = resultado["text"].strip()

        if not texto_transcrito:
            await update.message.reply_text("No he podido extraer texto de este audio. ¿Está vacío?")
            return

        # 2. Actualizar estado y analizar con Ollama
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=mensaje_espera.message_id, text="🧠 Entendiendo el contexto de la tarea con Ollama...")
        prioridad, categoria = analizar_tarea_con_ia(texto_transcrito)

        palabras = texto_transcrito.split()
        titulo_corto = " ".join(palabras[:5]) + "..." if len(palabras) > 5 else texto_transcrito

        # 3. Guardar en Base de Datos
        guardar_tarea(titulo=titulo_corto, descripcion=texto_transcrito, origen="Audio", prioridad=prioridad, categoria=categoria)

        respuesta = (
            f"🎙️ *¡Audio guardado y clasificado!*\n\n"
            f"*Transcripción:* {texto_transcrito}\n\n"
            f"*Prioridad asignada:* {prioridad}\n"
            f"*Categoría asignada:* {categoria}"
        )
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=mensaje_espera.message_id, text=respuesta, parse_mode="Markdown")

    except Exception as e:
        await update.message.reply_text(f"Error en el módulo de voz/IA: {e}")
    finally:
        if os.path.exists(ruta_audio):
            os.remove(ruta_audio)

# FUNCIÓN PRINCIPAL
def main():
    inicializar_base_de_datos()

    application = Application.builder().token(TOKEN_DEL_BOT).build()

    # Registramos los comandos y oyentes
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, manejar_texto))
    application.add_handler(MessageHandler(filters.VOICE, manejar_audio)) # <-- Registramos el oyente de voz

    print("Bot iniciado... Presiona Ctrl+C para detenerlo.")
    application.run_polling()

if __name__ == '__main__':
    main()