"""
Fonctions de visualisation Plotly + template custom "aramisauto".
"""

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# --- Helpers ---
def hex_to_rgba(hex_color: str, alpha: float) -> str:
    """Hex vers rgba."""
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c*2 for c in h)
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return f"rgba({r},{g},{b},{alpha})"

# Couleurs par segment
SEGMENT_COLORS = {
    "Hyperconnectés":     "#EF4444",
    "Primo-Numériques":   "#3B82F6",
    "Seniors Premium":    "#10B981",
    "Opportunistes Budget": "#F59E0B",
}

# Template Plotly custom
_base_layout = go.Layout(
    font=dict(family="Inter, -apple-system, BlinkMacSystemFont, sans-serif", size=13, color="#374151"),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    colorway=["#003c57", "#6ad724", "#605de7", "#EF4444", "#F59E0B", "#06B6D4", "#EC4899"],
    title=dict(
        font=dict(size=14, color="#111827", weight="bold"),
        x=0.0,
        xanchor="left",
        pad=dict(l=0, t=4, b=12),
    ),
    xaxis=dict(
        showgrid=False,
        showline=False,
        zeroline=False,
        tickfont=dict(size=11, color="#9CA3AF"),
        title_font=dict(size=11, color="#9CA3AF"),
        ticks="",
    ),
    yaxis=dict(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(0,0,0,0.04)",
        showline=False,
        zeroline=False,
        tickfont=dict(size=11, color="#9CA3AF"),
        title_font=dict(size=11, color="#9CA3AF"),
        ticks="",
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0,
        font=dict(size=11, color="#6B7280"),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="left",
        x=0,
    ),
    margin=dict(t=52, b=36, l=44, r=20),
    hoverlabel=dict(
        bgcolor="white",
        bordercolor="rgba(0,0,0,0.08)",
        font=dict(size=12, family="Inter, sans-serif", color="#111827"),
        align="left",
    ),
    hovermode="x unified",
    modebar=dict(
        bgcolor="rgba(0,0,0,0)",
        color="#D1D5DB",
        activecolor="#6ad724",
        orientation="v",
    ),
)

pio.templates["aramisauto"] = go.layout.Template(layout=_base_layout)
pio.templates.default = "aramisauto"

TEMPLATE = "aramisauto"
FONT     = "Inter, -apple-system, sans-serif"

# Couleurs par type d'énergie
ENERGIE_COLORS = {
    "Diesel":               "#6B7280",
    "Essence":              "#3B82F6",
    "Hybride":              "#10B981",
    "Hybride Rechargeable": "#34D399",
    "Electrique":           "#F59E0B",
    "Électrique":           "#F59E0B",
    "Autre":                "#D1D5DB",
}

def fig_repartition_segments(df: pd.DataFrame) -> go.Figure:
    from utils.data_loader import SEGMENT_DESC
    counts = df["SEGMENT_NOM"].value_counts().reset_index()
    counts.columns = ["Segment", "Clients"]
    colors = [SEGMENT_COLORS.get(s, "#94A3B8") for s in counts["Segment"]]

    # Légende enrichie avec description courte
    legend_labels = []
    for s in counts["Segment"]:
        desc = SEGMENT_DESC.get(s, "")
        legend_labels.append(f"{s}<br><span style='font-size:10px;color:#9CA3AF'>{desc}</span>")

    fig = go.Figure(go.Pie(
        labels=legend_labels,
        values=counts["Clients"],
        hole=0.62,
        marker=dict(colors=colors, line=dict(color="white", width=3)),
        textinfo="percent",
        textfont=dict(size=13, family=FONT),
        hovertemplate="<b>%{label}</b><br>%{value:,} clients<br>%{percent}<extra></extra>",
        sort=False,
    ))

    total = counts["Clients"].sum()
    fig.add_annotation(
        text=f"<b>{total:,}</b><br><span style='font-size:11px;color:#94A3B8'>clients</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=20, family=FONT, color="#0F172A"),
        align="center",
    )

    fig.update_layout(
        title="Segments clients",
        template=TEMPLATE,
        showlegend=True,
        legend=dict(
            orientation="h", yanchor="top", y=-0.05,
            xanchor="left", x=0,
            font=dict(size=11, color="#6B7280"),
            borderwidth=0,
        ),
        margin=dict(t=50, b=120, l=10, r=10),
        height=420,
    )
    return fig


