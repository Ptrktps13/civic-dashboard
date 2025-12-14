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
    st.error("⚠️ Error de conexión con Google Earth Engine. Verifica que el 'EARTHENGINE_TOKEN' esté en los Secrets.")

def generar_mapa():
    # Centrado en Gas Sayago
    m = geemap.Map(center=[-34.9080, -56.2650], zoom=14)
    
    # IZQUIERDA: 2013 (Inicio - Landsat 8)
    img_2013 = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA') \
        .filterBounds(ee.Geometry.Point([-56.2650, -34.9080])) \
        .filterDate('2013-05-01', '2013-12-31') \
        .sort('CLOUD_COVER') \
        .first()
    
    vis_2013 = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.25, 'gamma': 1.3}
    left_layer = geemap.ee_tile_layer(img_2013, vis_2013, '2013 (Inicio)')

    # DERECHA: 2024 (Realidad - Sentinel 2)
    img_2024 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(ee.Geometry.Point([-56.2650, -34.9080])) \
        .filterDate('2023-01-01', '2024-01-01') \
        .sort('CLOUDY_PIXEL_PERCENTAGE') \
        .first()
        
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

try:
    # URL directa a tu archivo en GitHub
    url_datos = "https://raw.githubusercontent.com/Ptrktps13/civic-dashboard/main/financial_data.csv"
    
    df = pd.read_csv(url_datos)
    
    # --- CORRECCIÓN DEL ERROR ---
    # Creamos una columna nueva con el valor absoluto (positivo) para el TAMAÑO de la burbuja.
    # Así el -213 se convierte en 213 solo para calcular qué tan grande se dibuja.
    df["monto_size"] = df["monto_millones"].abs()
    
    # Crear Gráfica
    fig = px.scatter(df, x="fecha", y="monto_millones", 
                     color="tipo", 
                     size="monto_size",  # <--- Usamos la columna positiva aquí
                     hover_data=["evento", "fuente", "monto_millones"],
                     size_max=40,
                     title="Cronología Financiera: Promesas vs Pérdidas (Millones USD)",
                     color_discrete_map={
                         "Promesa": "blue", 
                         "Gasto Real": "orange", 
                         "Pérdida Neta": "red",
                         "Recupero": "green",
                         "Hito": "grey"
                     })
    
    fig.update_traces(mode='markers+lines')
    # Ajustamos el eje Y para que se vea bien el cero
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_layout(xaxis_title="Fecha del Evento", yaxis_title="Monto (Millones USD)")

    st.plotly_chart(fig, use_container_width=True)
    
    st.caption("ℹ️ Datos extraídos de fuentes oficiales. Los valores negativos indican pérdidas confirmadas para el Estado.")

except Exception as e:
    st.error(f"⚠️ Error cargando los datos financieros: {e}")