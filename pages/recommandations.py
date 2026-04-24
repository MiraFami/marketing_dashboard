"""
Page Recommandations : actions basées sur les résultats des hypothèses.
"""
import pandas as pd
from dash import dcc, html

from utils.data_loader import SEGMENT_COLORS
from utils.charts import hex_to_rgba
from components import icon, section_hd, grid, col


_CARD_SHADOW = "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02)"

RECO_HYPOTHESES = [
    {
        "hyp": "H1 : Clientèle masculine 45-60 ans (Validée)",
        "icon": "check_circle", "color": "#10B981",
        "constat": (
            "La clientèle est à plus de 70% masculine avec un âge moyen autour de 51 ans. "
            "Le segment Seniors Premium (57 ans en moyenne) représente 45% des clients."
        ),
        "actions": [
            ("Diversifier la cible", "Développer des campagnes marketing ciblant les femmes et les 25-40 ans pour élargir la base client."),
            ("Adapter la communication Seniors", "Privilégier un ton rassurant, mettre en avant les garanties, le SAV et le contact humain pour ce segment majoritaire."),
            ("Contenu adapté par tranche d'âge", "Segmenter les emails et publicités selon l'âge : digital-first pour les jeunes, téléphone et agence pour les seniors."),
        ],
    },
    {
        "hyp": "H2 : Électrique sous-représenté (Validée)",
        "icon": "check_circle", "color": "#10B981",
        "constat": (
            "Environ 4% de ventes électriques chez aramisauto contre ~17% sur le marché national VN. "
            "Décalage structurel lié au positionnement sur le marché VO."
        ),
        "actions": [
            ("Enrichir l'offre électrique VO", "Sourcer davantage de véhicules électriques d'occasion pour combler l'écart avec le marché national."),
            ("Page dédiée « Transition électrique »", "Créer un espace pédagogique sur le site : autonomie, coût d'usage, bornes, aides à l'achat."),
            ("Partenariats bornes de recharge", "Proposer des offres couplées véhicule + solution de recharge à domicile pour lever les freins à l'achat."),
        ],
    },
    {
        "hyp": "H3 : Navigation web ≠ panier élevé (Invalidée)",
        "icon": "cancel", "color": "#EF4444",
        "constat": (
            "Les Hyperconnectés (736 sessions) ont un panier de ~24k€ tandis que les Seniors Premium "
            "(~123 sessions) atteignent ~26k€. La navigation intensive traduit l'hésitation, pas le standing."
        ),
        "actions": [
            ("Remarketing ciblé Hyperconnectés", "Retargeting personnalisé sur les véhicules consultés pour convertir ces clients hésitants à fort engagement digital."),
            ("Contenu de réassurance", "Vidéos 360°, comparateurs interactifs et avis clients pour réduire le temps de décision des gros navigateurs."),
            ("Conseiller dédié post-visite", "Chat live ou call-back automatique après X sessions sans conversion pour accompagner la décision."),
        ],
    },
    {
        "hyp": "H4 : Financement ≠ petits budgets uniquement (Partielle)",
        "icon": "warning", "color": "#F59E0B",
        "constat": (
            "Les Primo-Numériques ont le taux de financement le plus élevé (~50%), mais les "
            "Opportunistes Budget l'utilisent moins que prévu. Le financement est un outil de confort, "
            "pas de nécessité."
        ),
        "actions": [
            ("Simulateur financement en page produit", "Afficher la mensualité LOA/Crédit directement sur chaque fiche véhicule pour tous les segments."),
            ("Offres financement Budget", "Proposer des formules sans apport et micro-crédit adaptées aux Opportunistes Budget pour augmenter l'adoption."),
            ("Upsell via financement", "Proposer aux Primo-Numériques financés des véhicules légèrement au-dessus de leur budget grâce à des mensualités attractives."),
        ],
    },
    {
        "hyp": "H5 : Distance & livraison à domicile (Partielle)",
        "icon": "warning", "color": "#F59E0B",
        "constat": (
            "Corrélation positive entre distance et choix de livraison à domicile, mais le segment "
            "et le prix restent plus déterminants. La majorité des clients (~84%) choisissent le retrait en agence."
        ),
        "actions": [
            ("Livraison premium ciblée", "Proposer la livraison à domicile gratuite ou à prix réduit pour les clients à plus de 50 km d'une agence."),
            ("Maillage territorial", "Identifier les zones géographiques à forte demande sans agence proche pour y développer des points relais."),
            ("Communication proactive", "Pour les clients éloignés détectés en ligne, mettre en avant l'option livraison dès la page produit."),
        ],
    },
]


def _reco_card(reco: dict) -> html.Div:
    """Carte de recommandation basée sur une hypothèse."""
    c = reco["color"]

    actions_html = [
        html.Div([
            html.Div(name, className="text-[13px] font-semibold text-gray-800"),
            html.Div(desc, className="text-[12px] text-gray-400 mt-0.5 leading-relaxed"),
        ], className="pl-3 py-1 mb-1.5 border-l-2 border-gray-200")
        for name, desc in reco["actions"]
    ]

    return html.Div([
        html.Div([
            html.Div([
                html.Div(icon(reco["icon"], "icon-nav"),
                         className="w-8 h-8 rounded-lg flex items-center justify-center",
                         style={"background": hex_to_rgba(c, 0.08), "color": c}),
                html.Div([
                    html.Span(reco["hyp"], className="text-sm font-semibold text-gray-800"),
                ], className="ml-2.5"),
            ], className="flex items-center"),
        ], className="mb-4"),
        grid(
            col([
                html.Div("Constat", className="text-[10px] font-medium text-gray-400 uppercase tracking-wider mb-2"),
                html.Div(reco["constat"], className="text-[13px] text-gray-500 leading-relaxed"),
            ], xs=12, lg=5),
            col([
                html.Div("Actions recommandées", className="text-[10px] font-medium text-gray-400 uppercase tracking-wider mb-2"),
                html.Div(actions_html),
            ], xs=12, lg=7),
            gap=4, extra="mb-0",
        ),
    ], className="bg-white rounded-2xl p-5 mb-3 hover:shadow-md transition-all duration-200",
       style={"boxShadow": _CARD_SHADOW})


def page_recommandations(df_seg: pd.DataFrame) -> html.Div:
    cards = [_reco_card(reco) for reco in RECO_HYPOTHESES]

    return html.Div([
        section_hd("tips_and_updates", "Recommandations basées sur les hypothèses"),
        html.Div(cards),
    ])
