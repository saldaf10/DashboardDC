import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io

# Page Configuration
st.set_page_config(
    page_title="AI Data Dashboard",
    page_icon="📊",
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

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2920/2920326.png", width=80)
    st.title("📊 DataInsight")
    st.markdown("---")
    st.header("📂 1. Carga de Datos")
    uploaded_file = st.file_uploader("Sube tu archivo CSV", type=['csv'])
    
    st.markdown("### ⚙️ 2. Configuración CSV")
    separator = st.selectbox("Separador", [",", ";", "|", "\\t"], index=0)
    encoding_opt = st.selectbox("Codificación", ["utf-8", "latin-1", "ISO-8859-1", "cp1252"], index=0)

    st.markdown("---")
    st.caption("Sistema de Análisis Universal con Streamlit")

# Main Logic
if uploaded_file is not None:
    try:
        # Read the file with user settings
        df_original = pd.read_csv(uploaded_file, sep=separator, encoding=encoding_opt)
        total_rows = len(df_original)
        
        # --- SAMPLE SIZE SLIDER ---
        st.sidebar.markdown("### ✂️ 3. Muestreo")
        sample_size = st.sidebar.slider(
            "Cantidad de filas a analizar:",
            min_value=min(10, total_rows),
            max_value=total_rows,
            value=total_rows,
            step=1,
            help="Desliza para analizar solo un subconjunto de datos (útil para archivos grandes)."
        )
        
        # Slice the dataframe
        df = df_original.head(sample_size)
        
        st.sidebar.markdown("### 🛠️ 4. Herramientas")
        show_gen = st.sidebar.checkbox("📋 Vista General", value=True)
        show_cat = st.sidebar.checkbox("📊 Análisis Cualitativo", value=True)
        show_num = st.sidebar.checkbox("📈 Análisis Cuantitativo", value=True)
        show_rel = st.sidebar.checkbox("🔗 Relaciones", value=True)
        show_time = st.sidebar.checkbox("📅 Series de Tiempo", value=True)
        show_ai = st.sidebar.checkbox("🤖 Asistente IA", value=True)
        
        # --- HEADER ---
        st.title("📊 Dashboard de Análisis Exploratorio")
        
        # Dynamic info text
        info_text = f"Analizando: <b>{uploaded_file.name}</b> | Registros: <b>{len(df)}</b>/{total_rows}"
        if len(df) < total_rows:
            info_text += f" (Muestra del {int((len(df)/total_rows)*100)}%)"
            
        st.markdown(f"""
        <div style='background-color: rgba(79, 172, 254, 0.1); padding: 1rem; border-radius: 10px; border-left: 5px solid #4facfe; margin-bottom: 2rem;'>
            <p style='margin: 0; font-size: 1.1rem;'>
                {info_text} | Columnas: <b>{len(df.columns)}</b>
            </p>
        </div>
        """, unsafe_allow_html=True)

        # --- TABS LOGIC ---
        tabs_config = []
        if show_gen: tabs_config.append({"title": "📋 General", "key": "gen"})
        if show_cat: tabs_config.append({"title": "📊 Análisis Cualitativo", "key": "cat"})
        if show_num: tabs_config.append({"title": "📈 Análisis Cuantitativo", "key": "num"})
        if show_rel: tabs_config.append({"title": "🔗 Relaciones", "key": "rel"})
        if show_time: tabs_config.append({"title": "📅 Series de Tiempo", "key": "time"})
        if show_ai: tabs_config.append({"title": "🤖 Asistente IA", "key": "ai"})
        
        if not tabs_config:
            st.warning("⚠️ Por favor selecciona al menos una herramienta en el panel lateral (Sección 4).")
        else:
            # Create Tabs
            tabs_objects = st.tabs([t["title"] for t in tabs_config])
            
            # Map Key -> Tab Object
            tabs_dict = {config["key"]: tab for config, tab in zip(tabs_config, tabs_objects)}
            
            # === TAB 1: GENERAL ===
            if "gen" in tabs_dict:
                with tabs_dict["gen"]:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1: st.metric("Filas", df.shape[0])
                    with col2: st.metric("Columnas", df.shape[1])
                    with col3: st.metric("Duplicados", df.duplicated().sum())
                    with col4: st.metric("Celdas Vacías", df.isnull().sum().sum())

                    st.markdown("### 🔍 Vista Previa")
                    
                    # Slider for preview rows
                    rows_to_show = st.slider(
                        "Filas a visualizar en la tabla:", 
                        min_value=5, 
                        max_value=len(df), 
                        value=10, 
                        step=5,
                        key="slider_preview_rows"
                    )
                    
                    st.dataframe(df.head(rows_to_show), use_container_width=True)
                    
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
            if "cat" in tabs_dict:
                with tabs_dict["cat"]:
                    st.markdown("### 📊 Análisis de Variables Categóricas")
                    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
                    
                    if cat_cols:
                        col_sel, col_display = st.columns([1, 3])
                        with col_sel:
                            selected_cat_col = st.selectbox("Selecciona una columna (Categoría):", cat_cols)
                            
                            st.markdown("#### Estadísticas")
                            st.write(df[selected_cat_col].describe())
                        
                        with col_display:
                            # Graficos lado a lado
                            c1, c2 = st.columns(2)
                            with c1:
                                # Bar Chart
                                counts = df[selected_cat_col].value_counts().reset_index()
                                counts.columns = ['Valor', 'Frecuencia']
                                # Limit to top 20 for readability
                                counts = counts.head(20)
                                
                                fig_bar = px.bar(
                                    counts, x='Valor', y='Frecuencia', 
                                    color='Frecuencia',
                                    title=f"Top Distribución: {selected_cat_col} (Max 20)",
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
            if "num" in tabs_dict:
                with tabs_dict["num"]:
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
            if "rel" in tabs_dict:
                with tabs_dict["rel"]:
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
            
            # === TAB 5: SERIES DE TIEMPO ===
            if "time" in tabs_dict:
                with tabs_dict["time"]:
                    st.markdown("### 📅 Análisis Temporal")
                    
                    # Intentar detectar columnas de fecha
                    possible_date_cols = [col for col in df.columns if 'date' in col.lower() or 'fecha' in col.lower() or 'time' in col.lower() or 'año' in col.lower()]
                    all_cols = df.columns.tolist()
                    
                    c_sel_date, c_display_time = st.columns([1, 3])
                    
                    with c_sel_date:
                        date_col = st.selectbox(
                            "Selecciona Columna de Fecha/Tiempo:", 
                            options=all_cols, 
                            index=all_cols.index(possible_date_cols[0]) if possible_date_cols else 0
                        )
                        st.info("Intenta seleccionar una columna que contenga fechas (YYYY-MM-DD) o años.")

                    with c_display_time:
                        try:
                            # Copy df to avoid affecting other tabs
                            df_time = df.copy()
                            df_time[date_col] = pd.to_datetime(df_time[date_col], errors='coerce')
                            
                            # Drop invalid dates
                            df_time = df_time.dropna(subset=[date_col])
                            
                            if not df_time.empty:
                                df_time = df_time.sort_values(by=date_col)
                                
                                st.write(f"Rango de Fechas detectado: **{df_time[date_col].min().date()}** a **{df_time[date_col].max().date()}**")
                                
                                # Time Series Plot
                                num_cols_time = df_time.select_dtypes(include=['number']).columns.tolist()
                                if num_cols_time:
                                    y_col_time = st.selectbox("Variable a graficar en el tiempo:", num_cols_time)
                                    
                                    # Aggregation
                                    agg_type = st.radio("Agregación:", ["Sin Agrupar", "Promedio Mensual", "Suma Mensual"], horizontal=True)
                                    
                                    if agg_type == "Promedio Mensual":
                                        df_plot = df_time.set_index(date_col).resample('M')[y_col_time].mean().reset_index()
                                    elif agg_type == "Suma Mensual":
                                        df_plot = df_time.set_index(date_col).resample('M')[y_col_time].sum().reset_index()
                                    else:
                                        df_plot = df_time
                                        
                                    fig_line = px.line(
                                        df_plot, x=date_col, y=y_col_time,
                                        title=f"Evolución de {y_col_time}",
                                        markers=True
                                    )
                                    fig_line.update_traces(line_color='#00f2fe', line_width=2)
                                    fig_line.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                                    st.plotly_chart(fig_line, use_container_width=True)
                                else:
                                    st.warning("No hay columnas numéricas para graficar en el tiempo.")
                            else:
                                st.warning("No se pudieron convertir los datos de esa columna ver fechas válidas.")
                        except Exception as e:
                            st.error(f"Error al procesar fechas: {e}")

            # === TAB 6: ASISTENTE IA ===
            if "ai" in tabs_dict:
                with tabs_dict["ai"]:
                    st.markdown("### 🤖 Asistente de IA (Powered by Groq)")
                    st.markdown("""
                    <div style='background-color: rgba(0, 255, 127, 0.1); padding: 10px; border-radius: 5px; border-left: 3px solid #00ff7f;'>
                        <small>Este asistente utiliza el modelo <b>llama-3.3-70b-versatile</b> para analizar tus datos en tiempo real.</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    api_key = st.text_input("Ingresa tu API Key de Groq:", type="password", help="Obtén tu key en https://console.groq.com/keys")
                    
                    if api_key:
                        st.info("API Key detectada. Listo para analizar.")
                        if st.button("🧠 Generar Análisis Automático"):
                            with st.spinner("La IA está analizando tu dataset..."):
                                try:
                                    # Prepare Data Context (limited to save tokens)
                                    from openai import OpenAI
                                    
                                    client = OpenAI(
                                        base_url="https://api.groq.com/openai/v1",
                                        api_key=api_key
                                    )
                                    
                                    data_summary = f"""
                                    Dataset Info:
                                    - Rows: {df.shape[0]}, Columns: {df.shape[1]}
                                    - Columns: {', '.join(df.columns)}
                                    - Missing Values: {df.isnull().sum().to_dict()}
                                    - Sample Data (first 5 rows):
                                    {df.head().to_markdown()}
                                    - Statistics:
                                    {df.describe().to_markdown()}
                                    """
                                    
                                    prompt = f"""
                                    Act as an expert Data Scientist. Analyze the following dataset summary and provide:
                                    1. 3 Key Observations/Trends.
                                    2. Potential anomalies or data quality issues.
                                    3. Suggestions for 2 specific advanced visualizations.
                                    
                                    Dataset:
                                    {data_summary}
                                    
                                    Format the output in clear Markdown with emojis. Keep it concise but professional.
                                    """
                                    
                                    completion = client.chat.completions.create(
                                        model="llama-3.3-70b-versatile",
                                        messages=[
                                            {"role": "system", "content": "You are a helpful Data Analysis Assistant capable of finding hidden insights in CSV data."},
                                            {"role": "user", "content": prompt}
                                        ],
                                        temperature=0.5,
                                        max_tokens=1024,
                                        top_p=1,
                                        stream=False,
                                        stop=None,
                                    )
                                    
                                    response = completion.choices[0].message.content
                                    st.markdown("### 📝 Resultados del Análisis")
                                    st.markdown(response)
                                    
                                except Exception as e:
                                    st.error(f"Error al conectar con la IA: {e}")
                    else:
                        st.warning("⚠️ Necesitas una API Key de Groq para usar esta funcionalidad.")

    except Exception as e:
        st.error(f"❌ Error al leer el archivo: {e}")
        st.info("Prueba combiando el Separador o la Codificación en el panel lateral.")
else:
    # Empty State with Animation
    st.markdown("""
    <div style='text-align: center; margin-top: 50px;'>
        <h1>👋 ¡Bienvenido al Analizador Universal!</h1>
        <p style='font-size: 1.2rem; color: #a0a0a0;'>
            Sube cualquier archivo CSV (Energía, Agrícola, Monitoreo, etc.) y detectaremos la estructura automáticamente.
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
                📂 Subir CSV
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
