import streamlit as st
import sqlite3
import pandas as pd
from PIL import Image
import os
import time
from datetime import datetime

# === CONFIGURACIONES INICIALES ===
ruta_actual = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="Dashboard de productividad IA", 
    layout="wide"    
)

# === INITIALIZE SESSION STATE FOR POMODORO ===
if "pomodoro_time" not in st.session_state:
    st.session_state.pomodoro_time = 25 * 60
if "pomodoro_active" not in st.session_state:
    st.session_state.pomodoro_active = False

# === CARGA DE ESTILOS CSS EXTERNOS ===
def cargar_css(archivo_css):
    if os.path.exists(archivo_css):
        with open(archivo_css, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Cargamos el archivo style.css
cargar_css(os.path.join(ruta_actual, "style.css"))

# === 🛠️ FUNCIONES DE CONTROL DE DATOS ===

def cargar_datos():
    conexion = sqlite3.connect("tareas.db")
    cursor = conexion.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT,
            descripcion TEXT,
            categoria TEXT,
            prioridad TEXT,
            estado TEXT,
            fecha TEXT,
            origen TEXT,
            fecha_limite TEXT
        )
    """)
    
    try:
        cursor.execute("ALTER TABLE tareas ADD COLUMN fecha_limite TEXT")
        conexion.commit()
    except sqlite3.OperationalError:
        pass 
        
    df = pd.read_sql_query("SELECT * FROM tareas ORDER BY id DESC", conexion)
    conexion.close()
    return df

def marcar_tarea_completada(id_tarea):
    conexion = sqlite3.connect("tareas.db")
    cursor = conexion.cursor()
    cursor.execute("UPDATE tareas SET estado = 'Completada' WHERE id = ?", (id_tarea,))
    conexion.commit()
    conexion.close()
    st.rerun()

def actualizar_fecha_limite(id_tarea, nueva_fecha):
    conexion = sqlite3.connect("tareas.db")
    cursor = conexion.cursor()
    cursor.execute("UPDATE tareas SET fecha_limite = ? WHERE id = ?", (nueva_fecha, id_tarea))
    conexion.commit()
    conexion.close()
    st.rerun()

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

def eliminar_tarea(id_tarea):
    conexion = sqlite3.connect("tareas.db")
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM tareas WHERE id = ?", (id_tarea,))
    conexion.commit()
    conexion.close()
    st.rerun()

def renderizar_tarjetas(df_sub, es_completada=False, prefijo=""):
    if df_sub.empty:
        st.info("No hay tareas en esta sección.")
        return
        
    for index, fila in df_sub.iterrows():
        if fila['prioridad'] == "Alta":
            color_p = "#ff4b4b"
        elif fila['prioridad'] == "Media":
            color_p = "#f47b20"
        else:
            color_p = "#25b882"
        
        tiene_fecha = 'fecha_limite' in fila and fila['fecha_limite'] and fila['fecha_limite'] != "Sin fecha"
        f_limite = fila['fecha_limite'] if tiene_fecha else "Sin fecha"
        
        with st.container(border=True):
            col_txt, col_act = st.columns([4.2, 1.8])
            
            with col_txt:
                st.markdown(f"""
                    <div style='display: flex; gap: 4px; margin-bottom: 2px; align-items: center; flex-wrap: wrap;'>
                        <span style='background-color: {color_p}15; color: {color_p}; padding: 1px 5px; border-radius: 10px; font-size: 10px; font-weight: bold; border: 1px solid {color_p}30;'>
                            ● {fila['prioridad']}
                        </span>
                        <span style='background-color: rgba(244, 123, 32, 0.1); color: #F47B20; padding: 1px 5px; border-radius: 10px; font-size: 10px; font-weight: 600;'>
                            📦 {fila['categoria']}
                        </span>
                        <span style='background-color: rgba(255, 75, 75, 0.1); color: #ff4b4b; padding: 1px 5px; border-radius: 10px; font-size: 10px; font-weight: bold;'>
                            ⏳ Límite: {f_limite}
                        </span>
                    </div>
                """, unsafe_allow_html=True)
                
                if es_completada or fila['estado'] == 'Completada':
                    st.markdown(f"<h3 style='margin:0; text-decoration: line-through; color: #555555;'>{fila['titulo']}</h3>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<h3 style='margin:0; color: #ffffff;'>{fila['titulo']}</h3>", unsafe_allow_html=True)
                    
                st.markdown(f"<p style='margin: 1px 0; font-size: 12px; color: #aaaaaa; line-height: 1.3;'>{fila['descripcion']}</p>", unsafe_allow_html=True)
                st.caption(f"⏱️ {fila['fecha']} | Canal: { '🎙️ Voz' if fila['origen'] == 'Audio' else '📝 Texto' }")
            
            with col_act:
                if not es_completada and fila['estado'] != 'Completada':
                    st.markdown('<div class="tarjeta-plazo">', unsafe_allow_html=True)
                    nueva_f = st.text_input("Editar plazo:", value=str(f_limite), key=f"inp_{prefijo}_{fila['id']}", label_visibility="collapsed")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('<div class="tarjeta-acciones">', unsafe_allow_html=True)
                    col_b1, col_b2, col_b3 = st.columns(3)
                    with col_b1:
                        if st.button("💾", key=f"set_{prefijo}_{fila['id']}", help="Guardar", use_container_width=True):
                            actualizar_fecha_limite(fila['id'], nueva_f)
                    with col_b2:
                        if st.button("✔️", key=f"{prefijo}_btn_{fila['id']}", help="Completar", use_container_width=True):
                            marcar_tarea_completada(fila['id'])
                    with col_b3:
                        if st.button("🗑️", key=f"del_{prefijo}_{fila['id']}", help="Eliminar", use_container_width=True):
                            eliminar_tarea(fila['id'])
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="tarjeta-acciones">', unsafe_allow_html=True)
                    col_c1, col_c2 = st.columns([1.5, 1])
                    with col_c1:
                        st.markdown("<div style='color: #25b882; font-weight: bold; font-size: 11px; padding-top: 4px;'>✨ Hecha</div>", unsafe_allow_html=True)
                    with col_c2:
                        if st.button("🗑️", key=f"del_{prefijo}_{fila['id']}", help="Eliminar", use_container_width=True):
                            eliminar_tarea(fila['id'])
                    st.markdown('</div>', unsafe_allow_html=True)

# === DICTAMEN DE DISTRIBUCIÓN DE PANTALLA ===
try:
    df_tareas = cargar_datos()

    # CORRECCIÓN AQUÍ: Usamos un escalado nativo más holgado en responsividad [1.2, 4.8] en lugar de fijos agresivos
    col_menu_lateral, col_contenido_principal = st.columns([1.2, 4.8], gap="medium")

    # 1. BLOQUE DE LA BARRA LATERAL FIJA (COLUMNA IZQUIERDA)
    with col_menu_lateral:
        # Añadimos un div HTML contenedor personalizado para pintarlo desde el CSS de forma ultra segura
        st.markdown('<div class="mi-sidebar-custom">', unsafe_allow_html=True)
        
        st.markdown("⚙️ **Configuración**")
        modo_productividad = st.selectbox(
            "Enfoque de Vista:",
            ["Bandeja Estándar", "Tablero Kanban", "Maratoniano (Time Blocking)", "Creativo (Eisenhower)"],
            key="vista_sel_fija",
            label_visibility="collapsed"
        )
        
        st.markdown("<br>🔍 **Filtros**", unsafe_allow_html=True)
        try:
            conexion = sqlite3.connect("tareas.db")
            cursor = conexion.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS categorias (id INTEGER PRIMARY KEY AUTOINCREMENT, nombre TEXT UNIQUE)")
            df_cat_custom = pd.read_sql_query("SELECT nombre FROM categorias", conexion)
            conexion.close()
            lista_custom = list(df_cat_custom['nombre'].dropna().unique())
        except Exception:
            lista_custom = []

        categorias_existentes = list(df_tareas['categoria'].dropna().unique()) if not df_tareas.empty else []
        prioridades_existentes = list(df_tareas['prioridad'].dropna().unique()) if not df_tareas.empty else []

        categorias_totales = categorias_existentes + lista_custom
        lista_categorias = ["Todas"] + list(set(categorias_totales))
        categoria_sel = st.selectbox("Categoría:", lista_categorias, key="cat_sel_fija")
        
        lista_prioridades = ["Todas"] + prioridades_existentes
        prioridad_sel = st.selectbox("Prioridad:", lista_prioridades, key="prio_sel_fija")

        st.markdown("<br>➕ **Categoría**", unsafe_allow_html=True)
        with st.form(key="form_nueva_categoria_fija", clear_on_submit=True):
            nueva_cat = st.text_input("Nombre:", placeholder="Ej: Finanzas", label_visibility="collapsed")
            boton_crear = st.form_submit_button("Añadir Categoría", use_container_width=True)
            if boton_crear and nueva_cat:
                guardar_nueva_categoria(nueva_cat)

        # SECCIÓN DE NOTAS RÁPIDAS
        st.markdown("<br>📝 **Añadir una Nota**", unsafe_allow_html=True)
        with st.form(key="form_nueva_nota_fija", clear_on_submit=True):
            nota_texto = st.text_area("Nueva Nota", key="input_nota_rapida", label_visibility="collapsed")
            boton_guardar_nota = st.form_submit_button("Guardar Nota", use_container_width=True)
            
            if boton_guardar_nota:
                if nota_texto.strip() != "":
                    try:
                        conn = sqlite3.connect("tareas.db")
                        c = conn.cursor()
                        
                        titulo_reducido = nota_texto[:50] + "..." if len(nota_texto) > 50 else nota_texto
                        fecha_creacion = datetime.now().strftime("%d %b %H:%M")
                        
                        c.execute("""
                            INSERT INTO tareas (titulo, descripcion, categoria, prioridad, estado, fecha, origen, fecha_limite)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (titulo_reducido.strip(), nota_texto.strip(), "Bandeja de entrada", "Media", "Por hacer", fecha_creacion, "Texto", "Sin fecha"))
                        
                        conn.commit()
                        conn.close()
                        
                        st.toast("📌 ¡Nota guardada como nueva tarea!", icon="🚀")
                        time.sleep(0.5)
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"Error al transformar nota en tarea: {e}")
                else:
                    st.warning("Escribe algo antes de guardar.")
                    
        st.markdown('</div>', unsafe_allow_html=True) # Cierre mi-sidebar-custom

    # 2. BLOQUE DE CONTENIDO PRINCIPAL (COLUMNA DERECHA)
    with col_contenido_principal:
        st.title("Centro de Control de Tareas")

        total_pendientes = 0
        total_altas = 0
        total_audio = 0
        total_texto = 0
        df_filtrado = pd.DataFrame()

        if not df_tareas.empty:
            df_filtrado = df_tareas.copy()
            if categoria_sel != "Todas":
                df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria_sel]
            if prioridad_sel != "Todas":
                df_filtrado = df_filtrado[df_filtrado['prioridad'] == prioridad_sel]

            df_pendientes_count = df_filtrado[df_filtrado['estado'] != 'Completada']
            total_pendientes = int(df_pendientes_count.shape[0])
            total_altas = int((df_pendientes_count['prioridad'] == 'Alta').sum())
            total_audio = int((df_pendientes_count['origen'] == 'Audio').sum())
            total_texto = int((df_pendientes_count['origen'] == 'Texto').sum())

        # SUB-BLOQUE: MÉTRICAS + POMODORO UNIFICADO
        col_dash_izq, col_pomo_der = st.columns([3.2, 0.8])
        
        with col_dash_izq:
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns(4)
                with c1: st.metric(label="Tareas Pendientes", value=total_pendientes)
                with c2: st.metric(label="Prioridad Alta 🚨", value=total_altas)
                with c3: st.metric(label="Por Voz 🎙️", value=total_audio)
                with c4: st.metric(label="Por Texto 📝", value=total_texto)
        
        with col_pomo_der:
            with st.container(border=True):
                @st.fragment(run_every=1 if st.session_state.pomodoro_active else None)
                def render_pomodoro_panel():
                    if st.session_state.pomodoro_active and st.session_state.pomodoro_time > 0:
                        st.session_state.pomodoro_time -= 1
                        if st.session_state.pomodoro_time == 0:
                            st.session_state.pomodoro_active = False
                            st.toast("🎉 ¡Pomodoro Completado!", icon="🚀")

                    mins, secs = divmod(st.session_state.pomodoro_time, 60)
                    st.markdown(f"<h3 style='text-align: center; color: #F47B20; font-family: monospace; margin: 0px 0 2px 0;'>⏱️ {mins:02d}:{secs:02d}</h3>", unsafe_allow_html=True)
                    
                    cp1, cp2 = st.columns(2)
                    with cp1:
                        etiqueta_boton = "⏸️ " if st.session_state.pomodoro_active else "▶️"
                        if st.button(etiqueta_boton, use_container_width=True, key="p_start"):
                            st.session_state.pomodoro_active = not st.session_state.pomodoro_active
                            st.rerun()
                    with cp2:
                        if st.button("🔄", use_container_width=True, key="p_reset"):
                            st.session_state.pomodoro_time = 25 * 60
                            st.session_state.pomodoro_active = False
                            st.rerun()
                render_pomodoro_panel()

        st.markdown("<hr style='margin:10px 0; border-color:rgba(128,128,128,0.1);'>", unsafe_allow_html=True)

        if df_tareas.empty:
            st.info("La sección de tareas está vacía. ¡Mándale un mensaje o audio al bot de Telegram para empezar a poblarla!")
        else:
            df_pendientes = df_filtrado[df_filtrado['estado'] != 'Completada'] if not df_filtrado.empty else pd.DataFrame()

            # VISTAS OPERATIVAS SEGÚN ENFOQUE SELECCIONADO
            if modo_productividad == "Bandeja Estándar":
                tab_pendientes, tab_completadas, tab_todas = st.tabs(["Bandeja de Entrada", "Completadas", "Todas las Tareas"])
                with tab_pendientes: renderizar_tarjetas(df_pendientes, es_completada=False, prefijo="pend")
                with tab_completadas: renderizar_tarjetas(df_filtrado[df_filtrado['estado'] == 'Completada'] if not df_filtrado.empty else pd.DataFrame(), es_completada=True, prefijo="comp")
                with tab_todas: renderizar_tarjetas(df_filtrado, es_completada=False, prefijo="todas")
            
            elif modo_productividad == "Tablero Kanban":
                st.subheader("Tablero Kanban Operativo")
                col_todo, col_doing, col_done = st.columns(3)

                with col_todo:
                    st.markdown("<h4 style='color: #ff4b4b; text-align: center; border-bottom: 2px solid #ff4b4b; padding-bottom: 3px;'>⏳ Por Hacer</h4>", unsafe_allow_html=True)
                    df_todo = df_filtrado[(df_filtrado['estado'] != 'Completada') & (df_filtrado['estado'] != 'En Progreso')] if not df_filtrado.empty else pd.DataFrame()
                    if df_todo.empty: st.caption("No hay tareas.")
                    else:
                        for _, t in df_todo.iterrows():
                            with st.container(border=True):
                                st.markdown(f"**{t['titulo']}**")
                                st.caption(f"📦 {t['categoria']} | 🚨 {t['prioridad']}")
                                st.markdown('<div class="tarjeta-acciones">', unsafe_allow_html=True)
                                if st.button("🚀 Iniciar", key=f"kb_prog_{t['id']}", use_container_width=True):
                                    conexion = sqlite3.connect("tareas.db")
                                    cursor = conexion.cursor()
                                    cursor.execute("UPDATE tareas SET estado = 'En Progreso' WHERE id = ?", (t['id'],))
                                    conexion.commit(); conexion.close(); st.rerun()
                                st.markdown('</div>', unsafe_allow_html=True)

                with col_doing:
                    st.markdown("<h4 style='color: #f47b20; text-align: center; border-bottom: 2px solid #f47b20; padding-bottom: 3px;'>⚡ En Progreso</h4>", unsafe_allow_html=True)
                    df_doing = df_filtrado[df_filtrado['estado'] == 'En Progreso'] if not df_filtrado.empty else pd.DataFrame()
                    if df_doing.empty: st.caption("No hay tareas en progreso.")
                    else:
                        for _, t in df_doing.iterrows():
                            with st.container(border=True):
                                st.markdown(f"**{t['titulo']}**")
                                st.caption(f"📦 {t['categoria']} | 🚨 {t['prioridad']}")
                                st.markdown('<div class="tarjeta-acciones">', unsafe_allow_html=True)
                                if st.button("✔️ Terminar", key=f"kb_done_{t['id']}", use_container_width=True): marcar_tarea_completada(t['id'])
                                st.markdown('</div>', unsafe_allow_html=True)

                with col_done:
                    st.markdown("<h4 style='color: #25b882; text-align: center; border-bottom: 2px solid #25b882; padding-bottom: 3px;'>✨ Hechas</h4>", unsafe_allow_html=True)
                    df_done = df_filtrado[df_filtrado['estado'] == 'Completada'] if not df_filtrado.empty else pd.DataFrame()
                    if df_done.empty: st.caption("Ninguna tarea completada.")
                    else:
                        for _, t in df_done.iterrows():
                            with st.container(border=True):
                                st.markdown(f"<span style='text-decoration: line-through; color: #777;'>{t['titulo']}</span>", unsafe_allow_html=True)
                                st.caption(f"📦 {t['categoria']}")

            elif modo_productividad == "Maratoniano (Time Blocking)":
                st.subheader("Agenda Dinámica por Bloques")
                if df_pendientes.empty: st.success("¡No hay tareas pendientes! 🎉")
                else:
                    hora_inicio = 9
                    for index, fila in df_pendientes.iterrows():
                        col_horas, col_bloques = st.columns([1, 5])
                        with col_horas:
                            st.markdown(f"<p style='padding: 8px 0; font-weight: bold; color: #F47B20;'>{hora_inicio:02d}:00 - {hora_inicio+1:02d}:00</p>", unsafe_allow_html=True)
                            hora_inicio += 1
                        with col_bloques:
                            with st.container(border=True):
                                st.markdown(f"**Bloque: {fila['titulo']}**")
                                st.markdown(f"<p style='color: #999; font-size:12px; margin: 0;'>{fila['descripcion']}</p>", unsafe_allow_html=True)
                                if st.button(" ✔️ Completar ", key=f"time_btn_{fila['id']}"): marcar_tarea_completada(fila['id'])

            elif modo_productividad == "Creativo (Eisenhower)":
                st.subheader("Análisis de Enfoque Antiestrés")
                if df_pendientes.empty: st.success("¡Matriz limpia!")
                else:
                    df_altas = df_pendientes[df_pendientes['prioridad'] == 'Alta']
                    df_medias = df_pendientes[df_pendientes['prioridad'] == 'Media']
                    df_bajas = df_pendientes[df_pendientes['prioridad'] == 'Baja']
                    
                    if not df_altas.empty:
                        tarea_reina = df_altas.iloc[0]
                        df_altas_restantes = df_altas.iloc[1:]
                    else:
                        tarea_reina = None; df_altas_restantes = df_altas
                    
                    if tarea_reina is not None:
                        with st.container(border=True):
                            st.markdown(f"<h4 style='color: #F47B20; margin:0;'>🔥 Hito Crítico Actual: {tarea_reina['titulo']}</h4>", unsafe_allow_html=True)
                            st.write(f"{tarea_reina['descripcion']}")
                            if st.button("✔️ Consolidar Hito", key=f"reina_{tarea_reina['id']}"): marcar_tarea_completada(tarea_reina['id'])
                    
                    st.markdown("<br>➡️ **Distribución de la Matriz**", unsafe_allow_html=True)
                    col_izq, col_der = st.columns(2)
                    with col_izq:
                        with st.container(border=True):
                            st.markdown("<h4 style='color: #ff4b4b; margin:0;'>🔴 Urgente e Importante</h4>", unsafe_allow_html=True)
                            for _, t in df_altas_restantes.iterrows(): st.markdown(f"• {t['titulo']}")
                        with st.container(border=True):
                            st.markdown("<h4 style='color: #25b882; margin:0;'>🟢 Planificación Estratégica</h4>", unsafe_allow_html=True)
                            for _, t in df_medias.iterrows(): st.markdown(f"• {t['titulo']}")
                    with col_der:
                        with st.container(border=True):
                            st.markdown("<h4 style='color: #f47b20; margin:0;'>🟡 Delegación / Quick Wins</h4>", unsafe_allow_html=True)
                            for _, t in df_bajas.iterrows(): st.markdown(f"• {t['titulo']}")
                        with st.container(border=True):
                            st.markdown("<h4 style='color: #888888; margin:0;'>⚫ Brain Dump (Últimas añadidas)</h4>", unsafe_allow_html=True)
                            for _, t in df_filtrado.tail(2).iterrows(): st.markdown(f"• {t['titulo']}")
            
except Exception as e:
    st.error(f"Error en la aplicación: {e}")