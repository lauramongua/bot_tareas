import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import os

ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_logo = os.path.join(ruta_actual, "logo_empresa.png")

logo_empresa = Image.open(ruta_logo)

#cargar logo de la empresa
st.set_page_config(
    page_title="Dashboard de productividad IA", 
    page_icon=logo_empresa,
    layout = "wide"    
)

#pinto el logo grande arriba de la pagina
st.image(logo_empresa, width=200)

#(CSS) Modificar botones

st.markdown("""
<style>
        div.stButton > button:first-child{
            background-color: #F47B20 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 10px 24px !important;
            font-weight: 700 !important;
            transition: all 0.3s ease !important;
        }
        div.stButton > button:first-child:hover {
            background-color: #d6651a !important;   /* Un naranja un pelín más oscuro para dar feedback */
            transform: translateY(-2px) !important;  /* El botón "flota" 2 píxeles hacia arriba */
            box-shadow: 0 4px 12px rgba(244, 123, 32, 0.3) !important; /* Sombra naranja brillante */
        }
</style>
""", unsafe_allow_html=True)


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

        with st.container(border=True):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(label="Total Tareas", value=int(df_tareas.shape[0]))

            with col2:
                tareas_altas = int((df_tareas['prioridad'] == 'Alta').sum()) 
                st.metric(label="Prioridad Alta 🚨", value=tareas_altas)

            with col3:
                origen_audio = int((df_tareas['origen'] == 'Audio').sum())
                st.metric(label="Indexadas por Voz 🎙️", value=origen_audio)
      
            with col4:
                # Añadimos una cuarta métrica para aprovechar el espacio horizontal
                origen_texto = int((df_tareas['origen'] == 'Texto').sum())
                st.metric(label="Notas de Texto 📝", value=origen_texto)
        #Barra lateral de filtros
        st.sidebar.header("🔍 Filtros de Búsqueda")

        lista_categorias = ["Todas"] + list(df_tareas['categoria'].dropna().unique())
        categoria_sel = st.sidebar.selectbox("Filtrar por Categoría:", lista_categorias)
        
        # Filtro de Prioridad dinámico
        lista_prioridades = ["Todas"] + list(df_tareas['prioridad'].dropna().unique())
        prioridad_sel = st.sidebar.selectbox("Filtrar por Prioridad:", lista_prioridades)

        #Aplico los filtros
        df_filtrado = df_tareas.copy()
        if categoria_sel != "Todas":
            df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_sel]
        if prioridad_sel != "Todas":
            df_filtrado = df_filtrado[df_filtrado['prioridad'] == prioridad_sel]

        # TABLA PRINCIPAL VISUAL
        st.subheader("📋 Listado Actual de Tareas")
        st.dataframe(
            df_filtrado, 
            column_config={
                "id": "ID",
                "titulo": "Título Corto",
                "descripcion": "Descripción Completa (Transcripción)",
                "estado": "Estado Actual",
                "origen": "Canal",
                "fecha": "Fecha Registro",
                "prioridad": "Prioridad IA",
                "categoria": "Categoría IA"
            },
            hide_index=True,
            use_container_width=True
        )
except Exception as e:

    st.error(f"No se pudo conectar con la base de datos: {e}")
    st.info("Asegúrate de haber ejecutado tu 'bot.py' al menos una vez para generar el archivo 'tareas.db'.")