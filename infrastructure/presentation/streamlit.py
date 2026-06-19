from typing import Callable, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
import warnings

from config.settings import INDICATOR_DESCRIPTIONS, INDICATORS
from domain.exceptions import DatosNoEncontradosError


def render_dashboard(data_loader: Callable[[], Tuple[pd.DataFrame, pd.DataFrame]]) -> None:
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
        st.markdown("**Configuracion del Analisis**")

        selected_indicator = st.selectbox(
            "Indicador Principal:", list(INDICATORS.values())
        )

        st.markdown("---")
        st.markdown(
            '<div class="icon-text"><span class="material-icons" style="color: #718096; font-size: 18px;">info</span>'
            ' <span style="color: #718096; font-size: 0.9em;">Datos: Banco Mundial via API o SQLite local si no hay internet.</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown(
        '<h1 class="icon-text"><span class="material-icons" style="font-size: 36px;">dashboard</span> Panel de Inteligencia: Desarrollo de Nicaragua</h1>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "Plataforma interactiva para evaluar en detalle el desempeno socioeconomico e historico de Nicaragua."
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

            with kpi_cols[i]:
                st.metric(
                    label=f"{ind}",
                    value=f"{val_curr:.1f}",
                    delta=f"{delta:.2f} pp" if delta != 0 else "0.0 pp",
                    help=f"Datos del año {latest_year}. Variacion respecto al año anterior.",
                )
    else:
        st.warning("No hay suficientes datos recientes.")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown(
        f'''
    <div style="background-color: #E2E8F0; padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <div class="icon-text"><span class="material-icons">description</span> <strong>¿Que estas viendo en pantalla?</strong></div>
        <p style="margin-top: 10px; margin-bottom: 0px;">{INDICATOR_DESCRIPTIONS[selected_indicator]}</p>
    </div>
    ''',
        unsafe_allow_html=True,
    )

    sns.set_theme(style="whitegrid")
    col_left, col_right = st.columns((2, 1))

    with col_left:
        st.markdown(f"**Evolucion Historica (15 Años): {selected_indicator}**")
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
        st.markdown("**Comparativa Ultimos 5 Años**")
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
            '<div class="icon-text"><span class="material-icons">warning</span> <strong>Deteccion de Anomalias (NumPy)</strong></div>',
            unsafe_allow_html=True,
        )
        st.caption(
            "Años con variaciones atipicas (outliers > 2 Desv. Estandar) para el indicador seleccionado."
        )

        if not df_nic.empty and selected_indicator in df_nic.columns:
            nic_values = df_nic[selected_indicator].dropna().values
            nic_years = df_nic.dropna(subset=[selected_indicator])["Year"].values

            if len(nic_values) > 1:
                diffs = np.diff(nic_values)
                mean_diff = np.nanmean(diffs)
                std_diff = np.nanstd(diffs)

                if std_diff > 0:
                    outliers = np.where(
                        np.abs(diffs - mean_diff) > 2 * std_diff
                    )[0]
                    if len(outliers) > 0:
                        for idx in outliers:
                            st.markdown(
                                f'<div class="icon-text" style="color: #E53E3E;"><span class="material-icons" style="color: #E53E3E;">priority_high</span> <strong>{nic_years[idx+1]}</strong>: Variacion abrupta de <strong>{diffs[idx]:+.2f} pp</strong></div>',
                                unsafe_allow_html=True,
                            )
                    else:
                        st.markdown(
                            '<div class="icon-text" style="color: #38A169;"><span class="material-icons" style="color: #38A169;">check_circle</span> Crecimiento estable, sin anomalias estadisticamente significativas.</div>',
                            unsafe_allow_html=True,
                        )
                else:
                    st.info("Variacion constante o nula a lo largo de los años.")

    with col_bottom2:
        st.markdown(
            '<div class="icon-text"><span class="material-icons">scatter_plot</span> <strong>Correlacion: Electricidad vs Internet</strong></div>',
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
        "Desarrollado en Python | <b>Insight Five0Five</b> | Librerias: Streamlit, Pandas, NumPy, Seaborn | Datos: Banco Mundial (API / SQLite local) | 2026 | Lerickson Gonzalez - UNHSJM"
        "</div>",
        unsafe_allow_html=True,
    )
