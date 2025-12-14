import streamlit as st
import geemap.foliumap as geemap
import ee
import pandas as pd
import plotly.express as px
import folium # Necesitamos importar folium directamente para el truco del texto

# --- 1. DICCIONARIO DE IDIOMAS ---
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
        # NUEVOS TEXTOS PARA LAS ETIQUETAS
        "label_left": "2013: INICIO (SOLO AGUA)",
        "label_right": "2024: REALIDAD (ABANDONO)"
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
        "label_right": "20