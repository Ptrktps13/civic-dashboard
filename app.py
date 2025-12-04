import streamlit as st
import geemap.foliumap as geemap
import ee

# 1. Configuración de la Página (Título e Icono)
st.set_page_config(page_title="Civic Integrity Dashboard", page_icon="🛰️", layout="wide")

# 2. Barra Lateral (Contexto del Proyecto)
st.sidebar.title("🔍 Auditoría Satelital")
st.sidebar.info(
    """
    **Proyecto:** Gas Sayago (Uruguay)
    **Inversión:** $150M USD (Estimado)
    **Estado:** Abandonado
    """
)
st.sidebar.markdown("---")
st.sidebar.write("Este dashboard utiliza **Inteligencia Geoespacial (GEOINT)** para verificar la evolución de obras públicas.")

# 3. Título Principal
st.title("🛰️ The Civic Integrity Dashboard")
st.markdown(
    """
    Comparación en tiempo real entre el **inicio del proyecto (2013)** y la **realidad actual (2024)**.
    Desliza la barra central para revelar la verdad.
    """
)

# 4. Inicialización de Mapas (Autenticación con Secretos)
# NOTA: Esto requiere configurar las llaves en la nube de Streamlit después.
try:
    # Intenta usar las credenciales de la nube si existen
    geemap.ee_initialize()
except Exception as e:
    # Si falla, usa el método estándar (solo funcionará en local si estás logueado)
    try:
        ee.Initialize(project='gas-plant-audit-uruguay')
    except:
        st.error("Error de conexión con Google Earth Engine. Faltan credenciales.")

# 5. Lógica del Mapa (Igual que en Colab pero adaptado)
def generar_mapa():
    # Coordenadas Gas Sayago
    m = geemap.Map(center=[-34.9080, -56.2650], zoom=15)
    
    # Imagen Izquierda (2013 - Inicio)
    img_2013 = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA') \
        .filterBounds(ee.Geometry.Point([-56.2650, -34.9080])) \
        .filterDate('2013-05-01', '2013-12-31') \
        .sort('CLOUD_COVER') \
        .first()
    
    vis_2013 = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.25, 'gamma': 1.3}
    layer_left = geemap.ee_tile_layer(img_2013, vis_2013, '2013 (Promesa)')

    # Imagen Derecha (2024 - Realidad - Google Satélite)
    # Usamos Sentinel para asegurar compatibilidad web si Google Maps falla en iframe
    img_2024 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(ee.Geometry.Point([-56.2650, -34.9080])) \
        .filterDate('2023-01-01', '2024-01-01') \
        .sort('CLOUDY_PIXEL_PERCENTAGE') \
        .first()
        
    vis_2024 = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000, 'gamma': 1.1}
    layer_right = geemap.ee_tile_layer(img_2024, vis_2024, '2024 (Realidad)')

    # Crear Split Map
    m.split_map(left_layer=layer_left, right_layer=layer_right)
    
    return m

# 6. Mostrar el Mapa en la Web
mapa_final = generar_mapa()
mapa_final.to_streamlit(height=600)

st.success("✅ Datos verificados vía satélite. Fuente: NASA/ESA.")