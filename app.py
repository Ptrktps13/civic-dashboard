import streamlit as st
import geemap.foliumap as geemap
import ee
import pandas as pd
import plotly.express as px
import folium
import os

# --- 1. DICCIONARIO DE IDIOMAS (CON EL NUEVO DOSSIER) ---
TRANSLATIONS = {
    "ES": {
        "page_title": "Dashboard de Integridad Cívica",
        "sidebar_title": "🔍 Auditoría Satelital",
        "sidebar_case": "### Caso: Gas Sayago (Uruguay)",
        "sidebar_info": "Este dashboard cruza **Inteligencia Geoespacial (GEOINT)** con datos financieros públicos (**OSINT**).",
        "sources": "**Fuentes:** NASA Landsat, Sentinel-2, Auditoría PwC, Presidencia.",
        "main_title": "🛰️ Dashboard de Integridad Cívica: Fase 2",
        "main_desc": "Comparación en tiempo real entre la **Promesa Financiera** y la **Realidad Física**.",
        "map_header": "1. Evidencia Física (El Terreno)",
        "layer_2013": "2013 (Inicio/Promesa)",
        "layer_2024": "2024 (Realidad/Abandono)",
        "finance_header": "2. Evidencia Documental (El Dinero)",
        "chart_title": "Cronología Financiera: Promesas vs Pérdidas (Millones USD)",
        "chart_x": "Fecha del Evento",
        "chart_y": "Monto (Millones USD)",
        "footer_caption": "ℹ️ Datos extraídos de fuentes oficiales. Los valores negativos indican pérdidas confirmadas.",
        "error_ee": "⚠️ Error de conexión con Google Earth Engine. Verifica los Secrets.",
        "error_data": "⚠️ Error cargando datos financieros: ",
        "label_left": "2013: INICIO (SOLO AGUA)",
        "label_right": "2024: REALIDAD (ABANDONO)",
        # --- NUEVO: SECCIÓN DOSSIER ---
        "dossier_header": "3. Dossier de Investigación (Informe Ejecutivo)",
        "dossier_title": "📄 Resumen del Caso: Proyecto Regasificadora Gas Sayago",
        "dossier_text": """
        **El Proyecto:** En 2013, el Estado uruguayo anunció la construcción de una planta regasificadora offshore con una inversión estimada de **$1.125 millones de dólares**, prometiendo cambiar la matriz energética del país.
        
        **La Falla:** La empresa constructora (GNLS) detuvo las obras en 2015 alegando problemas técnicos. El contrato fue rescindido, dejando en el agua una estructura de pilotes inconclusa que se puede observar en la imagen satelital de 2024.
        
        **El Costo:** Según la auditoría forense realizada por PwC (2021), el Estado uruguayo sufrió una **pérdida neta de $213 millones de dólares**. Esto incluye gastos operativos, legales y de infraestructura inútil que se mantuvieron años después de la cancelación del proyecto.
        """
    },
    "EN": {
        "page_title": "Civic Integrity Dashboard",
        "sidebar_title": "🔍 Satellite Audit",
        "sidebar_case": "### Case: Gas Sayago (Uruguay)",
        "sidebar_info": "This dashboard crosses **Geospatial Intelligence (GEOINT)** with public financial data (**OSINT**).",
        "sources": "**Sources:** NASA Landsat, Sentinel-2, PwC Audit, Presidency.",
        "main_title": "🛰️ Civic Integrity Dashboard: Phase 2",
        "main_desc": "Real-time comparison between **Financial Promise** and **Physical Reality**.",
        "map_header": "1. Physical Evidence (The Ground)",
        "layer_2013": "2013 (Start/Promise)",
        "layer_2024": "2024 (Reality/Abandoned)",
        "finance_header": "2. Documentary Evidence (The Money)",
        "chart_title": "Financial Timeline: Promises vs Losses (Million USD)",
        "chart_x": "Event Date",
        "chart_y": "Amount (Million USD)",
        "footer_caption": "ℹ️ Data extracted from official sources. Negative values indicate confirmed losses.",
        "error_ee": "⚠️ Connection error with Google Earth Engine. Check Secrets.",
        "error_data": "⚠️ Error loading financial data: ",
        "label_left": "2013: START (WATER ONLY)",
        "label_right": "2024: REALITY (ABANDONED)",
        # --- NEW: DOSSIER SECTION ---
        "dossier_header": "3. Investigative Dossier (Executive Report)",
        "dossier_title": "📄 Case Summary: Gas Sayago Regasification Project",
        "dossier_text": """
        **The Project:** In 2013, the Uruguayan government announced the construction of an offshore regasification plant with an estimated investment of **$1.125 billion USD**, promising to transform the country's energy matrix.
        
        **The Failure:** The construction firm (GNLS) halted works in 2015 citing technical issues. The contract was rescinded, leaving an unfinished structure of piles in the ocean, clearly visible in the 2024 satellite imagery.
        
        **The Cost:** According to a forensic audit by PwC (2021), the Uruguayan State suffered a **net loss of $213 million USD**. This includes operational, legal, and useless infrastructure costs incurred years after the project's cancellation.
        """
    },
    "FR": {
        "page_title": "Tableau de Bord d'Intégrité Civique",
        "sidebar_title": "🔍 Audit Satellitaire",
        "sidebar_case": "### Cas: Gas Sayago (Uruguay)",
        "sidebar_info": "Ce tableau croise **Renseignement Géospatial (GEOINT)** et données financières publiques (**OSINT**).",
        "sources": "**Sources:** NASA Landsat, Sentinel-2, Audit PwC, Présidence.",
        "main_title": "🛰️ Tableau de Bord d'Intégrité Civique: Phase 2",
        "main_desc": "Comparaison en temps réel entre la **Promesse Financière** et la **Réalité Physique**.",
        "map_header": "1. Preuve Physique (Le Terrain)",
        "layer_2013": "2013 (Début/Promesse)",
        "layer_2024": "2024 (Réalité/Abandon)",
        "finance_header": "2. Preuve Documentaire (L'Argent)",
        "chart_title": "Chronologie Financière: Promesses vs Pertes (Millions USD)",
        "chart_x": "Date de l'événement",
        "chart_y": "Montant (Millions USD)",
        "footer_caption": "ℹ️ Données extraites de sources officielles. Les valeurs négatives indiquent des pertes confirmées.",
        "error_ee": "⚠️ Erreur de connexion avec Google Earth Engine. Vérifiez les Secrets.",
        "error_data": "⚠️ Erreur de chargement des données financières: ",
        "label_left": "2013: DÉBUT", 
        "label_right": "2024: RÉALITÉ",
        # --- NOUVEAU: DOSSIER ---
        "dossier_header": "3. Dossier d'Enquête (Rapport Exécutif)",
        "dossier_title": "📄 Résumé du cas : Projet de Regazéification Gas Sayago",
        "dossier_text": """
        **Le Projet :** En 2013, l'État uruguayen a annoncé la construction d'une usine de regazéification offshore avec un investissement estimé à **1,125 milliard de dollars**, promettant de changer la matrice énergétique du pays.
        
        **L'Échec :** L'entreprise de construction (GNLS) a arrêté les travaux en 2015 en invoquant des problèmes techniques. Le contrat a été résilié, laissant dans l'eau une structure inachevée visible sur l'image satellite de 2024.
        
        **Le Coût :** Selon l'audit de PwC (2021), l'État a subi une **perte nette de 213 millions de dollars**. Cela inclut des frais opérationnels et d'infrastructures inutiles maintenus des années après l'annulation.
        """
    },
    "PT": {
        "page_title": "Painel de Integridade Cívica",
        "sidebar_title": "🔍 Auditoria por Satélite",
        "sidebar_case": "### Caso: Gás Sayago (Uruguai)",
        "sidebar_info": "Este painel cruza **Inteligência Geoespacial (GEOINT)** com dados financeiros públicos (**OSINT**).",
        "sources": "**Fontes:** NASA Landsat, Sentinel-2, Auditoria PwC, Presidência.",
        "main_title": "🛰️ Painel de Integridade Cívica: Fase 2",
        "main_desc": "Comparação em tempo real entre a **Promessa Financeira** e a **Realidade Física**.",
        "map_header": "1. Evidência Física (O Terreno)",
        "layer_2013": "2013 (Início/Promessa)",
        "layer_2024": "2024 (Realidade/Abandono)",
        "finance_header": "2. Evidência Documental (O Dinheiro)",
        "chart_title": "Cronologia Financeira: Promessas vs Perdas (Milhões USD)",
        "chart_x": "Data do Evento",
        "chart_y": "Montante (Milhões USD)",
        "footer_caption": "ℹ️ Dados extraídos de fontes oficiais. Valores negativos indicam perdas confirmadas.",
        "error_ee": "⚠️ Erro de conexão com Google Earth Engine. Verifique os Secrets.",
        "error_data": "⚠️ Erro ao carregar dados financeiros: ",
        "label_left": "2013: INÍCIO", 
        "label_right": "2024: REALIDADE",
        # --- NOVO: DOSSIER ---
        "dossier_header": "3. Dossiê de Investigação (Relatório Executivo)",
        "dossier_title": "📄 Resumo do Caso: Projeto Gás Sayago",
        "dossier_text": """
        **O Projeto:** Em 2013, o governo uruguaio anunciou a construção de uma planta de regaseificação offshore com um investimento estimado de **$1.125 milhões de dólares**, prometendo mudar a matriz energética do país.
        
        **A Falha:** A construtora (GNLS) parou as obras em 2015 alegando problemas técnicos. O contrato foi rescindido, deixando no mar uma estrutura de estacas inacabada visível na imagem de satélite de 2024.
        
        **O Custo:** Segundo auditoria da PwC (2021), o Estado sofreu uma **perda líquida de $213 milhões de dólares**. Isso inclui gastos operacionais e de infraestrutura inútil mantidos anos após o cancelamento.
        """
    }
}

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Civic Integrity Dashboard", page_icon="🛰️", layout="wide")

