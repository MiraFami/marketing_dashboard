"""
Page Segmentation : profils des 4 clusters K-means.
"""
import pandas as pd
from dash import html

from utils.data_loader import SEGMENT_COLORS, SEGMENT_ICONS, SEGMENT_DESC, SEGMENT_TOOLTIP
from utils.charts import (
    hex_to_rgba, fig_radar_segments, fig_prix_par_segment, fig_energie_stacked,
)
from components import icon, chart_card, section_hd, seg_metric, tbl, grid, col


_CARD_SHADOW = "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02)"

SEGMENT_ORDER = ["Hyperconnectés", "Primo-Numériques", "Seniors Premium", "Opportunistes Budget"]


def _segment_cards(df_seg: pd.DataFrame) -> list:
    """Cartes des 4 segments avec stats."""
    stats = df_seg.groupby("SEGMENT_NOM").agg(
        n=("LEAD_ID", "count"), age=("AGE", "mean"),
        prix=("PRIX_VENTE_TTC_COM", "mean"), km=("VEHICULE_KM", "mean"),
        fin=("A_FINANCEMENT", "mean"),
    )
    total = len(df_seg)
    cards = []

    for seg in SEGMENT_ORDER:
        if seg not in stats.index:
            continue
        s = stats.loc[seg]
        c = SEGMENT_COLORS.get(seg, "#94A3B8")
        n = int(s["n"])
        pct = n / total * 100
        ic = SEGMENT_ICONS.get(seg, "person")

        cards.append(col(
            html.Div([
                html.Div([
                    html.Div([
                        html.Div(icon(ic, "icon-nav"),
                                 className="w-7 h-7 rounded-lg flex items-center justify-center",
                                 style={"background": hex_to_rgba(c, 0.08), "color": c}),
                        html.Span(seg, className="text-sm font-semibold text-gray-800 ml-2",
                                 title=SEGMENT_TOOLTIP.get(seg, "")),
                    ], className="flex items-center"),
                    html.Div(f"{pct:.1f}%", className="text-[11px] font-semibold px-2 py-0.5 rounded-full",
                             style={"background": hex_to_rgba(c, 0.08), "color": c}),
                ], className="flex justify-between items-center mb-3"),
                html.Div([
                    html.Span(f"{n:,}", className="text-2xl font-bold tracking-tight text-gray-900"),
                    html.Span(" clients", className="text-sm text-gray-400 ml-1"),
                ], className="flex items-baseline mb-1"),
                html.Div(SEGMENT_DESC.get(seg, ""), className="text-xs text-gray-400 leading-relaxed mb-3"),
                html.Div([
                    seg_metric(f"{s['age']:.0f} ans",      "Âge moy."),
                    seg_metric(f"{s['prix']:,.0f} €",       "Prix moy."),
                    seg_metric(f"{s['km']:,.0f} km",        "Km moy."),
                    seg_metric(f"{s['fin']*100:.0f}%",      "Financement"),
                ], className="grid grid-cols-4 gap-2 pt-3 border-t border-gray-100"),
            ], className="bg-white rounded-2xl p-5 hover:shadow-md transition-all duration-200 h-full",
               style={"boxShadow": _CARD_SHADOW}),
            xs=12, md=6, lg=3,
        ))
    return cards


def _profile_table(df_seg: pd.DataFrame) -> pd.DataFrame:
    """Tableau profil moyen par segment, cohérent avec les cartes segments."""
    total = len(df_seg)
    p = df_seg.groupby("SEGMENT_NOM").agg(
        Clients=("LEAD_ID", "count"), Age_moy=("AGE", "mean"),
        Prix_moy=("PRIX_VENTE_TTC_COM", "mean"), Km_moy=("VEHICULE_KM", "mean"),
        Sessions=("NB_SESSIONS", "mean"), Financement=("A_FINANCEMENT", "mean"),
        Reprise=("A_REPRISE", "mean"),
    ).reindex(SEGMENT_ORDER).reset_index()
    p["% Total"] = (p["Clients"] / total * 100).round(1)
    p["Prix_moy"] = p["Prix_moy"].round(0).astype(int)
    p["Km_moy"] = p["Km_moy"].round(0).astype(int)
    p["Age_moy"] = p["Age_moy"].round(1)
    p["Sessions"] = p["Sessions"].round(0).astype(int)
    p["Financement"] = (p["Financement"] * 100).round(1)
    p["Reprise"]     = (p["Reprise"] * 100).round(1)
    p.rename(columns={
        "SEGMENT_NOM": "Segment", "Age_moy": "Âge moy.", "Prix_moy": "Prix moy. (€)",
        "Km_moy": "Km moy.", "Sessions": "Sessions web",
        "Financement": "% Financement", "Reprise": "% Reprise",
    }, inplace=True)
    p = p[["Segment", "Clients", "% Total", "Âge moy.", "Prix moy. (€)",
           "Km moy.", "Sessions web", "% Financement", "% Reprise"]]
    return p


def page_segmentation(df: pd.DataFrame, df_seg: pd.DataFrame) -> html.Div:
    seg_cards = _segment_cards(df_seg)
    profile_tbl = _profile_table(df_seg)
    data = df if len(df) > 10 else df_seg

    return html.Div([
        html.Div([
            html.Div("Comment lire ces segments ?", className="text-sm font-semibold text-gray-700 mb-2"),
            html.Div(
                "Les 4 profils suivants ont été identifiés par une analyse K-means sur les données d'achat, "
                "de navigation web, de financement et de localisation des clients aramisauto (Jan-Mai 2024). "
                "Chaque segment regroupe des clients aux comportements similaires. "
                "Survolez le nom d'un segment pour voir sa description.",
                className="text-sm text-gray-500 leading-relaxed",
            ),
        ], className="bg-blue-50 rounded-2xl p-5 mb-4",
           style={"boxShadow": _CARD_SHADOW}),

        section_hd("hub", "4 segments identifiés par K-means"),
        grid(*seg_cards),

        section_hd("radar", "Profil comparatif (radar & prix)"),
        grid(
            col(chart_card(fig_radar_segments(data), "440px"), xs=12, lg=7),
            col(chart_card(fig_prix_par_segment(data), "440px"), xs=12, lg=5),
        ),

        section_hd("table_chart", "Profil moyen par segment"),
        html.Div(tbl(profile_tbl),
                 className="bg-white rounded-2xl overflow-hidden mb-4",
                 style={"boxShadow": "0 1px 3px rgba(0,0,0,0.04)"}),

        section_hd("bolt", "Mix énergétique par segment"),
        chart_card(fig_energie_stacked(data), "380px"),
    ])
