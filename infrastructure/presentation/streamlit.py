from typing import Callable, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import warnings

from config.settings import INDICATOR_DESCRIPTIONS, INDICATORS
from domain.exceptions import DatosNoEncontradosError
from domain.ports import AnomalyDetectorPort


def render_dashboard(
    data_loader: Callable[[], Tuple[pd.DataFrame, pd.DataFrame]],
    anomaly_detector: AnomalyDetectorPort,
) -> None:
    warnings.filterwarnings("ignore")

    st.set_page_config(
        page_title="Insight Five0Five",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
    .stApp { background-color: #F8F9FA; }
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown { color: #1A365D !important; }
    [data-testid="stSidebar"] { background-color: #FFFFFF !important; border-right: 1px solid #E2E8F0; }
    [data-testid="metric-container"] {
        background-color: #FFFFFF; padding: 15px; border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05); border-left: 5px solid #1A365D;
    }
    [data-testid="stMetricLabel"] p { color: #718096 !important; font-weight: 600; }
    [data-testid="stMetricValue"] { color: #1A365D !important; font-weight: bold; }
    .icon-text { display: flex; align-items: center; gap: 8px; }
    .material-icons { color: #1A365D; }
    </style>
    """,
        unsafe_allow_html=True,
    )

    try:
        try:
            df_long, df_wide = data_loader()
        except DatosNoEncontradosError as e:
            st.error(str(e))
            st.stop()

        with st.sidebar:
            st.markdown(
                '<h1 class="icon-text"><span class="material-icons" style="font-size: 32px;">analytics</span> Insight Five0Five</h1>',
                unsafe_allow_html=True,
            )
            st.markdown("### Monitor de Desarrollo Nacional")
            st.markdown("---")
            st.markdown(
                '<div style="background-color: #F7FAFC; padding: 12px; border-radius: 8px; border: 1px solid #E2E8F0; margin-bottom: 10px;">'
                '<div style="display: flex; align-items: center; gap: 8px;">'
                '<span class="material-icons" style="font-size: 20px; color: #1A365D;">settings</span>'
                '<strong style="color: #1A365D; font-size: 0.95rem;">Configuración del Análisis</strong>'
                '</div>'
                '<span style="font-size: 0.8rem; color: #4A5568; display: block; margin-top: 4px;">'
                'Seleccione el indicador principal para visualizar en las gráficas y análisis detallados.'
                '</span>'
                '</div>',
                unsafe_allow_html=True,
            )

            selected_indicator = st.selectbox(
                "Indicador Principal:", list(INDICATORS.values())
            )

            st.markdown("---")
            st.markdown(
                '<div class="icon-text"><span class="material-icons" style="color: #718096; font-size: 18px;">info</span>'
                ' <span style="color: #718096; font-size: 0.9em;">Datos: Banco Mundial vía API o SQLite local.</span></div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            '''
            <div style="background: linear-gradient(135deg, #A0AEC0 0%, #E2E8F0 100%); padding: 25px; border-radius: 12px; margin-bottom: 25px; color: white; box-shadow: 0 4px 15px rgba(43, 108, 176, 0.25);">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span class="material-icons" style="font-size: 40px; color: #90CDF4;">dashboard</span>
                    <h1 style="margin: 0; font-size: 2.2rem; font-weight: 700; color: white !important; letter-spacing: -0.5px; line-height: 1.2;">
                        Panel de Inteligencia: Desarrollo de Nicaragua
                    </h1>
                </div>
                <p style="margin: 10px 0 0 0; color: #E2E8F0 !important; font-size: 1.1rem; opacity: 0.9;">
                    Plataforma interactiva para evaluar en detalle el desempeño socioeconómico e histórico de Nicaragua.
                </p>
            </div>
            ''',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<h3 class="icon-text"><span class="material-icons">trending_up</span> Indicadores Clave (Actualidad)</h3>',
            unsafe_allow_html=True,
        )

        df_nic = df_wide.sort_values("Year")

        if not df_nic.empty:
            latest_year = df_nic["Year"].max()
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

                # Determine the unit based on the indicator name to be accurate
                if "Años" in ind:
                    unit = "años"
                else:
                    unit = "pp"

                with kpi_cols[i]:
                    st.metric(
                        label=f"{ind}",
                        value=f"{val_curr:.1f}",
                        delta=f"{delta:.2f} {unit}" if delta != 0 else f"0.00 {unit}",
                        help=f"Datos del año {latest_year}. Variación respecto al año anterior.",
                    )
        else:
            st.warning("No hay suficientes datos recientes.")

        st.markdown("<br>", unsafe_allow_html=True)

        # Beautiful description card using .get() to avoid KeyErrors and show clean messages
        description = INDICATOR_DESCRIPTIONS.get(
            selected_indicator, 
            f"No se encontró una descripción detallada para '{selected_indicator}' en la configuración."
        )
        st.markdown(
            f'''
            <div style="background-color: #F0F4F8; padding: 18px; border-radius: 8px; border-left: 4px solid #2B6CB0; margin-bottom: 25px; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <div class="icon-text" style="color: #1A365D; font-size: 1.05rem; font-weight: 600; display: flex; align-items: center; gap: 8px;">
                    <span class="material-icons" style="color: #2B6CB0;">info</span>
                    <span>¿Qué estás viendo en pantalla?</span>
                </div>
                <p style="margin-top: 10px; margin-bottom: 0px; color: #2D3748; line-height: 1.5; font-size: 0.95rem;">
                    {description}
                </p>
            </div>
            ''',
            unsafe_allow_html=True,
        )

        sns.set_theme(style="whitegrid")
        col_left, col_right = st.columns((2, 1))

        with col_left:
            st.markdown(f"**Evolución Histórica (15 Años): {selected_indicator}**")
            fig1, ax1 = plt.subplots(figsize=(10, 5))

            plot_data = df_long[df_long["Indicator"] == selected_indicator]

            if not plot_data.empty and plot_data["Value"].notna().any():
                sns.lineplot(
                    data=plot_data,
                    x="Year",
                    y="Value",
                    marker="o",
                    ax=ax1,
                    color="#1A365D",
                    linewidth=2.5,
                )
                ax1.set_ylabel("Valor")
            else:
                ax1.text(
                    0.5,
                    0.5,
                    "No hay datos disponibles",
                    ha="center",
                    va="center",
                    color="#718096",
                )
                ax1.set_axis_off()

            ax1.set_xlabel("Año")
            plt.tight_layout()
            st.pyplot(fig1)

        with col_right:
            st.markdown("**Comparativa Últimos 5 Años**")
            fig2, ax2 = plt.subplots(figsize=(5, 5))

            last_5_years = df_nic.tail(5)

            if (
                selected_indicator in last_5_years.columns
                and last_5_years[selected_indicator].notna().any()
            ):
                bars = ax2.bar(
                    last_5_years["Year"].astype(str),
                    last_5_years[selected_indicator],
                    color="#4299E1",
                )
                ax2.set_ylabel("Valor")
                ax2.set_xlabel("Año")

                for bar in bars:
                    yval = bar.get_height()
                    if not np.isnan(yval):
                        ax2.text(
                            bar.get_x() + bar.get_width() / 2,
                            yval + (abs(yval) * 0.02),
                            f"{yval:.1f}",
                            ha="center",
                            va="bottom",
                            fontweight="bold",
                            fontsize=9,
                        )
            else:
                ax2.text(
                    0.5,
                    0.5,
                    "Sin datos recientes",
                    ha="center",
                    va="center",
                    color="#718096",
                )
                ax2.set_axis_off()

            plt.tight_layout()
            st.pyplot(fig2)

        st.markdown("<br>", unsafe_allow_html=True)

        col_bottom1, col_bottom2 = st.columns((1, 2))

        with col_bottom1:
            st.markdown(
                '<div class="icon-text"><span class="material-icons">warning</span> <strong>Detección de Anomalías (NumPy)</strong></div>',
                unsafe_allow_html=True,
            )
            st.caption(
                "Años con variaciones atípicas (outliers > 2 Desv. Estándar) para el indicador seleccionado."
            )

            if not df_nic.empty and selected_indicator in df_nic.columns:
                nic_values = df_nic[selected_indicator].tolist()
                nic_years = df_nic["Year"].tolist()

                anomalies = anomaly_detector.detect_anomalies(nic_years, nic_values)

                if len(anomalies) > 0:
                    for year, var in anomalies:
                        # Determine unit for anomalies as well
                        anom_unit = "años" if "Años" in selected_indicator else "pp"
                        st.markdown(
                            f'<div class="icon-text" style="color: #E53E3E;"><span class="material-icons" style="color: #E53E3E;">priority_high</span> <strong>{year}</strong>: Variación abrupta de <strong>{var:+.2f} {anom_unit}</strong></div>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown(
                        '<div class="icon-text" style="color: #38A169;"><span class="material-icons" style="color: #38A169;">check_circle</span> Crecimiento estable, sin anomalías estadísticamente significativas.</div>',
                        unsafe_allow_html=True,
                    )

        with col_bottom2:
            st.markdown(
                '<div class="icon-text"><span class="material-icons">scatter_plot</span> <strong>Correlación: Electricidad vs Internet</strong></div>',
                unsafe_allow_html=True,
            )
            fig3, ax3 = plt.subplots(figsize=(9, 4))

            cols_to_check = ["Acceso a Electricidad (%)", "Uso de Internet (%)"]
            if all(c in df_wide.columns for c in cols_to_check):
                scatter_data = df_wide.dropna(subset=cols_to_check)
                if not scatter_data.empty:
                    sns.scatterplot(
                        data=scatter_data,
                        x="Acceso a Electricidad (%)",
                        y="Uso de Internet (%)",
                        size="Year",
                        sizes=(30, 150),
                        color="#2B6CB0",
                        ax=ax3,
                        alpha=0.8,
                    )
                else:
                    ax3.text(
                        0.5,
                        0.5,
                        "Datos insuficientes",
                        ha="center",
                        va="center",
                        color="#718096",
                    )
                    ax3.set_axis_off()
            else:
                ax3.text(
                    0.5,
                    0.5,
                    "Indicadores no disponibles",
                    ha="center",
                    va="center",
                    color="#718096",
                )
                ax3.set_axis_off()

            plt.legend(bbox_to_anchor=(1.01, 1), loc="upper left")
            plt.tight_layout()
            st.pyplot(fig3)

        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #718096; font-size: 0.85em;'>"
            "Desarrollado en Python | <b>Insight Five0Five</b> | Librerías: Streamlit, Pandas, NumPy, Seaborn | Datos: Banco Mundial (API / SQLite local) | 2026 | Lerickson Gonzalez - UNHSJM"
            "</div>",
            unsafe_allow_html=True,
        )

    except Exception as e:
        import traceback
        st.markdown(
            f"""
            <div style="background-color: #FFF5F5; border: 1px solid #FEB2B2; border-left: 5px solid #E53E3E; padding: 20px; border-radius: 8px; margin: 20px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
                <h3 style="color: #C53030 !important; margin-top: 0; display: flex; align-items: center; gap: 8px; font-family: system-ui, -apple-system, sans-serif;">
                    <span class="material-icons" style="color: #E53E3E; font-size: 28px; vertical-align: middle;">error</span>
                    Error en la Visualización o Configuración
                </h3>
                <p style="color: #742A2A !important; font-size: 1.05rem; font-weight: 600; margin-top: 10px;">
                    Se ha detectado un error al procesar o renderizar los datos del indicador seleccionado.
                </p>
                <div style="background-color: #FFF; padding: 15px; border-radius: 6px; border: 1px solid #FED7D7; font-family: 'Courier New', Courier, monospace; font-size: 0.9rem; color: #2D3748; margin-top: 15px; overflow-x: auto; box-shadow: inset 0 1px 3px rgba(0,0,0,0.05);">
                    <strong>Detalle Técnico:</strong> {type(e).__name__}: {str(e)}
                </div>
                <div style="margin-top: 20px; color: #742A2A !important; font-size: 0.95rem; line-height: 1.6;">
                    <strong>Sugerencias para resolverlo:</strong>
                    <ul style="margin-top: 8px; padding-left: 20px;">
                        <li>Verifique que el indicador seleccionado esté correctamente configurado con su respectiva descripción en <code>config/settings.py</code>.</li>
                        <li>Asegúrese de que la base de datos local esté sincronizada ejecutando el comando <code>python populate_db.py</code> en su terminal.</li>
                        <li>Si acaba de agregar o modificar un indicador, limpie la caché de Streamlit desde la esquina superior derecha o reinicie la aplicación.</li>
                    </ul>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        print(f"Error detectado en el dashboard: {e}")
        traceback.print_exc()
