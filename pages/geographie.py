"""
Page Géographie : régions, agences, distances, revenus.
"""
import pandas as pd
import plotly.graph_objects as go
from dash import html

from utils.charts import hex_to_rgba, fig_region_map_bar, fig_distance_livraison, TEMPLATE
from components import chart_card, section_hd, grid, col


def _fig_top_agences(df: pd.DataFrame) -> go.Figure:
    """Top 10 agences de livraison."""
    agences = df["AGENCE_LIVRAISON_COM"].value_counts().head(10).reset_index()
    agences.columns = ["Agence", "Clients"]
    agences = agences.sort_values("Clients")

    fig = go.Figure(go.Bar(
        x=agences["Clients"], y=agences["Agence"], orientation="h",
        marker=dict(
            color=agences["Clients"],
            colorscale=[[0, hex_to_rgba("#F59E0B", 0.25)], [1, "#F59E0B"]],
            showscale=False,
        ),
        text=agences["Clients"].apply(lambda v: f"{v:,}"), textposition="outside",
        hovertemplate="<b>%{y}</b><br>%{x:,} clients<extra></extra>",
    ))
    fig.update_layout(
        title="Top 10 agences de livraison", template=TEMPLATE, height=420,
        showlegend=False, xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.04)"),
        margin=dict(t=56, b=40, l=160, r=60),
    )
    return fig


def _fig_distance(df: pd.DataFrame) -> go.Figure:
    """Histogramme distance client-agence."""
    dist = df["AGENCE_DIST_KM"].dropna().clip(upper=250)
    fig = go.Figure(go.Histogram(
        x=dist, nbinsx=40,
        marker=dict(color="#7C3AED", opacity=0.75, line=dict(color="white", width=0.5)),
        hovertemplate="Distance %{x:.0f} km : %{y} clients<extra></extra>",
    ))
    fig.add_vline(x=dist.mean(), line_dash="dash", line_color="#EF4444",
                  annotation_text=f"Moy. {dist.mean():.0f} km", annotation_font_size=11)
    fig.update_layout(
        title="Distance à l'agence (km)", xaxis_title="km", yaxis_title="Nb clients",
        template=TEMPLATE, height=340, showlegend=False, margin=dict(t=56, b=40, l=48, r=20),
    )
    return fig


def _fig_duree(df: pd.DataFrame) -> go.Figure:
    """Histogramme temps de trajet."""
    dur = df["NEAREST_AGENCY_DUREE"].dropna().clip(upper=150)
    fig = go.Figure(go.Histogram(
        x=dur, nbinsx=40,
        marker=dict(color="#06B6D4", opacity=0.75, line=dict(color="white", width=0.5)),
        hovertemplate="Durée %{x:.0f} min : %{y} clients<extra></extra>",
    ))
    fig.add_vline(x=dur.mean(), line_dash="dash", line_color="#EF4444",
                  annotation_text=f"Moy. {dur.mean():.0f} min", annotation_font_size=11)
    fig.update_layout(
        title="Durée de trajet (min)", xaxis_title="min", yaxis_title="Nb clients",
        template=TEMPLATE, height=340, showlegend=False, margin=dict(t=56, b=40, l=48, r=20),
    )
    return fig


def _fig_revenus(df: pd.DataFrame) -> go.Figure:
    """Revenu médian par région (INSEE)."""
    rev = df.groupby("NOM_REGION")["REVENU_MEDIAN_UC_2021"].mean().sort_values().reset_index()
    rev.columns = ["Région", "Revenu médian (€)"]

    fig = go.Figure(go.Bar(
        x=rev["Revenu médian (€)"], y=rev["Région"], orientation="h",
        marker=dict(
            color=rev["Revenu médian (€)"],
            colorscale=[[0, hex_to_rgba("#3B82F6", 0.15)], [1, "#3B82F6"]],
            showscale=False,
        ),
        text=rev["Revenu médian (€)"].apply(lambda v: f"{v:,.0f} €"), textposition="outside",
        hovertemplate="<b>%{y}</b><br>%{x:,.0f} €<extra></extra>",
    ))
    fig.update_layout(
        title="Revenu médian par UC (INSEE Filosofi 2021)",
        xaxis_title="Revenu médian UC (€)", template=TEMPLATE, height=500,
        showlegend=False, xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.04)"),
        margin=dict(t=56, b=40, l=190, r=80),
    )
    return fig


def page_geographie(df: pd.DataFrame, filtre_seg: str) -> html.Div:
    seg = filtre_seg if filtre_seg != "Tous" else None

    return html.Div([
        section_hd("public", "Distribution géographique"),
        grid(
            col(chart_card(fig_region_map_bar(df, seg), "440px"), xs=12, lg=6),
            col(chart_card(_fig_top_agences(df), "440px"), xs=12, lg=6),
        ),
        section_hd("near_me", "Distance & durée vers les agences"),
        grid(
            col(chart_card(_fig_distance(df), "340px"), xs=12, lg=6),
            col(chart_card(_fig_duree(df), "340px"), xs=12, lg=6),
        ),
        section_hd("local_shipping", "Mode de livraison selon la distance"),
        chart_card(fig_distance_livraison(df), "400px"),
        section_hd("payments", "Revenus médians des zones clients"),
        chart_card(_fig_revenus(df), "500px"),
    ])