# --- SELECTOR DE IDIOMA ---
st.sidebar.markdown("## 🌐 Language / Idioma")
lang_options = {"Español": "ES", "English": "EN", "Français": "FR", "Português": "PT"}
selected_lang_name = st.sidebar.selectbox("Seleccionar / Select:", list(lang_options.keys()))
lang_code = lang_options[selected_lang_name]
text = TRANSLATIONS[lang_code]

# --- BARRA LATERAL ---
st.sidebar.title(text["sidebar_title"])
st.sidebar.markdown(text["sidebar_case"])
st.sidebar.info(text["sidebar_info"])
st.sidebar.markdown("---")
st.sidebar.write(text["sources"])

# --- CONTENIDO PRINCIPAL ---
st.title(text["main_title"])
st.markdown(text["main_desc"])

# --- CONEXIÓN BLINDADA CON EARTH ENGINE ---
def iniciar_earth_engine():
    """Intenta conectar con GEE usando el Token de los Secrets."""
    try:
        # 1. Recuperar el token de los secretos de Streamlit
        if "EARTHENGINE_TOKEN" in st.secrets:
            # Pasamos el token a las variables de entorno para que geemap lo encuentre
            os.environ["EARTHENGINE_TOKEN"] = st.secrets["EARTHENGINE_TOKEN"]
        
        # 2. Inicializar usando el proyecto por defecto o específico
        geemap.ee_initialize(project='gas-plant-audit-uruguay')
        return True
        
    except Exception as e:
        st.error(f"⚠️ Error Crítico de Conexión: {e}")
        st.stop()
        return False

