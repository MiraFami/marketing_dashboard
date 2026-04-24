"""
Page Benchmark : comparaison aramisauto vs SDES 2021-2024.
"""
import pandas as pd
from dash import html

from utils.charts import fig_sdes_evolution, fig_benchmark_energie
from components import chart_card, section_hd, info_banner, tbl


def _build_sdes_table(df_sdes: pd.DataFrame) -> pd.DataFrame:
    """Pivot SDES pour affichage."""
    pivot = df_sdes.pivot_table(
        values="PART_MARCHE_PCT", index="ENERGIE", columns="ANNEE", aggfunc="sum"
    ).round(1)
    pivot.index.name = None
    pivot.columns = [str(int(c)) for c in pivot.columns]
    pivot = pivot.reset_index()
    first_col = pivot.columns[0]
    pivot = pivot.rename(columns={first_col: "Énergie"})
    pivot.columns = ["Énergie"] + [f"Part mkt {c} (%)" for c in pivot.columns[1:]]
    return pivot


def page_benchmark(df: pd.DataFrame, df_sdes: pd.DataFrame, df_seg: pd.DataFrame) -> html.Div:
    pivot = _build_sdes_table(df_sdes)
    bench_data = df if len(df) > 50 else df_seg

    return html.Div([
        info_banner(
            "Source : SDES - Ministère de la Transition Écologique · "
            "statistiques.developpement-durable.gouv.fr"
        ),
        section_hd("trending_up", "Évolution du marché national par énergie"),
        chart_card(fig_sdes_evolution(df_sdes), "400px"),

        section_hd("compare_arrows", "Benchmark aramisauto vs Marché national 2024"),
        chart_card(fig_benchmark_energie(df_sdes, bench_data), "400px"),

        section_hd("table_chart", "Données SDES, parts de marché (%)"),
        html.Div(tbl(pivot),
                 className="bg-white rounded-2xl overflow-hidden",
                 style={"boxShadow": "0 1px 3px rgba(0,0,0,0.04)"}),
    ])
