import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image

logo_empresa = Image.open("logo_empresa.png")

#cargar logo de la empresa
st.set_page_config(
    page_title="Dashboard de productividad IA", 
    page_icon=logo_empresa,
    layout = "wide"    
)

#extrae los datos con Pandas
def cargar_datos():
    conexion = sqlite3.connect("tareas.db")
    query = "SELECT id, titulo, descripcion, estado, origen, fecha, prioridad, categoria FROM tareas ORDER BY id DESC"
    df = pd.read_sql_query(query, conexion)
    conexion.close()
    return df

try:
    df_tareas = cargar_datos()


    #Compruebo si la tabla tiene registros
    if df_tareas.empty:
        st.info("La base de datos está vacía. ¡Mándale un mensaje o audio al bot de Telegram para empezar!")
    else:
        st.title("Centro de Control de Tareas")
        st.markdown("Bienvenida a tu panel de control.")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(label="Total Tareas", value= len(df_tareas))
        with col2:
            tareas_altas = len(df_tareas[df_tareas['prioridad'] == 'Alta'])
            st.metric(label="Prioridad Alta !!", value=tareas_altas)
        with col3:
            origen_audio = len(df_tareas[df_tareas['origen'] == 'Audio'])
            st.metric(label="Indexadas por Voz 🎙️", value=origen_audio)
 
        st.divider()

        #Barra lateral de filtros
        st.sidebar.header("🔍 Filtros de Búsqueda")

        lista_categorias

