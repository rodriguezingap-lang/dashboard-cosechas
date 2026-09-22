import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard Estadístico Agroindustrial",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS ELEGANTES ---
st.markdown("""
    <style>
        .main { background-color: #0e1117; }
        .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; }
        h1, h2, h3 { color: #f3f4f6; }
        .explanation-box {
            background-color: #1f2937;
            padding: 15px;
            border-left: 5px solid #10b981;
            border-radius: 5px;
            margin-bottom: 20px;
            color: #d1d5db;
        }
    </style>
""", unsafe_allow_html=True)

# --- CARGA DE DATOS AUTOMÁTICA DESDE GOOGLE DRIVE ---
@st.cache_data(ttl=300) # El dashboard refresca los datos automáticamente cada 5 minutos
def cargar_datos():
    file_id = "1pRT2SDTTx8lP60zs-uzYLoVD6Vj0DpRE"
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    df_master = pd.read_excel(url, sheet_name='Base_Maestra')
    df_kpis = pd.read_excel(url, sheet_name='Resumen_KPIs')
    return df_master, df_kpis

try:
    df, df_kpis = cargar_datos()
except Exception as e:
    st.error(f"⚠️ Error al conectar con Google Drive. Verifica que el archivo sea público y el enlace sea correcto: {e}")
    st.stop()

# --- CÁLCULO DE LA MÉTRICA CLAVE (KG / HA) ---
df['Rendimiento_Kg_Ha'] = df['Kilos_Recolectados'] / df['Hectareas'].replace(0, np.nan)

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.title("Filtros Globales")
st.sidebar.markdown("---")
regiones = ['Todas'] + list(df['Region'].dropna().unique())
region_seleccionada = st.sidebar.selectbox("Seleccionar Región:", regiones, key="region_filtro")

cultivos = ['Todos'] + list(df['Cultivo'].dropna().unique())
cultivo_seleccionado = st.sidebar.selectbox("Seleccionar Cultivo:", cultivos, key="cultivo_filtro")

df_filtrado = df.copy()
if region_seleccionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['Region'] == region_seleccionada]
if cultivo_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Cultivo'] == cultivo_seleccionado]

# --- ENCABEZADO ---
st.title("📈 Panel Estadístico y Eficiencia Agroindustrial")
st.markdown("Análisis de rendimiento por hectárea, control de supervisores y evaluación de productividad en tiempo real.")
st.markdown("---")

# --- TARJETAS DE KPI ---
col1, col2, col3, col4 = st.columns(4)
total_kilos = df_filtrado['Kilos_Recolectados'].sum()
total_hectareas = df_filtrado['Hectareas'].sum()
promedio_rendimiento = total_kilos / total_hectareas if total_hectareas > 0 else 0
total_cosechas = len(df_filtrado)

with col1: st.metric("📥 Kilos Totales", f"{total_kilos:,.0f} kg")
with col2: st.metric("🌱 Hectáreas Totales", f"{total_hectareas:,.2f} ha")
with col3: st.metric("📊 Rendimiento Promedio", f"{promedio_rendimiento:,.2f} kg/ha")
with col4: st.metric("📋 Registros Analizados", f"{total_cosechas:,}")

st.markdown("---")

# --- SECCIÓN 1: ESTADÍSTICA DESCRIPTIVA ---
st.subheader("📊 1. Estadísticas Descriptivas (Rendimiento en kg/ha)")

if not df_filtrado.empty:
    media = df_filtrado['Rendimiento_Kg_Ha'].mean()
    mediana = df_filtrado['Rendimiento_Kg_Ha'].median()
    desv_std = df_filtrado['Rendimiento_Kg_Ha'].std()
    minimo = df_filtrado['Rendimiento_Kg_Ha'].min()
    maximo = df_filtrado['Rendimiento_Kg_Ha'].max()

    df_stats = pd.DataFrame({
        'Métrica Estadística': ['Media (Promedio kg/ha)', 'Mediana', 'Desviación Estándar', 'Mínimo', 'Máximo'],
        'Valor (Kg/Ha)': [media, mediana, desv_std, minimo, maximo]
    })
    st.dataframe(df_stats.style.format({'Valor (Kg/Ha)': '{:,.2f}'}), use_container_width=True)

    st.markdown("""
        <div class="explanation-box">
        <strong>💡 Interpretación Gerencial del Rendimiento:</strong><br>
        • Mide cuántos kilos se producen exactamente por cada hectárea cultivada.<br>
        • Una <b>Desviación Estándar</b> baja indica que la productividad es uniforme y estable en todos los terrenos evaluados.
        </div>
    """, unsafe_allow_html=True)

    # --- SECCIÓN 2: RENDIMIENTO POR SUPERVISOR Y RANKING DE LOTES ---
    st.subheader("👨‍🌾 2. Eficiencia Operativa y Lotes Destacados")
    
    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.markdown("##### Rendimiento Promedio por Supervisor (kg/ha)")
        df_sup_rend = df_filtrado.groupby('Nombre_Completo')['Rendimiento_Kg_Ha'].mean().reset_index()
        fig_sup = px.bar(
            df_sup_rend, 
            x='Nombre_Completo', 
            y='Rendimiento_Kg_Ha',
            text_auto='.2f',
            color='Rendimiento_Kg_Ha',
            color_discrete_sequence=px.colors.sequential.Tealgrn
        )
        fig_sup.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_sup, use_container_width=True)
        
        st.markdown("""
            <div class="explanation-box">
            <b>Interpretación:</b> Compara el promedio de kilos por hectárea bajo la supervisión de cada responsable. Permite identificar qué equipo de campo logra la mayor efectividad productiva por unidad de área.
            </div>
        """, unsafe_allow_html=True)

    with col_s2:
        st.markdown("##### Top Lotes con Mayor Rendimiento (kg/ha)")
        df_top_lotes = df_filtrado.nlargest(10, 'Rendimiento_Kg_Ha')
        fig_lotes = px.bar(
            df_top_lotes, 
            x='ID_Lote', 
            y='Rendimiento_Kg_Ha',
            text_auto='.2f',
            color='Cultivo',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_lotes.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_lotes, use_container_width=True)
        
        st.markdown("""
            <div class="explanation-box">
            <b>Interpretación:</b> Muestra los 10 lotes más rentables y eficientes de la operación actual, sirviendo como modelo a replicar en las siguientes campañas agrícolas.
            </div>
        """, unsafe_allow_html=True)

    # --- SECCIÓN 3: DETECCIÓN DE OUTLIERS DE RENDIMIENTO ---
    st.subheader("📉 3. Detección de Anomalías de Rendimiento (Boxplot kg/ha)")
    fig_box = px.box(
        df_filtrado, 
        y='Rendimiento_Kg_Ha', 
        points="all", 
        color_discrete_sequence=['#3b82f6']
    )
    fig_box.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
    st.plotly_chart(fig_box, use_container_width=True)
    
    st.markdown("""
        <div class="explanation-box">
        <b>Interpretación del Boxplot:</b> Ayuda a visualizar de forma limpia los puntos atípicos de rendimiento. Los puntos que sobresalgan por debajo de la caja principal alertan sobre lotes con problemas severos de baja productividad por hectárea.
        </div>
    """, unsafe_allow_html=True)

else:
    st.warning("No hay datos suficientes con los filtros seleccionados para mostrar el análisis.")