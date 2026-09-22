import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard Agroindustrial | Control de Cosechas",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS ELEGANTES (MODERN UI) ---
st.markdown("""
    <style>
        .main {
            background-color: #0e1117;
        }
        .stMetric {
            background-color: #1f2937;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        h1, h2, h3 {
            color: #f3f4f6;
        }
    </style>
""", unsafe_allow_html=True)

# --- CARGA DE DATOS ---
@st.cache_data
def cargar_datos():
    archivo = 'Base_Maestra_Limpia.xlsx'
    df_master = pd.read_excel(archivo, sheet_name='Base_Maestra')
    df_kpis = pd.read_excel(archivo, sheet_name='Resumen_KPIs')
    return df_master, df_kpis

try:
    df, df_kpis = cargar_datos()
except FileNotFoundError:
    st.error("⚠️ No se encontró el archivo 'Base_Maestra_Limpia.xlsx'. Ejecuta primero tu robot de Python para generarlo.")
    st.stop()

# --- BARRA LATERAL (FILTROS) ---
st.sidebar.image("https://img.icons8.com/color/96/wheat.png", width=70)
st.sidebar.title("Filtros Globales")
st.sidebar.markdown("---")

# Filtro por Región
regiones = ['Todas'] + list(df['Region'].dropna().unique())
region_seleccionada = st.sidebar.selectbox("Seleccionar Región:", regiones)

# Filtro por Cultivo
cultivos = ['Todos'] + list(df['Cultivo'].dropna().unique())
cultivo_seleccionado = st.sidebar.selectbox("Seleccionar Cultivo:", cultivos)

# Aplicar filtros al DataFrame
df_filtrado = df.copy()
if region_seleccionada != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['Region'] == region_seleccionada]
if cultivo_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Cultivo'] == cultivo_seleccionado]

# --- ENCABEZADO PRINCIPAL ---
st.title("🌾 Panel de Control Agroindustrial")
st.markdown("Monitoreo en tiempo real de cosechas, rendimiento por hectárea y control de supervisores.")
st.markdown("---")

# --- TARJETAS DE KPI (MÉTRICAS PRINCIPALES) ---
col1, col2, col3, col4 = st.columns(4)

total_kilos = df_filtrado['Kilos_Recolectados'].sum()
total_hectareas = df_filtrado['Hectareas'].sum()
promedio_rendimiento = total_kilos / total_hectareas if total_hectareas > 0 else 0
total_cosechas = len(df_filtrado)

with col1:
    st.metric(label="📥 Kilos Totales Cosechados", value=f"{total_kilos:,.0f} kg")
with col2:
    st.metric(label="🌱 Hectáreas Totales", value=f"{total_hectareas:,.2f} ha")
with col3:
    st.metric(label="📊 Rendimiento Promedio", value=f"{promedio_rendimiento:,.2f} kg/ha")
with col4:
    st.metric(label="📋 Total de Registros", value=f"{total_cosechas:,}")

st.markdown("---")

# --- SECCIÓN DE GRÁFICOS AVANZADOS (PLOTLY) ---
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.subheader("🌱 Producción por Cultivo (Kilos)")
    if not df_filtrado.empty:
        df_cultivos = df_filtrado.groupby('Cultivo')['Kilos_Recolectados'].sum().reset_index()
        fig_cultivos = px.bar(
            df_cultivos, 
            x='Cultivo', 
            y='Kilos_Recolectados', 
            text_auto='.2s',
            color='Cultivo',
            color_discrete_sequence=px.colors.sequential.Tealgrn
        )
        fig_cultivos.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_cultivos, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar con los filtros seleccionados.")

with col_graf2:
    st.subheader("🗺️ Distribución de Hectáreas por Región")
    if not df_filtrado.empty:
        df_regiones = df_filtrado.groupby('Region')['Hectareas'].sum().reset_index()
        fig_regiones = px.pie(
            df_regiones, 
            names='Region', 
            values='Hectareas', 
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Mint
        )
        fig_regiones.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_regiones, use_container_width=True)
    else:
        st.warning("No hay datos para mostrar con los filtros seleccionados.")

# --- TABLA DE DATOS DETALLADA ---
st.markdown("---")
st.subheader("📋 Detalle de la Base Maestra Limpia")
with st.expander("Ver tabla completa de registros filtrados"):
    st.dataframe(df_filtrado, use_container_width=True)