def fig_prix_par_segment(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    order = ["Opportunistes Budget", "Primo-Numériques", "Hyperconnectés", "Seniors Premium"]
    short = ["Budget", "Primo-Num.", "Hyperco.", "Seniors Prem."]
    for seg, label in zip(order, short):
        if seg not in df["SEGMENT_NOM"].values:
            continue
        data = df[df["SEGMENT_NOM"] == seg]["PRIX_VENTE_TTC_COM"].dropna()
        color = SEGMENT_COLORS.get(seg, "#94A3B8")
        med = data.median()
        moy = data.mean()
        fig.add_trace(go.Box(
            y=data, name=label,
            marker=dict(color=color, opacity=0.8, size=4),
            line=dict(color=color, width=2),
            fillcolor=hex_to_rgba(color, 0.13),
            boxmean="sd",
            hovertemplate=(
                f"<b>{seg}</b><br>"
                f"Prix : %{{y:,.0f}} €<br>"
                f"Médiane : {med:,.0f} € · Moyenne : {moy:,.0f} €"
                "<extra></extra>"
            ),
        ))
    fig.update_layout(
        title="Distribution des prix par segment",
        yaxis_title="Prix TTC (€)",
        template=TEMPLATE,
        showlegend=False,
        height=400,
        margin=dict(t=56, b=40, l=60, r=20),
    )
    return fig


def fig_age_distribution(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for seg, color in SEGMENT_COLORS.items():
        sub = df[df["SEGMENT_NOM"] == seg]["AGE"].dropna()
        if len(sub) == 0:
            continue
        fig.add_trace(go.Histogram(
            x=sub, name=seg, nbinsx=25,
            marker_color=color,
            opacity=0.75,
            hovertemplate=f"<b>{seg}</b><br>Âge : %{{x}}<br>Nb : %{{y}}<extra></extra>",
        ))
    fig.update_layout(
        title="Distribution des âges par segment",
        xaxis_title="Âge (années)",
        yaxis_title="Nombre de clients",
        barmode="overlay",
        template=TEMPLATE,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        height=360,
        margin=dict(t=56, b=40, l=56, r=20),
    )
    return fig


def fig_genre_donut(df: pd.DataFrame) -> go.Figure:
    """Donut homme/femme."""
    genre = df["IS_MALE"].value_counts().reset_index()
    genre.columns = ["IS_MALE", "Nb"]
    genre["Genre"] = genre["IS_MALE"].map({1: "Homme", 0: "Femme"})
    fig = go.Figure(go.Pie(
        labels=genre["Genre"], values=genre["Nb"], hole=0.6,
        marker=dict(colors=["#3B82F6", "#EC4899"], line=dict(color="white", width=3)),
        textinfo="percent+label", textfont=dict(size=12, family=FONT),
        hovertemplate="<b>%{label}</b><br>%{value:,} clients (%{percent})<extra></extra>",
    ))
    total = genre["Nb"].sum()
    fig.add_annotation(
        text=f"<b>{total:,}</b><br><span style='font-size:10px;color:#94A3B8'>clients</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, family=FONT, color="#0F172A"), align="center",
    )
    fig.update_layout(
        title="Répartition par genre",
        template=TEMPLATE, showlegend=False, height=300,
        margin=dict(t=50, b=20, l=20, r=20),
    )
    return fig


def fig_sessions_vs_prix(df: pd.DataFrame) -> go.Figure:
    """Bar chart sessions web vs prix moyen par segment."""
    stats = df.groupby("SEGMENT_NOM").agg(
        sessions=("NB_SESSIONS", "mean"),
        prix=("PRIX_VENTE_TTC_COM", "mean"),
    ).reindex(["Opportunistes Budget", "Primo-Numériques", "Hyperconnectés", "Seniors Premium"])

    short = ["Budget", "Primo-Num.", "Hyperco.", "Seniors Prem."]
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=short, y=stats["sessions"],
        name="Sessions web (moy.)",
        marker_color="#EF4444", opacity=0.8,
        text=[f"{v:.0f}" for v in stats["sessions"]], textposition="outside",
        textfont=dict(size=11),
        hovertemplate="<b>%{x}</b><br>Sessions : %{y:.0f}<extra></extra>",
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=short, y=stats["prix"],
        name="Prix moyen (€)",
        mode="lines+markers",
        line=dict(color="#10B981", width=2.5),
        marker=dict(size=8, color="white", line=dict(color="#10B981", width=2)),
        hovertemplate="<b>%{x}</b><br>Prix : %{y:,.0f} €<extra></extra>",
    ), secondary_y=True)

    fig.update_yaxes(title_text="Sessions web (moy.)", secondary_y=False,
                     showgrid=True, gridcolor="rgba(0,0,0,0.04)", zeroline=False)
    fig.update_yaxes(title_text="Prix moyen (€)", secondary_y=True,
                     showgrid=False, zeroline=False)
    fig.update_layout(
        title="Sessions web vs prix moyen par segment",
        template=TEMPLATE, height=380,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, borderwidth=0),
        margin=dict(t=60, b=40, l=56, r=56),
    )
    return fig


