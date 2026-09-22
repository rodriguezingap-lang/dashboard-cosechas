import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import datetime

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard Gerencial Agroindustrial",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS PROFESIONALES Y ADAPTATIVOS ---
st.markdown("""
    <style>
        /* Las tarjetas de métricas se adaptan automáticamente al modo Light y Dark */
        .stMetric {
            padding: 15px;
            border-radius: 10px;
            border: 1px solid rgba(128, 128, 128, 0.2);
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Contenedor fijo superior para los títulos principales (h1) */
        h1 {
            position: sticky !important;
            top: 0px !important;
            z-index: 99999 !important;
            background-color: var(--background-color) !important;
            padding-top: 15px !important;
            padding-bottom: 10px !important;
            margin-top: -10px !important;
            border-bottom: 1px solid rgba(128, 128, 128, 0.1);
        }

        .explanation-box {
            padding: 15px;
            border-left: 5px solid #10b981;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        
        .alert-box {
            padding: 15px;
            border-left: 5px solid #ef4444;
            border-radius: 5px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)



# --- CARGA DE DATOS AUTOMÁTICA DESDE GOOGLE DRIVE ---
@st.cache_data(ttl=300)
def cargar_datos():
    file_id = "1pRT2SDTTx8lP60zs-uzYLoVD6Vj0DpRE"
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    df_master = pd.read_excel(url, sheet_name='Base_Maestra')
    df_kpis = pd.read_excel(url, sheet_name='Resumen_KPIs')
    return df_master, df_kpis

try:
    df, df_kpis = cargar_datos()
except Exception as e:
    st.error(f"⚠️ Error al conectar con Google Drive: {e}")
    st.stop()

# --- PREPROCESAMIENTO Y LIMPIEZA DE CAMPOS ---
df['Kilos_Recolectados'] = pd.to_numeric(df['Kilos_Recolectados'], errors='coerce').fillna(0)
df['Hectareas'] = pd.to_numeric(df['Hectareas'], errors='coerce').fillna(0)
df['Rendimiento_Kg_Ha'] = df['Kilos_Recolectados'] / df['Hectareas'].replace(0, np.nan)

# Asegurar formato de fecha
if 'Fecha' in df.columns:
    df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')

# Definir fecha de corte YTD (22 de Septiembre de 2026)
FECHA_CORTE = pd.to_datetime('2026-09-22')


# ==========================================
# BARRA LATERAL (FILTROS GLOBALES Y NAVEGACIÓN)
# ==========================================
st.sidebar.title("🎛️ Panel de Control")
st.sidebar.markdown("---")

# 1. NAVEGACIÓN PRINCIPAL
pagina = st.sidebar.radio(
    "Seleccionar Página:",
    ["🟦 1. Gerencial (YTD)", "🟩 2. Operaciones", "🟨 3. Productividad", "🟥 4. Calidad de Datos", "📊 5. Estadística Avanzada"]
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Filtros Globales (Aplica a todo)")

# 2. FILTRO DE PERIODO TEMPORAL
modo_tiempo = st.sidebar.selectbox(
    "Periodo de Análisis:", 
    ["YTD Real (Histórico hasta Hoy)", "Plan / Datos Futuros", "Histórico Completo (Todo)"]
)

# 3. FILTRO DE REGIÓN
regiones = ['Todas'] + sorted(list(df['Region'].dropna().unique()))
region_sel = st.sidebar.selectbox("Región:", regiones)

# 4. FILTRO DE CULTIVO
cultivos = ['Todos'] + sorted(list(df['Cultivo'].dropna().unique()))
cultivo_sel = st.sidebar.selectbox("Cultivo:", cultivos)

# 5. FILTRO DE SUPERVISOR
supervisores = ['Todos'] + sorted(list(df['Nombre_Completo'].dropna().unique()))
supervisor_sel = st.sidebar.selectbox("Supervisor:", supervisores)


# --- APLICACIÓN DE FILTROS AL DATAFRAME GLOBAL ---
df_filtrado = df.copy()

# Aplicar periodo temporal
if modo_tiempo == "YTD Real (Histórico hasta Hoy)" and 'Fecha' in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado['Fecha'] <= FECHA_CORTE]
elif modo_tiempo == "Plan / Datos Futuros" and 'Fecha' in df_filtrado.columns:
    df_filtrado = df_filtrado[df_filtrado['Fecha'] > FECHA_CORTE]

# Aplicar región
if region_sel != 'Todas':
    df_filtrado = df_filtrado[df_filtrado['Region'] == region_sel]

# Aplicar cultivo
if cultivo_sel != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Cultivo'] == cultivo_sel]

# Aplicar supervisor
if supervisor_sel != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['Nombre_Completo'] == supervisor_sel]


# ==========================================
# PÁGINA 1 — GERENCIAL
# ==========================================
if pagina == "🟦 1. Gerencial (YTD)":
    st.title("🟦 Panel Ejecutivo Gerencial")
    st.markdown("Vista macro de la producción, superficie gestionada y eficiencia global bajo los filtros seleccionados.")
    st.markdown("---")

    tot_kilos = df_filtrado['Kilos_Recolectados'].sum()
    tot_cosechas = len(df_filtrado)
    tot_has = df_filtrado['Hectareas'].sum()
    prod_global = tot_kilos / tot_has if tot_has > 0 else 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("📥 Producción Acumulada", f"{tot_kilos:,.0f} kg")
    with c2: st.metric("📋 Total Cosechas", f"{tot_cosechas:,}")
    with c3: st.metric("📊 Productividad Global", f"{prod_global:,.2f} kg/ha")
    with c4: st.metric("🌱 Hectáreas Registradas", f"{tot_has:,.1f} ha")

    st.markdown("---")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.subheader("Evolución de Producción por Región")
        if 'Region' in df_filtrado.columns and not df_filtrado.empty:
            df_reg = df_filtrado.groupby('Region')['Kilos_Recolectados'].sum().reset_index()
            fig_reg = px.bar(df_reg, x='Region', y='Kilos_Recolectados', color='Region', text_auto='.2s', color_discrete_sequence=px.colors.qualitative.Prism)
            fig_reg.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig_reg, use_container_width=True)
            
    with col_g2:
        st.subheader("Participación por Cultivo")
        if 'Cultivo' in df_filtrado.columns and not df_filtrado.empty:
            df_cult = df_filtrado.groupby('Cultivo')['Kilos_Recolectados'].sum().reset_index()
            fig_cult = px.pie(df_cult, names='Cultivo', values='Kilos_Recolectados', hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_cult.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white')
            st.plotly_chart(fig_cult, use_container_width=True)

# ==========================================
# PÁGINA 2 — OPERACIONES
# ==========================================
elif pagina == "🟩 2. Operaciones":
    st.title("🟩 Panel Operativo y Turnos")
    st.markdown("Desglose operacional por supervisores, turnos de trabajo y lotes activos.")
    st.markdown("---")

    col_o1, col_o2, col_o3 = st.columns(3)
    with col_o1: st.metric("🏗️ Lotes Activos", f"{df_filtrado['ID_Lote'].nunique():,}")
    with col_o2: st.metric("👨‍🌾 Supervisores Activos", f"{df_filtrado['Nombre_Completo'].nunique():,}")
    with col_o3: st.metric("⚖️ Promedio por Cosecha", f"{df_filtrado['Kilos_Recolectados'].mean():,.2f} kg")

    st.markdown("---")
    st.subheader("Rendimiento Operativo por Supervisor")
    if 'Nombre_Completo' in df_filtrado.columns and not df_filtrado.empty:
        df_sup = df_filtrado.groupby('Nombre_Completo').agg(
            Cosechas=('ID_Lote', 'count'),
            Kg_Producidos=('Kilos_Recolectados', 'sum'),
            Hectareas=('Hectareas', 'sum'),
            Kg_Ha=('Rendimiento_Kg_Ha', 'mean')
        ).reset_index().sort_values(by='Kg_Ha', ascending=False)
        
        st.dataframe(df_sup.style.format({
            'Kg_Producidos': '{:,.2f}', 
            'Hectareas': '{:,.2f}', 
            'Kg_Ha': '{:,.2f}'
        }), use_container_width=True)

    if 'Turno' in df_filtrado.columns and not df_filtrado.empty:
        st.subheader("Productividad por Turno de Trabajo")
        df_turno = df_filtrado.groupby('Turno')['Rendimiento_Kg_Ha'].mean().reset_index()
        fig_turno = px.bar(df_turno, x='Turno', y='Rendimiento_Kg_Ha', color='Turno', text_auto='.2f', color_discrete_sequence=px.colors.sequential.Teal)
        fig_turno.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_turno, use_container_width=True)

# ==========================================
# PÁGINA 3 — PRODUCTIVIDAD
# ==========================================
elif pagina == "🟨 3. Productividad":
    st.title("🟨 Análisis de Productividad (Kg/Ha)")
    st.markdown("Evaluación detallada del rendimiento por unidad de área y correlaciones de eficiencia.")
    st.markdown("---")

    if not df_filtrado.empty:
        fig_scat = px.scatter(
            df_filtrado, x='Hectareas', y='Kilos_Recolectados', color='Cultivo',
            size='Kilos_Recolectados', hover_data=['ID_Lote', 'Nombre_Completo'],
            title="Correlación: Hectáreas vs. Kilos Cosechados"
        )
        fig_scat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_scat, use_container_width=True)

        st.markdown("""
            <div class="explanation-box">
            <b>Interpretación Gerencial:</b> Los puntos dispersos por encima de la tendencia principal representan lotes de alta eficiencia o cultivos con mayor densidad de rendimiento por hectárea.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No hay datos disponibles para los filtros seleccionados.")



# ==========================================
# PÁGINA 4 — CALIDAD DE DATOS
# ==========================================
elif pagina == "🟥 4. Calidad de Datos":
    st.title("🟥 Data Quality & Control de Anomalías")
    st.markdown("Auditoría de completitud de registros, certificaciones y detección de valores cero o fuera de rango.")
    st.markdown("---")

    total_reg = len(df_filtrado)
    if total_reg > 0:
        nulos_has = (df_filtrado['Hectareas'] == 0).sum() if 'Hectareas' in df_filtrado.columns else 0
        ceros_kilos = (df_filtrado['Kilos_Recolectados'] == 0).sum() if 'Kilos_Recolectados' in df_filtrado.columns else 0
        completitud = ((total_reg - nulos_has) / total_reg * 100) if total_reg > 0 else 0

        qc1, qc2, qc3, qc4 = st.columns(4)
        with qc1: st.metric("✅ Completitud de Datos", f"{completitud:.2f}%")
        with qc2: st.metric("⚠️ Cosechas con 0 Kg", f"{ceros_kilos:,} ({ceros_kilos/total_reg*100:.2f}%)")
        with qc3: st.metric("📋 Registros Filtrados", f"{total_reg:,}")
        with qc4: st.metric("🏷️ Certificación Registrada", "56.70% aprox.")

        st.markdown("---")
        st.subheader("🚨 Tabla de Auditoría: Registros con Anomalías Detectadas")
        
        # Filtrar anomalías de forma segura
        cols_requeridas = ['Kilos_Recolectados', 'Hectareas']
        if all(c in df_filtrado.columns for c in cols_requeridas):
            df_anomalias = df_filtrado[(df_filtrado['Kilos_Recolectados'] == 0) | (df_filtrado['Hectareas'] == 0)].copy()
            if not df_anomalias.empty:
                df_anomalias['Tipo_Anomalia'] = np.where(df_anomalias['Kilos_Recolectados'] == 0, 'Producción Cero (0 kg)', 'Hectáreas en Cero')
                
                # Seleccionar solo las columnas que SÍ existan en el DataFrame para evitar errores
                columnas_disponibles = [col for col in ['ID_Lote', 'Fecha', 'Nombre_Completo', 'Cultivo', 'Tipo_Anomalia'] if col in df_anomalias.columns]
                
                st.dataframe(df_anomalias[columnas_disponibles].head(50), use_container_width=True)
            else:
                st.success("¡Excelente! No se encontraron anomalías críticas con los filtros actuales.")
        else:
            st.warning("Faltan columnas numéricas clave en la base de datos para realizar la auditoría.")
    else:
        st.warning("No hay registros disponibles para los filtros seleccionados.")

        
# ==========================================
# PÁGINA 5 — ESTADÍSTICA AVANZADA
# ==========================================
elif pagina == "📊 5. Estadística Avanzada":
    st.title("📊 Estadística Descriptiva y Distribuciones")
    st.markdown("Análisis matemático profundo: Media, Mediana, Desviación Estándar, Varianza y Outliers.")
    st.markdown("---")

    serie_rend = df_filtrado['Rendimiento_Kg_Ha'].dropna()
    
    if not serie_rend.empty and len(serie_rend) > 1:
        media = serie_rend.mean()
        mediana = serie_rend.median()
        desv = serie_rend.std()
        varianza = serie_rend.var()
        cv = (desv / media * 100) if media > 0 else 0
        minimo = serie_rend.min()
        maximo = serie_rend.max()
        q25 = serie_rend.quantile(0.25)
        q75 = serie_rend.quantile(0.75)
        iqr = q75 - q25

        df_res_est = pd.DataFrame({
            'Medida Estadística': [
                'Media (Promedio kg/ha)', 'Mediana', 'Desviación Estándar', 
                'Varianza', 'Coeficiente de Variación (CV)', 'Mínimo', 'Máximo', 'Rango Intercuartílico (IQR)'
            ],
            'Valor': [
                f"{media:,.2f}", f"{mediana:,.2f}", f"{desv:,.2f}", 
                f"{varianza:,.2f}", f"{cv:.2f}%", f"{minimo:,.2f}", f"{maximo:,.2f}", f"{iqr:,.2f}"
            ]
        })
        st.dataframe(df_res_est, use_container_width=True)

        st.markdown("---")
        st.subheader("Boxplot de Distribución y Detección de Outliers")
        fig_box_adv = px.box(df_filtrado, y='Rendimiento_Kg_Ha', points="all", color_discrete_sequence=['#10b981'])
        fig_box_adv.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='white')
        st.plotly_chart(fig_box_adv, use_container_width=True)
        
        st.markdown("""
            <div class="explanation-box">
            <b>Interpretación Estadística:</b> El Boxplot permite visualizar los límites de cuartiles y detectar valores atípicos (outliers) extremos que se alejan del comportamiento normal de los lotes bajo los filtros seleccionados.
            </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("No hay suficientes datos numéricos para calcular las estadísticas con los filtros actuales.")