import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
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

# Helper function to find columns
def get_column_by_keyword(df, keywords):
    for col in df.columns:
        if any(keyword.lower() in col.lower() for keyword in keywords):
            return col
    return None

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3109/3109838.png", width=80)
    st.title("⚡ EnergíaDashboard")
    st.markdown("---")
    st.header("📂 Configuración")
    uploaded_file = st.file_uploader("Cargar archivo CSV", type=['csv'])
    
    st.markdown("### Información del Sistema")
    st.info("Sube tu archivo para ver el análisis automático.")
    st.markdown("---")
    st.caption("Desarrollado con Streamlit & Plotly")

# Main Logic
if uploaded_file is not None:
    try:
        # Read the file
        df = pd.read_csv(uploaded_file)
        
        # --- HEADER ---
        st.title("⚡ Dashboard de Análisis Energético")
        st.markdown(f"""
        <div style='background-color: rgba(79, 172, 254, 0.1); padding: 1rem; border-radius: 10px; border-left: 5px solid #4facfe; margin-bottom: 2rem;'>
            <p style='margin: 0; font-size: 1.1rem;'>
                Analizando archivo: <b>{uploaded_file.name}</b> | Registros: <b>{len(df)}</b>
            </p>
        </div>
        """, unsafe_allow_html=True)

        # --- TABS DE NAVEGACIÓN ---
        tab1, tab2, tab3, tab4 = st.tabs(["📋 General", "📊 Análisis Cualitativo", "📈 Análisis Cuantitativo", "🔗 Relaciones"])
        
        # === TAB 1: GENERAL ===
        with tab1:
            col1, col2, col3, col4 = st.columns(4)
            with col1: st.metric("Filas", df.shape[0])
            with col2: st.metric("Columnas", df.shape[1])
            with col3: st.metric("Duplicados", df.duplicated().sum())
            with col4: st.metric("Celdas Vacías", df.isnull().sum().sum())

            st.markdown("### 🔍 Vista Previa")
            st.dataframe(df.head(10), use_container_width=True)
            
            # Missing Values Chart
            st.subheader("⚠️ Mapa de Valores Nulos")
            nulls = df.isnull().sum()
            if nulls.sum() > 0:
                fig_null = px.bar(
                    x=nulls.index, 
                    y=nulls.values,
                    labels={'x': 'Columna', 'y': 'Cantidad de Nulos'},
                    title="Valores Nulos por Columna",
                    color_discrete_sequence=['#ff6b6b']
                )
                fig_null.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_null, use_container_width=True)
            else:
                st.success("¡Excelente! No se detectaron valores nulos en el dataset.")

        # === TAB 2: CUALITATIVO (CATEGÓRICO) ===
        with tab2:
            st.markdown("### 📊 Análisis de Variables Categóricas")
            cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
            
            if cat_cols:
                col_sel, col_display = st.columns([1, 3])
                with col_sel:
                    selected_cat_col = st.selectbox("Selecciona una columna:", cat_cols)
                    
                    st.markdown("#### Estadísticas")
                    st.write(df[selected_cat_col].describe())
                
                with col_display:
                    # Graficos lado a lado
                    c1, c2 = st.columns(2)
                    with c1:
                        # Bar Chart
                        counts = df[selected_cat_col].value_counts().reset_index()
                        counts.columns = ['Valor', 'Frecuencia']
                        fig_bar = px.bar(
                            counts, x='Valor', y='Frecuencia', 
                            color='Frecuencia',
                            title=f"Distribución: {selected_cat_col}",
                            color_continuous_scale=px.colors.sequential.Bluered
                        )
                        fig_bar.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig_bar, use_container_width=True)
                    
                    with c2:
                        # Pie Chart
                        fig_pie = px.pie(
                            counts, names='Valor', values='Frecuencia',
                            title=f"Proporción: {selected_cat_col}",
                            hole=0.4,
                            color_discrete_sequence=px.colors.sequential.Bluered_r
                        )
                        fig_pie.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("No se encontraron columnas categóricas (texto/categorías) en este dataset.")

        # === TAB 3: CUANTITATIVO (NUMÉRICO) ===
        with tab3:
            st.markdown("### 📈 Análisis de Variables Numéricas")
            num_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if num_cols:
                col_sel_num, col_display_num = st.columns([1, 3])
                with col_sel_num:
                    selected_num_col = st.selectbox("Selecciona variable numérica:", num_cols)
                    
                    st.markdown("#### Estadísticas Descriptivas")
                    desc = df[selected_num_col].describe()
                    st.dataframe(desc, use_container_width=True)
                
                with col_display_num:
                    c1, c2 = st.columns(2)
                    with c1:
                        # Histogram
                        fig_hist = px.histogram(
                            df, x=selected_num_col, 
                            nbins=30, 
                            title=f"Histograma: {selected_num_col}",
                            color_discrete_sequence=['#4facfe']
                        )
                        fig_hist.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig_hist, use_container_width=True)
                    
                    with c2:
                        # Box Plot
                        fig_box = px.box(
                            df, y=selected_num_col,
                            title=f"Box Plot (Valores Atípicos): {selected_num_col}",
                            color_discrete_sequence=['#00f2fe']
                        )
                        fig_box.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                        st.plotly_chart(fig_box, use_container_width=True)
            else:
                st.info("No se encontraron columnas numéricas en este dataset.")

        # === TAB 4: RELACIONES ===
        with tab4:
            st.markdown("### 🔗 Relaciones y Correlaciones")
            num_cols = df.select_dtypes(include=['number']).columns.tolist()
            
            if len(num_cols) > 1:
                # Heatmap
                st.subheader("Mapa de Calor (Correlación)")
                corr = df[num_cols].corr()
                fig_corr = px.imshow(
                    corr, text_auto=True, aspect="auto",
                    color_continuous_scale='RdBu_r',
                    title="Matriz de Correlación"
                )
                fig_corr.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_corr, use_container_width=True)
                
                # Scatter Plot Interactivo
                st.subheader("Gráfico de Dispersión (Scatter Plot)")
                c1, c2, c3 = st.columns(3)
                with c1: x_axis = st.selectbox("Eje X", num_cols, index=0)
                with c2: y_axis = st.selectbox("Eje Y", num_cols, index=1 if len(num_cols)>1 else 0)
                with c3: 
                    cat_cols_scatter = df.select_dtypes(include=['object', 'category']).columns.tolist()
                    color_col = st.selectbox("Color (Agrupador)", [None] + cat_cols_scatter)

                fig_scatter = px.scatter(
                    df, x=x_axis, y=y_axis, color=color_col,
                    title=f"Correlación: {x_axis} vs {y_axis}",
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                fig_scatter.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_scatter, use_container_width=True)
            else:
                st.info("Se necesitan al menos 2 columnas numéricas para analizar correlaciones.")
            
    except Exception as e:
        st.error(f"❌ Error al procesar el archivo: {e}")
        st.write(e) # Show detailed error for debugging
else:
    # Empty State with Animation
    st.markdown("""
    <div style='text-align: center; margin-top: 50px;'>
        <h1>👋 ¡Hola!</h1>
        <p style='font-size: 1.2rem; color: #a0a0a0;'>
            Para comenzar, sube tu archivo CSV en el panel de la izquierda.
        </p>
        <div style='display: flex; justify-content: center; margin-top: 20px;'>
            <div style='
                width: 200px; 
                height: 150px; 
                border: 2px dashed #4facfe; 
                border-radius: 10px; 
                display: flex; 
                align-items: center; 
                justify-content: center; 
                color: #4facfe;'>
                📂 Tu archivo aquí
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
