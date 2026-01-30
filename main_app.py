import streamlit as st
import pandas as pd
import numpy as np
import io

# Page Configuration
st.set_page_config(
    page_title="Dashboard Energía Renovable",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

try:
    local_css("style.css")
except FileNotFoundError:
    st.warning("Archivo style.css no encontrado. Asegúrate de que esté en el mismo directorio.")

# Main Layout
st.title("⚡ Dashboard de Energía Renovable")
st.markdown("""
<div style='background-color: rgba(79, 172, 254, 0.1); padding: 1rem; border-radius: 10px; border-left: 5px solid #4facfe; margin-bottom: 2rem;'>
    <p style='margin: 0; font-size: 1.1rem;'>
        Bienvenido al sistema de análisis. Sube tu archivo CSV para comenzar el Análisis Exploratorio de Datos (EDA).
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📂 Configuración de Datos")
    uploaded_file = st.file_uploader("Cargar archivo CSV", type=['csv'])
    
    st.markdown("---")
    st.markdown("### Información del Sistema")
    st.info("Soporta archivos .CSV con codificación UTF-8.")

# Main Logic
if uploaded_file is not None:
    try:
        # Read the file
        df = pd.read_csv(uploaded_file)
        
        # Success message with animation effect
        st.success(f"✅ Archivo cargado exitosamente: **{uploaded_file.name}**")
        
        # Dashboard Grid
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Filas", df.shape[0])
        with col2:
            st.metric("Total Columnas", df.shape[1])
        with col3:
            st.metric("Celdas Vacías", df.isnull().sum().sum())
            
        st.markdown("### 🔍 Vista Previa de Datos")
        st.dataframe(df.head(), use_container_width=True)
        
        # Basic Info Section
        with st.expander("ℹ️ Ver Información del DataFrame"):
            buffer = io.StringIO()
            df.info(buf=buffer)
            s = buffer.getvalue()
            st.text(s)
            
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
else:
    # Empty State
    st.markdown("""
    <div style='text-align: center; padding: 50px; opacity: 0.7;'>
        <h2>waiting for data...</h2>
        <p>Por favor carga un archivo CSV en el panel lateral para visualizar el dashboard.</p>
    </div>
    """, unsafe_allow_html=True)
