import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import os
from datetime import datetime

ruta_actual = os.path.dirname(os.path.abspath(__file__))
ruta_logo = os.path.join(ruta_actual, "logo_empresa.png")

logo_empresa = Image.open(ruta_logo)

# Configurar la página
st.set_page_config(
    page_title="Dashboard de productividad IA", 
    page_icon=logo_empresa,
    layout="wide"    
)

# Pintar el logo grande arriba de la página
st.image(logo_empresa, width=150)

# (CSS) Modificar botones, métricas y pestañas premium
st.markdown("""
<style>
        div.stButton > button:first-child{
            background-color: #F47B20 !important;
            color: white !important;
            border: none !important;
            border-radius: 8px !important;
            padding: 8px 16px !important;
            font-weight: 700 !important;
            transition: all 0.3s ease !important;
        }
        div.stButton > button:first-child:hover {
            background-color: #d6651a !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 12px rgba(244, 123, 32, 0.3) !important;
        }
        
        [data-testid="stMetric"] {
            background-color: transparent !important;
            box-shadow: none !important;
            border: none !important;
            padding-left: 15px !important;
        }
        [data-testid="stMetricVBox"] {
            border-right: 1px solid rgba(128, 128, 128, 0.2) !important;
        }
        div[data-testid="stHorizontalBlock"] > div:last-child [data-testid="stMetricVBox"] {
            border-right: none !important;
        }

        /* --- ESTILO DE PESTAÑAS DE ESTADO PREMIUM --- */
        div[data-testid="stTabBar"] {
            background-color: rgba(255, 255, 255, 0.03) !important;
            padding: 8px 16px !important;
            border-radius: 12px !important;
            border: 1px solid rgba(128, 128, 128, 0.1) !important;
            margin-bottom: 25px !important;
            gap: 20px !important;
        }

        div[data-testid="stTabBar"] button {
            font-size: 15px !important;
            font-weight: 600 !important;
            padding: 8px 20px !important;
            border-radius: 8px !important;
            transition: all 0.3s ease !important;
            color: #888888 !important;
        }

        div[data-testid="stTabBar"] button:hover {
            color: #ffffff !important;
            background-color: rgba(255, 255, 255, 0.05) !important;
        }

        div[data-testid="stTabBar"] button[aria-selected="true"] {
            color: white !important;
            background-color: #F47B20 !important;
            box-shadow: 0 4px 12px rgba(244, 123, 32, 0.2) !important;
        }

        div[data-testid="stTabBarTabIndicator"] {
            background-color: transparent !important;
        }
</style>
""", unsafe_allow_html=True)


# Extrae los datos con Pandas
def cargar_datos():
    conexion = sqlite3.connect("tareas.db")
    
    # Aseguramos que exista la columna fecha_limite en la tabla tareas
    cursor = conexion.cursor()
    try:
        cursor.execute("ALTER TABLE tareas ADD COLUMN fecha_limite TEXT")
        conexion.commit()
    except sqlite3.OperationalError:
        pass 
        
    df = pd.read_sql_query("SELECT * FROM tareas ORDER BY id DESC", conexion)
    conexion.close()
    return df

# Marcar tarea como completada
def marcar_tarea_completada(id_tarea):
    conexion = sqlite3.connect("tareas.db")
    cursor = conexion.cursor()
    cursor.execute("UPDATE tareas SET estado = 'Completada' WHERE id = ?", (id_tarea,))
    conexion.commit()
    conexion.close()
    st.rerun()

# Actualizar manualmente la fecha límite desde el panel
def actualizar_fecha_limite(id_tarea, nueva_fecha):
    conexion = sqlite3.connect("tareas.db")
    cursor = conexion.cursor()
    cursor.execute("UPDATE tareas SET fecha_limite = ? WHERE id = ?", (nueva_fecha, id_tarea))
    conexion.commit()
    conexion.close()
    st.rerun()