def fig_financement_segment(df: pd.DataFrame) -> go.Figure:
    """Bar chart taux de financement par segment."""
    order = ["Opportunistes Budget", "Primo-Numériques", "Hyperconnectés", "Seniors Premium"]
    stats = df.groupby("SEGMENT_NOM")["A_FINANCEMENT"].mean().reindex(order).mul(100)
    short = ["Budget", "Primo-Num.", "Hyperco.", "Seniors Prem."]
    colors = [SEGMENT_COLORS.get(s, "#94A3B8") for s in order]

    fig = go.Figure(go.Bar(
        x=short, y=stats.values,
        marker_color=colors,
        text=[f"{v:.0f}%" for v in stats.values], textposition="outside",
        textfont=dict(size=12),
        hovertemplate="<b>%{x}</b><br>Taux de financement : %{y:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        title="Taux de financement par segment",
        yaxis_title="Taux de financement (%)",
        template=TEMPLATE, showlegend=False, height=360,
        margin=dict(t=56, b=40, l=56, r=20),
        yaxis=dict(range=[0, max(stats.values) * 1.2]),
    )
    return fig


def fig_energie_stacked(df: pd.DataFrame) -> go.Figure:
    cross = df.groupby(["SEGMENT_NOM", "VEHICULE_ENERGIE"]).size().reset_index(name="n")
    total = cross.groupby("SEGMENT_NOM")["n"].transform("sum")
    cross["pct"] = (cross["n"] / total * 100).round(1)

    energies = cross["VEHICULE_ENERGIE"].unique()
    fig = go.Figure()
    for e in sorted(energies):
        sub = cross[cross["VEHICULE_ENERGIE"] == e]
        fig.add_trace(go.Bar(
            name=e,
            x=sub["SEGMENT_NOM"],
            y=sub["pct"],
            marker_color=ENERGIE_COLORS.get(e, "#CBD5E1"),
            text=sub["pct"].apply(lambda v: f"{v:.0f}%" if v >= 5 else ""),
            textposition="inside",
            textfont=dict(size=11, color="white"),
            hovertemplate=f"<b>{e}</b><br>%{{x}}<br>%{{y:.1f}}%<extra></extra>",
        ))
    fig.update_layout(
        title="Mix énergétique par segment (%)",
        yaxis_title="Part (%)",
        barmode="stack",
        template=TEMPLATE,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        height=380,
        margin=dict(t=60, b=40, l=48, r=20),
    )
    return fig


def fig_benchmark_energie(df_sdes: pd.DataFrame, df: pd.DataFrame) -> go.Figure:
    sdes_24 = df_sdes[df_sdes["ANNEE"] == 2024].copy()
    mapping = {
        "Essence": "Essence", "Diesel": "Diesel",
        "Hybride (HEV/MHEV)": "Hybride", "Hybride Rechargeable": "Hybride",
        "Électrique": "Électrique",
    }
    sdes_24["ENERGIE_GRP"] = sdes_24["ENERGIE"].map(mapping)
    sdes_grp = sdes_24.groupby("ENERGIE_GRP")["PART_MARCHE_PCT"].sum().reset_index()

    aa = df["VEHICULE_ENERGIE"].value_counts(normalize=True).mul(100).reset_index()
    aa.columns = ["ENERGIE_GRP", "PART_MARCHE_PCT"]
    # Normaliser "Electrique" en "Électrique"
    aa["ENERGIE_GRP"] = aa["ENERGIE_GRP"].replace({"Electrique": "Électrique"})

    order = ["Diesel", "Essence", "Hybride", "Électrique"]
    fig = go.Figure()

    sdes_dict = dict(zip(sdes_grp["ENERGIE_GRP"], sdes_grp["PART_MARCHE_PCT"]))
    aa_dict   = dict(zip(aa["ENERGIE_GRP"], aa["PART_MARCHE_PCT"]))

    sdes_vals = [sdes_dict.get(e, 0) for e in order]
    aa_vals   = [aa_dict.get(e, 0) for e in order]

    fig.add_trace(go.Bar(
        name="Marché national (SDES 2024)", x=order, y=sdes_vals,
        marker_color="#3B82F6", opacity=0.85,
        text=[f"{v:.1f}%" for v in sdes_vals], textposition="outside",
        textfont=dict(size=11),
    ))
    fig.add_trace(go.Bar(
        name="aramisauto (Jan–Mai 2024)", x=order, y=aa_vals,
        marker_color="#F59E0B", opacity=0.85,
        text=[f"{v:.1f}%" for v in aa_vals], textposition="outside",
        textfont=dict(size=11),
    ))
    fig.update_layout(
        title="Benchmark énergie : aramisauto vs Marché national 2024",
        yaxis_title="Part de marché (%)",
        barmode="group",
        template=TEMPLATE,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        height=400,
        margin=dict(t=60, b=40, l=56, r=20),
    )
    return fig


def fig_monthly_volume(df: pd.DataFrame) -> go.Figure:
    monthly = df.groupby("MOIS_PANIER").agg(
        NB_COMMANDES=("LEAD_ID", "count"),
        CA_MOYEN=("PRIX_VENTE_TTC_COM", "mean"),
    ).reset_index().sort_values("MOIS_PANIER")

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    fig.add_trace(go.Bar(
        x=monthly["MOIS_PANIER"], y=monthly["NB_COMMANDES"],
        name="Nb commandes",
        marker=dict(color="#3B82F6", opacity=0.7),
        hovertemplate="<b>%{x}</b><br>Commandes : %{y}<extra></extra>",
    ), secondary_y=False)

    fig.add_trace(go.Scatter(
        x=monthly["MOIS_PANIER"], y=monthly["CA_MOYEN"],
        name="Panier moyen (€)",
        line=dict(color="#EF4444", width=2.5),
        mode="lines+markers",
        marker=dict(size=6, color="white", line=dict(color="#EF4444", width=2)),
        hovertemplate="<b>%{x}</b><br>Panier : %{y:,.0f} €<extra></extra>",
    ), secondary_y=True)

    fig.update_xaxes(title_text="Mois", showgrid=False)
    fig.update_yaxes(title_text="Nombre de commandes", secondary_y=False,
                     showgrid=True, gridcolor="rgba(0,0,0,0.04)", zeroline=False)
    fig.update_yaxes(title_text="Panier moyen (€)", secondary_y=True,
                     showgrid=False, zeroline=False)
    fig.update_layout(
        title="Évolution mensuelle, commandes & panier moyen",
        template=TEMPLATE,
        height=360,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, borderwidth=0),
        margin=dict(t=60, b=40, l=56, r=56),
    )
    return fig