# Ejecutamos la conexión
iniciar_earth_engine()

# --- FUNCIÓN PARA TEXTO FLOTANTE ---
def add_text_to_map(m, text_left, text_right):
    """Agrega cuadros de texto en las esquinas inferiores del mapa."""
    box_style = """
        position: absolute;
        bottom: 20px;
        z-index: 9999;
        background-color: white;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        font-weight: bold;
        font-size: 14px;
        font-family: sans-serif;
    """
    left_html = f'<div style="{box_style} left: 20px;">{text_left}</div>'
    right_html = f'<div style="{box_style} right: 20px;">{text_right}</div>'
    
    m.get_root().html.add_child(folium.Element(left_html))
    m.get_root().html.add_child(folium.Element(right_html))

def generar_mapa():
    m = geemap.Map(center=[-34.9080, -56.2650], zoom=14)
    
    # 2013
    img_2013 = ee.ImageCollection('LANDSAT/LC08/C02/T1_TOA') \
        .filterBounds(ee.Geometry.Point([-56.2650, -34.9080])) \
        .filterDate('2013-05-01', '2013-12-31') \
        .sort('CLOUD_COVER') \
        .first()
    vis_2013 = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 0.25, 'gamma': 1.3}
    left_layer = geemap.ee_tile_layer(img_2013, vis_2013, text["layer_2013"])

    # 2024
    img_2024 = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED') \
        .filterBounds(ee.Geometry.Point([-56.2650, -34.9080])) \
        .filterDate('2023-01-01', '2024-01-01') \
        .sort('CLOUDY_PIXEL_PERCENTAGE') \
        .first()
    vis_2024 = {'bands': ['B4', 'B3', 'B2'], 'min': 0, 'max': 3000, 'gamma': 1.1}
    right_layer = geemap.ee_tile_layer(img_2024, vis_2024, text["layer_2024"])

    m.split_map(left_layer, right_layer)
    add_text_to_map(m, text["label_left"], text["label_right"])
    return m

st.subheader(text["map_header"])
mapa = generar_mapa()
mapa.to_streamlit(height=500)

# --- FINANZAS (OSINT) ---
st.markdown("---")
st.subheader(text["finance_header"])

try:
    url_datos = "https://raw.githubusercontent.com/Ptrktps13/civic-dashboard/main/financial_data.csv"
    df = pd.read_csv(url_datos)
    
    # Cálculo para tamaño de burbuja
    df["monto_size"] = df["monto_millones"].abs()
    
    fig = px.scatter(df, x="fecha", y="monto_millones", 
                     color="tipo", 
                     size="monto_size", 
                     hover_data=["evento", "fuente", "monto_millones"],
                     size_max=40,
                     title=text["chart_title"],
                     color_discrete_map={
                         "Promesa": "blue", 
                         "Gasto Real": "orange", 
                         "Pérdida Neta": "red",
                         "Recupero": "green",
                         "Hito": "grey"
                     })
    
    fig.update_traces(mode='markers+lines')
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.update_layout(xaxis_title=text["chart_x"], yaxis_title=text["chart_y"])

    st.plotly_chart(fig, use_container_width=True)
    st.caption(text["footer_caption"])

except Exception as e:
    st.error(text["error_data"] + str(e))

# --- 6. DOSSIER (NARRATIVA - NUEVO) ---
st.markdown("---")
st.subheader(text["dossier_header"])

# Bloque desplegable
with st.expander(text["dossier_title"], expanded=False):
    st.markdown(text["dossier_text"])
    st.info("ℹ️ " + text["sources"])
