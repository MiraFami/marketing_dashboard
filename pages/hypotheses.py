"""
Page Hypothèses : 5 hypothèses testées sur les données.
"""
import pandas as pd
from dash import dcc, html

from utils.data_loader import get_kpis, load_sdes_data
from utils.charts import (
    fig_age_distribution, fig_genre_donut,
    fig_benchmark_energie, fig_sessions_vs_prix,
    fig_financement_segment, fig_distance_livraison,
)
from components import icon, info_banner, section_hd, chart_card, grid, col


STATUS_MAP = {
    "validated":   ("check_circle", "Validée",   "bg-emerald-50 text-emerald-600"),
    "invalidated": ("cancel",       "Invalidée", "bg-red-50 text-red-500"),
    "partial":     ("warning",      "Partielle", "bg-amber-50 text-amber-600"),
}

_CARD_SHADOW = "0 1px 3px rgba(0,0,0,0.04)"


def _build_hypotheses(df: pd.DataFrame) -> list[dict]:
    """Liste des hypothèses avec valeurs calculées depuis le df."""
    kpis = get_kpis(df)

    # H2 - calcul électrique réel
    energie = df["VEHICULE_ENERGIE"].value_counts(normalize=True).mul(100)
    pct_elec = energie.get("Electrique", energie.get("Électrique", 0))

    # H5 - stats distance par livraison
    dist_agence = df[df["TYPE_LIVRAISON_COM"] == "En Agence"]["AGENCE_DIST_KM"].dropna()
    dist_domicile = df[df["TYPE_LIVRAISON_COM"] == "A Domicile"]["AGENCE_DIST_KM"].dropna()
    med_agence = dist_agence.median() if len(dist_agence) > 0 else 0
    med_domicile = dist_domicile.median() if len(dist_domicile) > 0 else 0
    pct_domicile = (len(dist_domicile) / (len(dist_agence) + len(dist_domicile)) * 100
                    if (len(dist_agence) + len(dist_domicile)) > 0 else 0)

    # Graphiques H2
    df_sdes = load_sdes_data()

    return [
        {
            "id": "H1", "color": "#10B981", "status": "validated",
            "titre": "La clientèle est majoritairement masculine et âgée de 45 à 60 ans",
            "evidence": (
                f"Les données confirment <strong>{kpis['pct_hommes']:.0f}%</strong> d'hommes. "
                f"Âge moyen <strong>{kpis['age_moyen']:.1f} ans</strong>. "
                "Le segment Seniors Premium (45% des clients) présente un âge moyen de 57 ans."
            ),
            "charts": [
                ("Répartition par genre", fig_genre_donut(df), "360px"),
                ("Distribution des âges par segment", fig_age_distribution(df), "360px"),
            ],
        },
        {
            "id": "H2", "color": "#10B981", "status": "validated",
            "titre": "L'électrique est sous-représenté chez aramisauto vs le marché national",
            "evidence": (
                f"Seulement <strong>{pct_elec:.1f}%</strong> des véhicules vendus par aramisauto "
                "sont électriques, contre <strong>~17%</strong> des immatriculations nationales VN (SDES 2024). "
                "Ce constat n'est <strong>pas lié à une zone géographique</strong> particulière : "
                "l'électrique reste sous les 9% dans toutes les régions (de 0% en Outre-mer à 8% en Centre-Val de Loire). "
                "Le décalage est structurel et s'explique par le positionnement d'aramisauto sur le marché des véhicules d'occasion, "
                "où l'offre électrique d'occasion reste limitée."
            ),
            "charts": [
                ("Benchmark énergie : aramisauto vs marché national", fig_benchmark_energie(df_sdes, df), "400px"),
            ],
        },
        {
            "id": "H3", "color": "#EF4444", "status": "invalidated",
            "titre": "L'intensité de navigation web est corrélée positivement au panier moyen",
            "evidence": (
                "Cette hypothèse suppose que plus un client navigue intensément sur le site, plus son "
                "panier moyen est élevé. <strong>Les données l'infirment :</strong> "
                "les <strong>Hyperconnectés</strong> cumulent en moyenne <strong>736 sessions</strong> "
                "mais un panier de <strong>~24 000 euros</strong>, tandis que les <strong>Seniors Premium</strong> "
                "avec seulement <strong>~123 sessions</strong> ont le panier le plus élevé : "
                "<strong>~26 000 euros</strong>. "
                "Une navigation intense traduit davantage une <strong>hésitation ou un besoin de réassurance</strong> "
                "qu'un pouvoir d'achat supérieur. Le panier est déterminé par le profil socio-économique "
                "du client, pas par son activité en ligne."
            ),
            "charts": [
                ("Sessions web vs prix moyen par segment", fig_sessions_vs_prix(df), "380px"),
            ],
        },
        {
            "id": "H4", "color": "#F59E0B", "status": "partial",
            "titre": "Le financement est principalement adopté par les segments jeunes / petits budgets",
            "evidence": (
                "Partiellement confirmée : les <strong>Primo-Numériques</strong> ont le taux de "
                "financement le plus élevé (~50%). Mais les Opportunistes Budget (les plus jeunes) "
                "utilisent moins le financement que prévu - c'est un outil de confort, pas de nécessité."
            ),
            "charts": [
                ("Taux de financement par segment", fig_financement_segment(df), "360px"),
            ],
        },
        {
            "id": "H5", "color": "#F59E0B", "status": "partial",
            "titre": "Les clients éloignés d'une agence optent davantage pour la livraison à domicile",
            "evidence": (
                f"La distance médiane est de <strong>{med_domicile:.0f} km</strong> pour la livraison à domicile "
                f"contre <strong>{med_agence:.0f} km</strong> pour le retrait en agence. "
                f"La livraison à domicile représente <strong>{pct_domicile:.0f}%</strong> des commandes. "
                "Il existe bien une corrélation entre distance et choix de livraison, mais le segment "
                "et le prix du véhicule restent des facteurs plus déterminants que la seule distance géographique."
            ),
            "charts": [
                ("Mode de livraison selon la distance", fig_distance_livraison(df), "400px"),
            ],
        },
    ]