def fig_radar_segments(df: pd.DataFrame) -> go.Figure:
    features = {
        "Âge": "AGE",
        "Prix véhicule": "PRIX_VENTE_TTC_COM",
        "Kilométrage": "VEHICULE_KM",
        "Sessions web": "NB_SESSIONS",
        "Revenu médian": "REVENU_MEDIAN_UC_2021",
        "Distance agence": "AGENCE_DIST_KM",
    }
    profile = df.groupby("SEGMENT_NOM")[list(features.values())].mean()
    mn, mx = profile.min(), profile.max()
    profile_norm = (profile - mn) / (mx - mn + 1e-9)
    categories = list(features.keys())

    fig = go.Figure()
    for seg in profile_norm.index:
        values = profile_norm.loc[seg].tolist() + [profile_norm.loc[seg].tolist()[0]]
        color = SEGMENT_COLORS.get(seg, "#94A3B8")
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill="toself",
            name=seg,
            line=dict(color=color, width=2.5),
            fillcolor=hex_to_rgba(color, 0.10),
            hovertemplate=f"<b>{seg}</b><br>%{{theta}} : %{{r:.2f}}<extra></extra>",
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, range=[0, 1],
                tickfont=dict(size=10, color="#D1D5DB"),
                gridcolor="rgba(0,0,0,0.05)",
                linecolor="rgba(0,0,0,0.05)",
            ),
            angularaxis=dict(
                tickfont=dict(size=11, color="#6B7280"),
                linecolor="rgba(0,0,0,0.05)",
                gridcolor="rgba(0,0,0,0.05)",
            ),
            bgcolor="rgba(0,0,0,0)",
        ),
        title="Profil comparatif des 4 segments (normalisé)",
        template=TEMPLATE,
        height=460,
        legend=dict(
            orientation="h", yanchor="top", y=-0.08,
            xanchor="center", x=0.5,
            font=dict(size=11),
            borderwidth=0,
        ),
        margin=dict(t=60, b=60, l=40, r=40),
    )
    return fig


