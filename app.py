import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
import os
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')

# =============================================================================
# 1. CONFIGURACIÓN Y ESTILOS (FRONTEND)
# =============================================================================
st.set_page_config(page_title="Insight Five0Five", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
    .stApp {
        background-color: #F8F9FA;
    }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {
        color: #1A365D !important;
    }
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E2E8F0;
    }
    [data-testid="metric-container"] {
        background-color: #FFFFFF;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #1A365D;
    }
    [data-testid="stMetricLabel"] p {
        color: #718096 !important;
        font-weight: 600;
    }
    [data-testid="stMetricValue"] {
        color: #1A365D !important;
        font-weight: bold;
    }
    .icon-text {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .material-icons {
        color: #1A365D;
    }
    </style>
""", unsafe_allow_html=True)

# =============================================================================
# 2. DEFINICIÓN DE INDICADORES METODOLÓGICOS
# =============================================================================
INDICATORS = {
    'IT.NET.USER.ZS': 'Uso de Internet (%)',
    'BX.TRF.PWKR.DT.GD.ZS': 'Remesas (% del PIB)',
    'EG.ELC.ACCS.ZS': 'Acceso a Electricidad (%)',
    'SE.XPD.TOTL.GD.ZS': 'Inversión en Educación (% PIB)',
    'SP.DYN.LE00.IN': 'Esperanza de Vida (Años)',
    'SH.XPD.CHEX.GD.ZS': 'Gasto en Salud (% PIB)',
    'FP.CPI.TOTL.ZG': 'Inflación (% Anual)',
    'SL.UEM.TOTL.ZS': 'Desempleo (%)'
}

INDICATOR_DESCRIPTIONS = {
    'Uso de Internet (%)': 'Mide la adopción digital en Nicaragua. Representa el porcentaje de la población que ha utilizado la red en los últimos 3 meses, reflejando el progreso en conectividad, inclusión tecnológica y acceso a la información.',
    'Remesas (% del PIB)': 'Indica el peso de las transferencias monetarias enviadas por nicaragüenses en el extranjero sobre la economía nacional. Un valor alto subraya la gran dependencia de estos flujos externos para el sustento de los hogares locales.',
    'Acceso a Electricidad (%)': 'Evalúa el porcentaje de habitantes conectados a la red eléctrica tanto en zonas urbanas como rurales. Es un pilar fundamental para el desarrollo de infraestructuras básicas, la productividad comercial y el confort moderno.',
    'Inversión en Educación (% PIB)': 'Muestra el gasto consolidado del gobierno en el sistema educativo respecto al tamaño de la economía. ⚠️ Nota Analítica: Las caídas abruptas a 0 o líneas planas prolongadas en la gráfica se deben frecuentemente a lagunas de reporte oficial (data gaps) en los servidores del Banco Mundial, no necesariamente a un recorte real del presupuesto interno.',
    'Esperanza de Vida (Años)': 'Promedio de años que se espera que viva un recién nacido manteniendo los patrones actuales de mortalidad. Funciona como el indicador sintético más completo sobre las condiciones socioeconómicas y la calidad de vida en el país.',
    'Gasto en Salud (% PIB)': 'Proporción de la riqueza nacional destinada al sistema sanitario. Refleja directamente la capacidad del país para brindar cobertura médica. *Nota: Periodos sin variación pueden indicar falta de actualización anual en las auditorías internacionales.*',
    'Inflación (% Anual)': 'Mide la tasa de variación anual de los precios al consumidor. Refleja el incremento del costo de vida y la pérdida de poder adquisitivo de la moneda local, siendo un indicador clave de estabilidad macroeconómica.',
    'Desempleo (%)': 'Porcentaje de la población económicamente activa que se encuentra sin trabajo pero está disponible y buscando empleo activamente. *Nota: Las variaciones atípicas o curvas muy suavizadas suelen ser resultado de estimaciones estadísticas modeladas por la OIT ante la ausencia de censos laborales continuos.*'
}

# =============================================================================
# 3. EXTRACCIÓN Y LIMPIEZA DE DATOS (DATA PIPELINE)
# =============================================================================
@st.cache_data(ttl=86400)
def _cargar_desde_api():
    import wbgapi as wb

    anio_actual = pd.Timestamp.now().year
    anios = range(anio_actual - 16, anio_actual)

    df = wb.data.DataFrame(list(INDICATORS.keys()), ['NIC'], time=anios)
    df = df.reset_index()

    if 'economy' not in df.columns:
        df['economy'] = 'NIC'

    df_long = df.melt(id_vars=['economy', 'series'], var_name='Year', value_name='Value')
    df_long['Year'] = df_long['Year'].str.replace('YR', '').astype(int)

    df_long['Value'] = df_long.groupby(['series'])['Value'].transform(
        lambda x: x.interpolate(method='linear', limit_direction='both')
    )

    df_long['Indicator'] = df_long['series'].map(INDICATORS)

    df_wide = df_long.pivot_table(
        index=['Year'], columns='Indicator', values='Value'
    ).reset_index()

    return df_long, df_wide


def _cargar_desde_db():
    ruta_db = os.environ.get("WORLDBANK_DB", "worldbank.db")

    if not os.path.exists(ruta_db):
        raise FileNotFoundError(
            "No hay conexion a internet ni base de datos local."
        )

    conexion = sqlite3.connect(ruta_db)
    query = """
        SELECT v.pais AS economy,
               v.indicador_codigo AS series,
               v.anio AS Year,
               v.valor AS Value,
               i.nombre AS Indicator
        FROM valores v
        JOIN indicadores i ON v.indicador_codigo = i.codigo
        ORDER BY v.anio
    """
    df_long = pd.read_sql_query(query, conexion)
    conexion.close()

    if df_long.empty:
        raise ValueError("La base de datos local esta vacia.")

    df_long['Value'] = df_long.groupby(['series'])['Value'].transform(
        lambda x: x.interpolate(method='linear', limit_direction='both')
    )

    df_wide = df_long.pivot_table(
        index=['Year'], columns='Indicator', values='Value'
    ).reset_index()

    return df_long, df_wide


@st.cache_data(ttl=86400)
def load_and_process_data():
    try:
        with st.spinner('Conectando con el Banco Mundial...'):
            return _cargar_desde_api()
    except Exception:
        try:
            with st.spinner('Sin internet. Cargando datos locales desde SQLite...'):
                return _cargar_desde_db()
        except (FileNotFoundError, ValueError):
            st.error(
                "No hay conexion a internet ni base de datos local.\n\n"
                "**Paso requerido:** Ejecute el siguiente comando en la terminal "
                "para crear la base de datos local:\n\n"
                "```\npython populate_db.py\n```\n\n"
                "*(Requiere conexion a internet para descargar los datos del Banco Mundial xd)*"
            )
            st.stop()


df_long, df_wide = load_and_process_data()

# =============================================================================
# 4. INTERFAZ DE USUARIO: SIDEBAR
# =============================================================================
with st.sidebar:
    st.markdown('<h1 class="icon-text"><span class="material-icons" style="font-size: 32px;">analytics</span> Insight Five0Five</h1>', unsafe_allow_html=True)
    st.markdown("### Monitor de Desarrollo Nacional")
    st.markdown("---")
    st.markdown("**Configuración del Análisis**")
    
    selected_indicator = st.selectbox("Indicador Principal:", list(INDICATORS.values()))
    
    st.markdown("---")
    st.markdown('<div class="icon-text"><span class="material-icons" style="color: #718096; font-size: 18px;">info</span> <span style="color: #718096; font-size: 0.9em;">Datos: Banco Mundial vía API o SQLite local si no hay internet.</span></div>', unsafe_allow_html=True)

# =============================================================================
# 5. PANEL DE INTELIGENCIA: KPIs
# =============================================================================
st.markdown('<h1 class="icon-text"><span class="material-icons" style="font-size: 36px;">dashboard</span> Panel de Inteligencia: Desarrollo de Nicaragua</h1>', unsafe_allow_html=True)
st.markdown("Plataforma interactiva para evaluar en detalle el desempeño socioeconómico e histórico de Nicaragua.")

st.markdown('<h3 class="icon-text"><span class="material-icons">trending_up</span> Indicadores Clave (Actualidad)</h3>', unsafe_allow_html=True)

df_nic = df_wide.sort_values('Year')

if not df_nic.empty:
    latest_year = df_nic['Year'].max()
    kpi_cols = st.columns(4)
    kpi_indicators = list(INDICATORS.values())[:4]
    
    for i, ind in enumerate(kpi_indicators):
        if ind in df_nic.columns:
            vals = df_nic[ind].dropna().values
            if len(vals) >= 2:
                val_curr, val_prev = vals[-1], vals[-2]
                delta = val_curr - val_prev
            elif len(vals) == 1:
                val_curr, delta = vals[-1], 0
            else:
                val_curr, delta = 0, 0
        else:
            val_curr, delta = 0, 0
            
        with kpi_cols[i]:
            st.metric(
                label=f"{ind}", 
                value=f"{val_curr:.1f}", 
                delta=f"{delta:.2f} pp" if delta != 0 else "0.0 pp",
                help=f"Datos del año {latest_year}. Variación respecto al año anterior."
            )
else:
    st.warning("No hay suficientes datos recientes.")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(f'''
<div style="background-color: #E2E8F0; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
    <div class="icon-text"><span class="material-icons">description</span> <strong>¿Qué estás viendo en pantalla?</strong></div>
    <p style="margin-top: 10px; margin-bottom: 0px;">{INDICATOR_DESCRIPTIONS[selected_indicator]}</p>
</div>
''', unsafe_allow_html=True)

# =============================================================================
# 6. VISUALIZACIONES PRINCIPALES
# =============================================================================
sns.set_theme(style="whitegrid")
col_left, col_right = st.columns((2, 1))

with col_left:
    st.markdown(f'**Evolución Histórica (15 Años): {selected_indicator}**')
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    
    plot_data = df_long[df_long['Indicator'] == selected_indicator]
    
    if not plot_data.empty and plot_data['Value'].notna().any():
        sns.lineplot(data=plot_data, x='Year', y='Value', marker='o', ax=ax1, color='#1A365D', linewidth=2.5)
        ax1.set_ylabel("Valor")
    else:
        ax1.text(0.5, 0.5, 'No hay datos disponibles', ha='center', va='center', color='#718096')
        ax1.set_axis_off()
        
    ax1.set_xlabel("Año")
    plt.tight_layout()
    st.pyplot(fig1)

with col_right:
    st.markdown("**Comparativa Últimos 5 Años**")
    fig2, ax2 = plt.subplots(figsize=(5, 5))
    
    last_5_years = df_nic.tail(5)
    
    if selected_indicator in last_5_years.columns and last_5_years[selected_indicator].notna().any():
        bars = ax2.bar(last_5_years['Year'].astype(str), last_5_years[selected_indicator], color='#4299E1')
        ax2.set_ylabel("Valor")
        ax2.set_xlabel("Año")
        
        for bar in bars:
            yval = bar.get_height()
            if not np.isnan(yval):
                ax2.text(bar.get_x() + bar.get_width()/2, yval + (abs(yval)*0.02), f"{yval:.1f}", ha='center', va='bottom', fontweight='bold', fontsize=9)
    else:
        ax2.text(0.5, 0.5, 'Sin datos recientes', ha='center', va='center', color='#718096')
        ax2.set_axis_off()
        
    plt.tight_layout()
    st.pyplot(fig2)

st.markdown("<br>", unsafe_allow_html=True)

# =============================================================================
# 7. ESTADÍSTICAS AVANZADAS Y ANOMALÍAS
# =============================================================================
col_bottom1, col_bottom2 = st.columns((1, 2))

with col_bottom1:
    st.markdown('<div class="icon-text"><span class="material-icons">warning</span> <strong>Detección de Anomalías (NumPy)</strong></div>', unsafe_allow_html=True)
    st.caption("Años con variaciones atípicas (outliers > 2 Desv. Estándar) para el indicador seleccionado.")
    
    if not df_nic.empty and selected_indicator in df_nic.columns:
        nic_values = df_nic[selected_indicator].dropna().values
        nic_years = df_nic.dropna(subset=[selected_indicator])['Year'].values
        
        if len(nic_values) > 1:
            diffs = np.diff(nic_values)
            mean_diff = np.nanmean(diffs)
            std_diff = np.nanstd(diffs)
            
            if std_diff > 0:
                outliers = np.where(np.abs(diffs - mean_diff) > 2 * std_diff)[0]
                if len(outliers) > 0:
                    for idx in outliers:
                        st.markdown(f'<div class="icon-text" style="color: #E53E3E;"><span class="material-icons" style="color: #E53E3E;">priority_high</span> <strong>{nic_years[idx+1]}</strong>: Variación abrupta de <strong>{diffs[idx]:+.2f} pp</strong></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="icon-text" style="color: #38A169;"><span class="material-icons" style="color: #38A169;">check_circle</span> Crecimiento estable, sin anomalías estadísticamente significativas.</div>', unsafe_allow_html=True)
            else:
                st.info("Variación constante o nula a lo largo de los años.")

with col_bottom2:
    st.markdown('<div class="icon-text"><span class="material-icons">scatter_plot</span> <strong>Correlación: Electricidad vs Internet</strong></div>', unsafe_allow_html=True)
    fig3, ax3 = plt.subplots(figsize=(9, 4))
    
    cols_to_check = ['Acceso a Electricidad (%)', 'Uso de Internet (%)']
    if all(c in df_wide.columns for c in cols_to_check):
        scatter_data = df_wide.dropna(subset=cols_to_check)
        if not scatter_data.empty:
            sns.scatterplot(
                data=scatter_data, 
                x='Acceso a Electricidad (%)', 
                y='Uso de Internet (%)', 
                size='Year', 
                sizes=(30, 150), 
                color="#2B6CB0", 
                ax=ax3,
                alpha=0.8
            )
        else:
            ax3.text(0.5, 0.5, 'Datos insuficientes', ha='center', va='center', color='#718096')
            ax3.set_axis_off()
    else:
        ax3.text(0.5, 0.5, 'Indicadores no disponibles', ha='center', va='center', color='#718096')
        ax3.set_axis_off()
    
    plt.legend(bbox_to_anchor=(1.01, 1), loc='upper left')
    plt.tight_layout()
    st.pyplot(fig3)

# =============================================================================
# 8. FOOTER
# =============================================================================
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #718096; font-size: 0.85em;'>"
    "Desarrollado en Python | <b>Insight Five0Five</b> | Librerías: Streamlit, Pandas, NumPy, Seaborn | Datos: Banco Mundial (API / SQLite local) | 2026 | Lerickson Gonzalez - UNHSJM"
    "</div>", 
    unsafe_allow_html=True
)
