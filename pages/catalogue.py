"""
Page Catalogue : marques, catégories, prix/km, boîte de vitesse, VO vs VN.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html

from utils.charts import fig_top_marques, fig_distance_livraison, TEMPLATE
from components import chart_card, section_hd, grid, col


def _fig_categories(df: pd.DataFrame) -> go.Figure:
    """Donut catégories de véhicules."""
    cat = df["VEHICULE_CATEGORIE"].value_counts().reset_index()
    cat.columns = ["Catégorie", "Nb"]
    fig = go.Figure(go.Pie(
        labels=cat["Catégorie"], values=cat["Nb"], hole=0.55,
        marker=dict(colors=px.colors.qualitative.Pastel, line=dict(color="white", width=2)),
        textinfo="percent+label", textfont=dict(size=11, family="Inter, sans-serif"),
        hovertemplate="<b>%{label}</b><br>%{value:,} ventes<extra></extra>",
    ))
    fig.update_layout(title="Catégories de véhicules", template=TEMPLATE,
                      height=380, showlegend=False, margin=dict(t=50, b=20, l=20, r=20))
    return fig


def _fig_boite_vitesse(df: pd.DataFrame) -> go.Figure:
    """Barres boîte de vitesse."""
    bv = df["VEHICULE_BOITE_VITESSE"].value_counts().reset_index()
    bv.columns = ["Boîte", "Nb"]
    fig = go.Figure(go.Bar(
        x=bv["Boîte"], y=bv["Nb"],
        marker_color=["#3B82F6", "#F59E0B", "#10B981"][:len(bv)],
        text=bv["Nb"].apply(lambda v: f"{v:,}"), textposition="outside",
        hovertemplate="<b>%{x}</b><br>%{y:,} ventes<extra></extra>",
    ))
    fig.update_layout(title="Type de boîte de vitesse", template=TEMPLATE,
                      height=320, showlegend=False, margin=dict(t=50, b=40, l=40, r=20))
    return fig


def _fig_vo_vn(df: pd.DataFrame) -> go.Figure:
    """Donut VO vs VN."""
    tv = df["VEHICULE_TYPE"].value_counts().reset_index()
    tv.columns = ["Type", "Nb"]
    tv["Type"] = tv["Type"].map({"VO": "Occasion (VO)", "VN": "Neuf (VN)"}).fillna(tv["Type"])
    fig = go.Figure(go.Pie(
        labels=tv["Type"], values=tv["Nb"], hole=0.55,
        marker=dict(colors=["#10B981", "#3B82F6"], line=dict(color="white", width=3)),
        textinfo="percent+label", textfont=dict(size=13, family="Inter, sans-serif"),
        hovertemplate="<b>%{label}</b><br>%{value:,} ventes (%{percent})<extra></extra>",
    ))
    fig.update_layout(title="Occasion vs Neuf", template=TEMPLATE,
                      height=320, showlegend=False, margin=dict(t=50, b=20, l=20, r=20))
    return fig


def page_catalogue(df: pd.DataFrame, filtre_seg: str, df_seg: pd.DataFrame) -> html.Div:
    seg = filtre_seg if filtre_seg != "Tous" else None

    return html.Div([
        section_hd("directions_car", "Analyse du catalogue vendu"),
        grid(
            col(chart_card(fig_top_marques(df, seg), "400px"), xs=12, lg=7),
            col(chart_card(_fig_categories(df), "400px"), xs=12, lg=5),
        ),
        
        section_hd("tune", "Caractéristiques techniques"),
        grid(
            col(chart_card(_fig_boite_vitesse(df), "320px"), xs=12, lg=6),
            col(chart_card(_fig_vo_vn(df), "320px"), xs=12, lg=6),
        ),
    ])