def fig_top_marques(df: pd.DataFrame, segment: str = None) -> go.Figure:
    data = df if segment is None else df[df["SEGMENT_NOM"] == segment]
    top = data["VEHICULE_MARQUE"].value_counts().head(12).reset_index()
    top.columns = ["Marque", "Nb"]
    top = top.sort_values("Nb")

    color = SEGMENT_COLORS.get(segment, "#3B82F6") if segment else "#3B82F6"

    n = len(top)
    alpha_range = [round(0.35 + 0.65 * i / max(n - 1, 1), 2) for i in range(n)]
    colors_list = [hex_to_rgba(color, a) for a in alpha_range]

    fig = go.Figure(go.Bar(
        x=top["Nb"], y=top["Marque"],
        orientation="h",
        marker=dict(color=colors_list),
        text=top["Nb"].apply(lambda v: f"{v:,}"),
        textposition="outside",
        textfont=dict(size=11, color="#475569"),
        hovertemplate="<b>%{y}</b><br>%{x:,} ventes<extra></extra>",
    ))
    fig.update_layout(
        title=f"Top marques ({segment or 'Tous segments'})",
        xaxis_title="Nombre de ventes",
        template=TEMPLATE,
        height=420,
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.04)"),
        yaxis=dict(showgrid=False),
        margin=dict(t=56, b=40, l=120, r=60),
    )
    return fig