# Agregar nueva categoría
def guardar_nueva_categoria(nombre_cat):
    conexion = sqlite3.connect("tareas.db")
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                nombre TEXT UNIQUE
        )                                  
    """)
    try:
        cursor.execute("INSERT INTO categorias (nombre) VALUES (?)", (nombre_cat.strip(),))
        conexion.commit()
    except sqlite3.IntegrityError:
        pass
    conexion.close()
    st.rerun()


try:
    df_tareas = cargar_datos()

    if df_tareas.empty:
        st.info("La base de datos está vacía. ¡Mándale un mensaje o audio al bot de Telegram para empezar!")
    else:
        st.title("Centro de Control de Tareas")
        st.markdown("Bienvenida a tu panel de control.")

        # Contenedor de métricas unificadas (Solo cuenta las pendientes)
        df_pendientes_count = df_tareas[df_tareas['estado'] != 'Completada']
        
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(label="Tareas Pendientes", value=int(df_pendientes_count.shape[0]))

            with col2:
                tareas_altas = int((df_pendientes_count['prioridad'] == 'Alta').sum()) 
                st.metric(label="Prioridad Alta 🚨", value=tareas_altas)

            with col3:
                origen_audio = int((df_pendientes_count['origen'] == 'Audio').sum())
                st.metric(label="Por Voz 🎙️", value=origen_audio)
                
            with col4:
                origen_texto = int((df_pendientes_count['origen'] == 'Texto').sum())
                st.metric(label="Por Texto 📝", value=origen_texto)
      
        # === BARRA LATERAL ===
        st.sidebar.header("🔍 Filtros de Búsqueda")

        try:
            conexion = sqlite3.connect("tareas.db")
            cursor = conexion.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS categorias (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE)")
            df_cat_custom = pd.read_sql_query("SELECT nombre FROM categorias", conexion)
            conexion.close()
            lista_custom = list(df_cat_custom['nombre'].dropna().unique())
        except Exception:
            lista_custom = []

        # Fusionamos categorías
        categorias_totales = list(df_tareas['categoria'].dropna().unique()) + lista_custom
        lista_categorias = ["Todas"] + list(set(categorias_totales))
        
        categoria_sel = st.sidebar.selectbox("Filtrar por Categoría:", lista_categorias)
        
        lista_prioridades = ["Todas"] + list(df_tareas['prioridad'].dropna().unique())
        prioridad_sel = st.sidebar.selectbox("Filtrar por Prioridad:", lista_prioridades)

        st.sidebar.divider()

        st.sidebar.subheader("➕ Nueva Categoría")
        with st.sidebar.form(key="form_nueva_categoria", clear_on_submit=True):
            nueva_cat = st.text_input("Nombre de la categoría:", placeholder="Ej: Finanzas, Personal...")
            boton_crear = st.form_submit_button("Añadir Categoría")
            
            if boton_crear and nueva_cat:
                guardar_nueva_categoria(nueva_cat)

        # === PROCESAMIENTO DE FILTROS ===
        df_filtrado = df_tareas.copy()
        if categoria_sel != "Todas":
            df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_sel]
        if prioridad_sel != "Todas":
            df_filtrado = df_filtrado[df_filtrado['prioridad'] == prioridad_sel]


        # === SISTEMA DE ESTADOS PREMIUM ===
        st.markdown("<br>", unsafe_allow_html=True)
        
        tab_pendientes, tab_completadas, tab_todas = st.tabs([
            "Bandeja de Entrada", 
            "Completadas", 
            "Todas las Tareas"
        ])
        
        # Función interna para renderizar las tarjetas estilizadas
        def renderizar_tarjetas(df_sub, es_completada=False, prefijo=""):
            if df_sub.empty:
                st.info("No hay tareas en esta sección con los filtros aplicados. 🎉")
                return
                
            for index, fila in df_sub.iterrows():
                if fila['prioridad'] == "Alta":
                    color_p = "#ff4b4b"
                elif fila['prioridad'] == "Media":
                    color_p = "#f47b20"
                else:
                    color_p = "#25b882"
                
                # Gestión visual de la fecha límite
                tiene_fecha = 'fecha_limite' in fila and fila['fecha_limite'] and fila['fecha_limite'] != "Sin fecha"
                f_limite = fila['fecha_limite'] if tiene_fecha else "Sin fecha"
                
                with st.container(border=True):
                    col_txt, col_act = st.columns([4.2, 1.5])
                    
                    with col_txt:
                        # Badges superiores
                        st.markdown(f"""
                            <div style='display: flex; gap: 8px; margin-bottom: 12px; align-items: center;'>
                                <span style='background-color: {color_p}15; color: {color_p}; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: bold; border: 1px solid {color_p}30;'>
                                    ● {fila['prioridad']}
                                </span>
                                <span style='background-color: rgba(244, 123, 32, 0.1); color: #F47B20; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;'>
                                    📦 {fila['categoria']}
                                </span>
                                <span style='background-color: rgba(255, 75, 75, 0.1); color: #ff4b4b; padding: 2px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;'>
                                    ⏳ Límite: {f_limite}
                                </span>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if es_completada or fila['estado'] == 'Completada':
                            st.markdown(f"<h3 style='margin:0; font-size:17px; font-weight:700; text-decoration: line-through; color: #555555;'>{fila['titulo']}</h3>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<h3 style='margin:0; font-size:17px; font-weight:700; color: #ffffff;'>{fila['titulo']}</h3>", unsafe_allow_html=True)
                            
                        st.markdown(f"<p style='margin: 6px 0; font-size: 13.5px; color: #999999; line-height: 1.4;'>{fila['descripcion']}</p>", unsafe_allow_html=True)
                        st.caption(f"⏱️ Creada el: {fila['fecha']} | Canal: { '🎙️ Voz' if fila['origen'] == 'Audio' else '📝 Texto' }")
                    
                    with col_act:
                        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                        
                        if not es_completada and fila['estado'] != 'Completada':
                            # Reemplazamos el calendario pesado por un input de texto ligero
                            nueva_f = st.text_input("Editar plazo:", value=str(f_limite), key=f"inp_{prefijo}_{fila['id']}")
                            
                            col_b1, col_b2 = st.columns(2)
                            with col_b1:
                                if st.button("💾", key=f"set_{prefijo}_{fila['id']}", help="Guardar fecha", use_container_width=True):
                                    actualizar_fecha_limite(fila['id'], nueva_f)
                            with col_b2:
                                if st.button("✔️", key=f"{prefijo}_btn_{fila['id']}", help="Completar tarea", use_container_width=True):
                                    marcar_tarea_completada(fila['id'])
                        else:
                            st.markdown("<div style='text-align: center; color: #25b882; font-weight: bold; font-size: 14px; padding-top: 25px;'>✨ Hecha</div>", unsafe_allow_html=True)
                
                st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

        # Distribuir las tareas en las bandejas
        with tab_pendientes:
            df_pend = df_filtrado[df_filtrado['estado'] != 'Completada'] if not df_filtrado.empty else pd.DataFrame()
            renderizar_tarjetas(df_pend, es_completada=False, prefijo="pend")
            
        with tab_completadas:
            df_comp = df_filtrado[df_filtrado['estado'] == 'Completada'] if not df_filtrado.empty else pd.DataFrame()
            renderizar_tarjetas(df_comp, es_completada=True, prefijo="comp")
            
        with tab_todas:
            renderizar_tarjetas(df_filtrado, es_completada=False, prefijo="todas")
       
except Exception as e:
    st.error(f"Error en la aplicación: {e}")