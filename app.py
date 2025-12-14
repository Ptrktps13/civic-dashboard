import streamlit as st
import geemap.foliumap as geemap
import ee
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Civic Integrity Dashboard", page_icon="🛰️", layout="wide")

# --- 2. BARRA LATERAL (CONTEXTO) ---
st.sidebar.title("🔍 Auditoría Satelital")
st.sidebar.markdown("### Caso: Gas Sayago (Uruguay)")
st.sidebar.info(
    """
    Este dashboard cruza **Inteligencia Geoespacial (GEOINT)** con datos financieros públicos (**OSINT**).
    """
)
st.sidebar.markdown("---")
st.sidebar.write("Fuentes: NASA Landsat, Sentinel-2, Auditoría PwC, Presidencia.")

# --- 3. TÍTULO ---
st.title("🛰️ Civic Integrity Dashboard: Fase 2")
st.markdown(
    """
    Comparación en tiempo real entre la **Promesa Financiera** y la **Realidad Física**.
    """
)

# --- 4. MAPA SATELITAL (GEOINT) ---
try:
    geemap.ee_initialize()
except Exception as e:
    # Intento de reconexión con credenciales si falla la primera
    try:
        ee.Initialize(project='gas-plant-audit-uruguay')
    except:
        st.error("⚠️ Error de conexión con Google Earth Engine. Verifica tus 'Secrets' en Streamlit.")

def generar_mapa():
    m = geemap.Map(center=[-34.9080, -56.2650], zoom=14)
    
    # 2013 (Izquierda)
    img_2013 = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA').filterBounds(ee.Geometry.Point([-56.2650, -34.9080])).filterDate('2013-05-01', '2013-12-31').sort('CLOUD_COVER').first()
    vis_2013 = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.25, 'gamma': 1.3}
    left_layer = geemap.ee_tile_layer(img_2013, vis_2013, '2013 (Inicio)')

    # 2024 (Derecha)
    img_2024 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED').filterBounds(ee.Geometry.Point([-56.2650, -34.9080])).filterDate('2023-01-01', '2024-01-01').sort('CLOUDY_PIXEL_PERCENTAGE').first()
    vis_2024 = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000, 'gamma': 1.1}
    right_layer = geemap.ee_tile_layer(img_2024, vis_2024, '2024 (Realidad)')

    m.split_map(left_layer, right_layer)
    return m

st.subheader("1. Evidencia Física (El Terreno)")
mapa = generar_mapa()
mapa.to_streamlit(height=500)

# --- 5. LÍNEA DE TIEMPO FINANCIERA (OSINT) ---
st.markdown("---")
st.subheader("2. Evidencia Documental (El Dinero)")

# Cargar datos
try:
    df = pd.read_csv("financial_data.csv")
    
    # Crear Gráfica Interactiva
    fig = px.scatter(df, x="fecha", y="monto_millones", 
                     color="tipo", 
                     size="monto_millones", 
                     hover_data=["evento", "fuente"],
                     size_max=40,
                     title="Cronología Financiera: Promesas vs Pérdidas (Millones USD)",
                     color_discrete_map={
                         "Promesa": "blue", 
                         "Gasto Real": "orange", 
                         "Pérdida Neta": "red",
                         "Recupero": "green",
                         "Hito": "grey"
                     })
    
    # Añadir líneas verticales para conectar los puntos con el eje X
    fig.update_traces(mode='markers+lines')
    fig.update_layout(xaxis_title="Año", yaxis_title="Monto (Millones USD)")

    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("ℹ️ Pasa el mouse sobre los puntos para ver la fuente de la información.")

except Exception as e:
    st.warning("⚠️ No se encontró el archivo de datos financieros. Asegúrate de subir 'financial_data.csv' al repositorio.")