def fig_region_map_bar(df: pd.DataFrame, segment: str = None) -> go.Figure:
    data = df if segment is None else df[df["SEGMENT_NOM"] == segment]
    regions = data["NOM_REGION"].value_counts().head(13).reset_index()
    regions.columns = ["Région", "Clients"]
    regions = regions.sort_values("Clients")

    color = SEGMENT_COLORS.get(segment, "#3B82F6") if segment else "#3B82F6"

    fig = go.Figure(go.Bar(
        x=regions["Clients"], y=regions["Région"],
        orientation="h",
        marker=dict(
            color=regions["Clients"],
            colorscale=[[0, hex_to_rgba(color, 0.25)], [1, color]],
            showscale=False,
        ),
        text=regions["Clients"].apply(lambda v: f"{v:,}"),
        textposition="outside",
        textfont=dict(size=11, color="#475569"),
        hovertemplate="<b>%{y}</b><br>%{x:,} clients<extra></extra>",
    ))
    fig.update_layout(
        title=f"Clients par région ({segment or 'Tous segments'})",
        xaxis_title="Nombre de clients",
        template=TEMPLATE,
        height=440,
        showlegend=False,
        xaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.04)"),
        yaxis=dict(showgrid=False),
        margin=dict(t=56, b=40, l=160, r=60),
    )
    return fig


