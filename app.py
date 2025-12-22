import streamlit as st
import geemap.foliumap as geemap
import ee
import pandas as pd
import plotly.express as px
import folium
import os

# --- 1. DICCIONARIO DE IDIOMAS (FASE 3 - COMPLETA) ---
TRANSLATIONS = {
    "ES": {
        "page_title": "Dashboard de Integridad Cívica",
        "sidebar_title": "🔍 Auditoría Satelital",
        "sidebar_case": "### Caso: Gas Sayago (Uruguay)",
        "sidebar_info": "Este dashboard cruza **Inteligencia Geoespacial (GEOINT)** con datos financieros públicos (**OSINT**).",
        "sources": "**Fuentes:** NASA Landsat, Sentinel-2, Auditoría PwC, Presidencia.",
        "main_title": "🛰️ Dashboard de Integridad Cívica: Fase 3",
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
        
        # --- DOSSIER FASE 3 ---
        "dossier_header": "3. Dossier de Investigación (Informe Ejecutivo)",
        "dossier_title": "📄 Ver Informe del Caso y Fuentes Originales",
        "dossier_text": """
        ### 📌 Resumen de los Hechos
        
        **1. La Promesa (2013):** El Estado anunció la construcción de la regasificadora con una inversión prometida de **$1.125 millones**.  
        🔗 *Fuente:* [Comunicado Oficial de Presidencia (2013)](https://www.gub.uy/presidencia/comunicacion/noticias/gas-sayago-gdf-suez-firman-contrato-para-construccion-operacion)
        
        **2. El Abandono (2015):** La constructora GNLS detuvo las obras. El contrato se rescindió, dejando inconclusa la escollera que se observa en el mapa.  
        🔗 *Prensa:* [Informe de Montevideo Portal sobre la rescisión](https://www.montevideo.com.uy/Noticias/Gobierno-rescindio-contrato-con-GNLS-por-regasificadora-uc285896)
        
        **3. El Costo Final (2021):** La auditoría forense confirmó una **pérdida neta de $213 millones** para los contribuyentes.  
        🔗 *Evidencia Clave:* [Descargar Auditoría Oficial (PwC)](https://www.gub.uy/presidencia/comunicacion/noticias/auditoria-encargada-ute-concluye-proyecto-gas-sayago-era-inviable-desde-su)
        """
    },
    "EN": {
        "page_title": "Civic Integrity Dashboard",
        "sidebar_title": "🔍 Satellite Audit",
        "sidebar_case": "### Case: Gas Sayago (Uruguay)",
        "sidebar_info": "This dashboard crosses **Geospatial Intelligence (GEOINT)** with public financial data (**OSINT**).",
        "sources": "**Sources:** NASA Landsat, Sentinel-2, PwC Audit, Presidency.",
        "main_title": "🛰️ Civic Integrity Dashboard: Phase 3",
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
        
        # --- DOSSIER PHASE 3 ---
        "dossier_header": "3. Investigative Dossier (Executive Report)",
        "dossier_title": "📄 View Case Report & Original Sources",
        "dossier_text": """
        ### 📌 Fact Sheet
        
        **1. The Promise (2013):** The government announced the plant with a promised investment of **$1.125 billion**.  
        🔗 *Source:* [Official Presidency Statement (2013)](https://www.gub.uy/presidencia/comunicacion/noticias/gas-sayago-gdf-suez-firman-contrato-para-construccion-operacion)
        
        **2. The Abandonment (2015):** Construction was halted by GNLS. The contract was rescinded, leaving the unfinished breakwater visible on the map.  
        🔗 *Press:* [News Report on Contract Termination](https://www.montevideo.com.uy/Noticias/Gobierno-rescindio-contrato-con-GNLS-por-regasificadora-uc285896)
        
        **3. The Final Cost (2021):** Forensic audit confirmed a **net loss of $213 million** for taxpayers.  
        🔗 *Key Evidence:* [Download Official Audit (PwC)](https://www.gub.uy/presidencia/comunicacion/noticias/auditoria-encargada-ute-concluye-proyecto-gas-sayago-era-inviable-desde-su)
        """
    },
    "FR": {
        "page_title": "Tableau de Bord d'Intégrité Civique",
        "sidebar_title": "🔍 Audit Satellitaire",
        "sidebar_case": "### Cas: Gas Sayago (Uruguay)",
        "sidebar_info": "Ce tableau croise **Renseignement Géospatial (GEOINT)** et données financières publiques (**OSINT**).",
        "sources": "**Sources:** NASA Landsat, Sentinel-2, Audit PwC, Présidence.",
        "main_title": "🛰️ Tableau de Bord d'Intégrité Civique: Phase 3",
        "main_desc": "Comparaison en temps réel entre la **Promesse Financière** et la **Réalité Physique**.",
        "map_header": "1. Preuve Physique (Le Terrain)",
        "layer_