def page_hypotheses(df: pd.DataFrame) -> html.Div:
    hypotheses = _build_hypotheses(df)

    n_val  = sum(1 for h in hypotheses if h["status"] == "validated")
    n_inv  = sum(1 for h in hypotheses if h["status"] == "invalidated")
    n_part = sum(1 for h in hypotheses if h["status"] == "partial")

    summary = grid(
        col(html.Div([
            html.Div(str(n_val), className="text-3xl font-bold text-emerald-500 leading-none"),
            html.Div("Validées", className="text-[10px] font-medium text-gray-400 uppercase tracking-wider mt-1.5"),
        ], className="bg-white rounded-2xl p-6 text-center",
           style={"boxShadow": _CARD_SHADOW}), xs=12, md=4),
        col(html.Div([
            html.Div(str(n_inv), className="text-3xl font-bold text-red-400 leading-none"),
            html.Div("Invalidées", className="text-[10px] font-medium text-gray-400 uppercase tracking-wider mt-1.5"),
        ], className="bg-white rounded-2xl p-6 text-center",
           style={"boxShadow": _CARD_SHADOW}), xs=12, md=4),
        col(html.Div([
            html.Div(str(n_part), className="text-3xl font-bold text-amber-400 leading-none"),
            html.Div("Partielles", className="text-[10px] font-medium text-gray-400 uppercase tracking-wider mt-1.5"),
        ], className="bg-white rounded-2xl p-6 text-center",
           style={"boxShadow": _CARD_SHADOW}), xs=12, md=4),
    )

    cards = []
    for i, h in enumerate(hypotheses):
        ic_n, badge_lbl, badge_cls = STATUS_MAP[h["status"]]

        # Header (toujours visible)
        header = html.Summary([
            html.Div([
                html.Div(h["id"], className="text-[11px] font-semibold text-gray-400 px-2 py-0.5 rounded-md bg-gray-100 flex-shrink-0"),
                html.Div(h["titre"], className="text-sm font-medium text-gray-800 flex-1"),
                html.Div([
                    icon(ic_n, "icon-xs"),
                    html.Span(badge_lbl, className="text-[11px] font-semibold"),
                ], className=f"flex items-center gap-1 px-2.5 py-1 rounded-full flex-shrink-0 {badge_cls}"),
            ], className="flex items-start gap-3"),
        ], className="cursor-pointer list-none",
           style={"outline": "none"})

        # Contenu (graphiques + evidence)
        chart_items = []
        charts = h.get("charts", [])
        if len(charts) == 1:
            _, fig, height = charts[0]
            chart_items.append(html.Div(chart_card(fig, height), className="mt-4"))
        elif len(charts) == 2:
            chart_items.append(html.Div(
                grid(
                    col(chart_card(charts[0][1], charts[0][2]), xs=12, lg=4),
                    col(chart_card(charts[1][1], charts[1][2]), xs=12, lg=8),
                ), className="mt-4",
            ))

        evidence_block = html.Div(
            dcc.Markdown(h["evidence"], dangerously_allow_html=True,
                         className="text-sm text-gray-500 leading-relaxed m-0",
                         style={"margin": 0}),
            className="bg-gray-50 rounded-xl p-4 mt-4",
        )

        content = html.Div(chart_items + [evidence_block])

        # Tous dépliés par défaut
        details_props = {"open": True}

        cards.append(
            html.Details([header, content],
                         className="bg-white rounded-2xl p-5 mb-3 hover:shadow-md transition-all duration-200",
                         style={"boxShadow": _CARD_SHADOW},
                         **details_props)
        )

    return html.Div([
        info_banner(
            "Ces hypothèses ont été formulées en amont et testées grâce aux données "
            "internes aramisauto enrichies de sources INSEE et SDES."
        ),
        summary,
        section_hd("science", "Analyse des hypothèses"),
        html.Div(cards),
    ])