def fig_sdes_evolution(df_sdes: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for energie in df_sdes["ENERGIE"].unique():
        sub = df_sdes[df_sdes["ENERGIE"] == energie].sort_values("ANNEE")
        color = ENERGIE_COLORS.get(energie, "#94A3B8")
        fig.add_trace(go.Scatter(
            x=sub["ANNEE"], y=sub["PART_MARCHE_PCT"],
            name=energie,
            mode="lines+markers",
            line=dict(color=color, width=2.5),
            marker=dict(size=8, color="white", line=dict(color=color, width=2)),
            hovertemplate=f"<b>{energie}</b><br>Année : %{{x}}<br>Part : %{{y:.1f}}%<extra></extra>",
        ))
    fig.update_layout(
        title="Évolution des parts de marché par énergie, France (SDES 2021-2024)",
        xaxis_title="Année",
        yaxis_title="Part de marché (%)",
        template=TEMPLATE,
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(t=60, b=40, l=56, r=20),
    )
    return fig


def fig_scatter_prix_km(df: pd.DataFrame) -> go.Figure:
    df_plot = df[df["VEHICULE_KM"] < 150000].copy()
    fig = go.Figure()
    for seg, color in SEGMENT_COLORS.items():
        sub = df_plot[df_plot["SEGMENT_NOM"] == seg]
        if len(sub) == 0:
            continue
        fig.add_trace(go.Scatter(
            x=sub["VEHICULE_KM"], y=sub["PRIX_VENTE_TTC_COM"],
            name=seg, mode="markers",
            marker=dict(color=color, size=5, opacity=0.45,
                        line=dict(color=color, width=0.5)),
            hovertemplate=(
                f"<b>{seg}</b><br>"
                "Km : %{x:,.0f}<br>Prix : %{y:,.0f} €<extra></extra>"
            ),
        ))
    fig.update_layout(
        title="Prix TTC vs Kilométrage par segment",
        xaxis_title="Kilométrage (km)",
        yaxis_title="Prix TTC (€)",
        template=TEMPLATE,
        height=440,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(t=60, b=40, l=64, r=20),
    )
    return fig


def fig_distance_livraison(df: pd.DataFrame) -> go.Figure:
    """Bar chart : % livraison à domicile vs en agence par tranche de distance."""
    dfl = df[["TYPE_LIVRAISON_COM", "AGENCE_DIST_KM"]].dropna().copy()

    bins = [0, 20, 50, 100, float("inf")]
    labels = ["0 – 20 km", "20 – 50 km", "50 – 100 km", "+ de 100 km"]
    dfl["tranche"] = pd.cut(dfl["AGENCE_DIST_KM"], bins=bins, labels=labels, right=False)

    cross = dfl.groupby(["tranche", "TYPE_LIVRAISON_COM"], observed=False).size().reset_index(name="n")
    totals = cross.groupby("tranche", observed=False)["n"].transform("sum")
    cross["pct"] = (cross["n"] / totals * 100).round(1)

    mode_map = {"En Agence": "Retrait en agence", "A Domicile": "Livraison à domicile"}
    colors = {"En Agence": "#3B82F6", "A Domicile": "#F59E0B"}

    fig = go.Figure()
    for mode in ["En Agence", "A Domicile"]:
        sub = cross[cross["TYPE_LIVRAISON_COM"] == mode]
        fig.add_trace(go.Bar(
            x=[str(t) for t in sub["tranche"]],
            y=sub["pct"],
            name=mode_map[mode],
            marker_color=colors[mode],
            text=sub["pct"].apply(lambda v: f"{v:.0f}%"),
            textposition="outside",
            textfont=dict(size=12),
            hovertemplate=f"<b>{mode_map[mode]}</b><br>%{{x}}<br>%{{y:.1f}}% (%{{customdata:,}} clients)<extra></extra>",
            customdata=sub["n"],
        ))

    fig.update_layout(
        title="Mode de livraison selon la distance à l'agence",
        xaxis_title="Distance à l'agence",
        yaxis_title="Part des clients (%)",
        barmode="group",
        template=TEMPLATE,
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        margin=dict(t=60, b=40, l=48, r=20),
        yaxis=dict(range=[0, 105]),
    )
    return fig


def fig_matrice_impact(df_seg: pd.DataFrame) -> go.Figure:
    matrix_data = pd.DataFrame({
        "Action": [
            "Programme fidélité Senior",
            "Alertes prix Budget",
            "Remarketing Hyperconnectés",
            "Simulateur financement",
            "Contenu rich media",
            "Livraison premium",
        ],
        "Priorité": [9, 7, 8, 8, 6, 7],
        "Impact CA": [9, 5, 7, 8, 6, 8],
        "Segment": [
            "Seniors Premium", "Opportunistes Budget",
            "Hyperconnectés", "Primo-Numériques",
            "Hyperconnectés", "Seniors Premium",
        ],
    })
    fig = go.Figure()
    for seg, color in SEGMENT_COLORS.items():
        sub = matrix_data[matrix_data["Segment"] == seg]
        if len(sub) == 0:
            continue
        fig.add_trace(go.Scatter(
            x=sub["Priorité"], y=sub["Impact CA"],
            name=seg, mode="markers+text",
            marker=dict(size=18, color=color, opacity=0.85,
                        line=dict(color="white", width=2)),
            text=sub["Action"],
            textposition="top center",
            textfont=dict(size=10, color="#475569"),
            hovertemplate="<b>%{text}</b><br>Priorité : %{x}/10<br>Impact CA : %{y}/10<extra></extra>",
        ))
    fig.add_hline(y=7, line_dash="dot", line_color="#CBD5E1", opacity=0.8)
    fig.add_vline(x=7, line_dash="dot", line_color="#CBD5E1", opacity=0.8)
    fig.add_annotation(x=9.5, y=9.5, text="<b>Priorité haute</b>",
                       showarrow=False, font=dict(size=10, color="#94A3B8"))
    fig.add_annotation(x=5, y=4.5, text="<b>À planifier</b>",
                       showarrow=False, font=dict(size=10, color="#CBD5E1"))
    fig.update_layout(
        title="Matrice Priorité × Impact des actions recommandées",
        xaxis=dict(title="Priorité de mise en œuvre (1-10)", range=[4.5, 10.5], showgrid=True, gridcolor="rgba(0,0,0,0.04)"),
        yaxis=dict(title="Impact CA estimé (1-10)", range=[3.5, 10.5], showgrid=True, gridcolor="rgba(0,0,0,0.04)"),
        template=TEMPLATE,
        height=460,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0, borderwidth=0),
        margin=dict(t=60, b=40, l=56, r=20),
    )
    return fig
