"""
Page Vue d'ensemble : KPIs, segments, volume mensuel, ages.
"""
import pandas as pd
from dash import html

from utils.data_loader import get_kpis
from utils.charts import fig_repartition_segments, fig_monthly_volume, fig_age_distribution
from components import kpi_card, chart_card, grid, col


def page_overview(df: pd.DataFrame) -> html.Div:
    k = get_kpis(df)

    row1 = grid(
        col(kpi_card("group",       f"{k['nb_clients']:,}",         "Clients acheteurs", "#3B82F6"), xs=12, md=6, lg=4, xl=2),
        col(kpi_card("payments",    f"{k['ca_total']/1e6:.1f} M€",  "CA total estimé",   "#10B981"), xs=12, md=6, lg=4, xl=2),
        col(kpi_card("euro",        f"{k['panier_moyen']:,.0f} €",   "Panier moyen",      "#7C3AED"), xs=12, md=6, lg=4, xl=2),
        col(kpi_card("cake",        f"{k['age_moyen']:.1f} ans",     "Âge moyen",         "#F59E0B"), xs=12, md=6, lg=4, xl=2),
        col(kpi_card("credit_card", f"{k['taux_financement']:.1f}%", "Taux financement",  "#EF4444"), xs=12, md=6, lg=4, xl=2),
        col(kpi_card("autorenew",   f"{k['taux_reprise']:.1f}%",     "Taux reprise",      "#06B6D4"), xs=12, md=6, lg=4, xl=2),
    )

    row2 = grid(
        col(kpi_card("star",       k['marque_top'],                                "Marque N°1",          "#F59E0B"), xs=12, md=6, lg=4, xl=2),
        col(kpi_card("man",        f"{k['pct_hommes']:.1f}%",                      "Part hommes",         "#3B82F6"), xs=12, md=6, lg=4, xl=2),
        col(kpi_card("location_on",str(k['nb_regions']),                           "Régions couvertes",   "#10B981"), xs=12, md=6, lg=4, xl=2),
        col(kpi_card("store",      str(k['nb_agences']),                           "Agences livraison",   "#7C3AED"), xs=12, md=6, lg=4, xl=2),
        col(kpi_card("swap_horiz", f"{int(df['VEHICULE_KM'].median()):,} km",     "Km médian véhicule",  "#F59E0B"), xs=12, md=6, lg=4, xl=2),
        col(kpi_card("bar_chart",  str(df['VEHICULE_MARQUE'].nunique()),           "Marques distinctes",  "#EF4444"), xs=12, md=6, lg=4, xl=2),
    )

    charts = grid(
        col(chart_card(fig_repartition_segments(df), "340px"), xs=12, lg=5),
        col(chart_card(fig_monthly_volume(df),        "340px"), xs=12, lg=7),
    )
    age = grid(col(chart_card(fig_age_distribution(df), "340px"), xs=12))

    return html.Div([row1, row2, charts, age])
