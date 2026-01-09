import streamlit as st
import pandas as pd
import os

# 1. Configuración de página
st.set_page_config(page_title="Gestión Curtiembre Cloud", layout="wide")

# --- ESTILO CSS PARA LOS DOS LOGOS Y DISEÑO ---
st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; padding-bottom: 0rem; }
    
    /* Estilo para los logos en la barra lateral */
    .sidebar-logo {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 90%;
        margin-bottom: 20px;
    }
    
    .titulo-compacto {
        text-align: left;
        font-size: 1.4rem !important;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
        border-left: 5px solid #1E3A8A;
        padding-left: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CARGAR DATOS (Temporalmente local hasta conectar Google Sheets) ---
@st.cache_data
def cargar_base():
    # Nota: Mañana cambiaremos esto por la conexión a la nube
    df = pd.read_excel("Listado de pendientes.xlsx")
    df.columns = df.columns.str.strip()
    return df

if 'df_maestro' not in st.session_state:
    st.session_state.df_maestro = cargar_base()

df = st.session_state.df_maestro

# --- 3. DETECTOR DE COLUMNAS ---
cols = df.columns.tolist()
def encontrar_col(nombres):
    for n in nombres:
        for c in cols:
            if n.upper() in c.upper(): return c
    return None

COL_TEMA = encontrar_col(["TEMA", "TAREA"])
COL_DESARROLLO = encontrar_col(["DESARROLLO", "DETALLE"])
COL_IMPORTANCIA = encontrar_col(["IMPORTANCIA", "PRIORIDAD"])
COL_RESPONSABLE = encontrar_col(["RESPONSABLE"])
COL_OK = encontrar_col(["OK", "ESTADO"])

# --- 4. BARRA LATERAL CON DOS LOGOS ---
with st.sidebar:
    # Logo Superior
    if os.path.exists("logo.png"):
        st.image("logo.png")
    
    st.markdown("---")
    st.markdown("### ⚙️ Configuración")
    responsable = st.selectbox("👤 Responsable", options=sorted(df[COL_RESPONSABLE].unique()))
    prioridades = st.multiselect("📊 Ver Prioridades", options=sorted(df[COL_IMPORTANCIA].unique()), default=sorted(df[COL_IMPORTANCIA].unique()))
    
    st.markdown("---")
    
    # NUEVO: Segundo Logo debajo de las opciones
    # Debes guardar una imagen llamada 'logo1.png' en tu carpeta
    if os.path.exists("logo1.png"):
        st.write("Soporte Institucional:")
        st.image("logo1.png")
    else:
        st.info("Coloca un archivo 'logo1.png' para verlo aquí.")

# --- 5. PROCESAR DATOS ---
df_temp = df.copy()
df_temp[COL_OK] = df_temp[COL_OK].apply(lambda x: True if str(x).upper() == "OK" else False)
mask = (df_temp[COL_RESPONSABLE] == responsable) & (df_temp[COL_IMPORTANCIA].isin(prioridades))
df_vista = df_temp[mask][[COL_TEMA, COL_DESARROLLO, COL_IMPORTANCIA, COL_OK]].copy()

def filtrar_contar(pri, ok_val):
    return len(df_vista[(df_vista[COL_IMPORTANCIA].str.contains(pri, case=False, na=False)) & (df_vista[COL_OK] == ok_val)])

# --- 6. PANEL SUPERIOR ---
st.markdown(f'<div class="titulo-compacto">Panel Cloud: {responsable}</div>', unsafe_allow_html=True)

c1, c2, c3, c4, c5, c6, _ = st.columns([1,1,1,1,1,1,3])
c1.metric("Crit. ⏳", filtrar_contar("Crit", False))
c2.metric("Imp. ⏳", filtrar_contar("Import", False))
c3.metric("Estr. ⏳", filtrar_contar("Estrat", False))
c4.metric("Crit. ✅", filtrar_contar("Crit", True))
c5.metric("Imp. ✅", filtrar_contar("Import", True))
c6.metric("Estr. ✅", filtrar_contar("Estrat", True))

# Botón Guardar a la izquierda
col_btn, _ = st.columns([2, 8])
with col_btn:
    btn_guardar = st.button("💾 SINCRONIZAR CAMBIOS", use_container_width=True)

st.markdown("---")

# --- 7. TABLA DE DATOS ---
df_editado = st.data_editor(
    df_vista,
    column_config={
        COL_OK: st.column_config.CheckboxColumn("OK", width="small"),
        COL_IMPORTANCIA: st.column_config.TextColumn("Prioridad", width="small"),
        COL_TEMA: st.column_config.TextColumn("Tema", width="medium"),
        COL_DESARROLLO: st.column_config.TextColumn("Desarrollo", width="large")
    },
    disabled=[COL_TEMA, COL_DESARROLLO, COL_IMPORTANCIA],
    hide_index=True,
    use_container_width=True,
    height=450
)

# Lógica de guardado
if btn_guardar:
    df.update(df_editado)
    df_f = df.copy()
    df_f[COL_OK] = df_f[COL_OK].apply(lambda x: "OK" if x == True else "_")
    try:
        df_f.to_excel("Listado de pendientes.xlsx", index=False)
        st.toast("¡Sincronizado con éxito!", icon="☁️")
        st.session_state.df_maestro = cargar_base()
        st.rerun()
    except:
        st.error("Error: Cierra el Excel.")