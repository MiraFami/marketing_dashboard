"""
Dashboard Dash pour le projet aramisauto Insight.
Lancement : python app_dash.py -> http://127.0.0.1:8050
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))

import dash
from dash import dcc, html, Input, Output, callback

from utils.data_loader import load_main_table, load_sdes_data, load_insee_revenus, get_kpis, SEGMENT_TOOLTIP
from components import icon, ARAMIS_DARK, ARAMIS_LIME

from pages.overview import page_overview
from pages.hypotheses import page_hypotheses
from pages.segmentation import page_segmentation
from pages.catalogue import page_catalogue
from pages.geographie import page_geographie
from pages.benchmark import page_benchmark
from pages.recommandations import page_recommandations


# Init Dash

app = dash.Dash(
    __name__,
    external_stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap",
        "https://fonts.googleapis.com/icon?family=Material+Icons+Round",
    ],
    external_scripts=[{"src": "https://cdn.tailwindcss.com"}],
    suppress_callback_exceptions=True,
    title="aramisauto Insight",
    update_title=None,
)
app._favicon = "favicon.ico"
server = app.server


# Chargement des données

df_main = load_main_table()
df_sdes = load_sdes_data()
df_rev  = load_insee_revenus()
df_seg  = df_main[df_main["SEGMENT_NOM"].notna()].copy()
kpis    = get_kpis(df_main)


# Navigation

NAV_ITEMS = [
    ("dashboard",        "Vue d'ensemble",  "page-overview"),
    ("science",          "Hypothèses",       "page-hypotheses"),
    ("hub",              "Segmentation",     "page-segmentation"),
    ("directions_car",   "Catalogue",        "page-catalogue"),
    ("public",           "Géographie",       "page-geographie"),
    ("trending_up",      "Benchmark marché", "page-benchmark"),
    ("tips_and_updates", "Recommandations",  "page-recommandations"),
]

PAGE_META = {
    "page-overview":        ("dashboard",       "Vue d'ensemble",   "KPIs globaux & tendances"),
    "page-hypotheses":      ("science",          "Hypothèses",       "5 hypothèses validées / invalidées"),
    "page-segmentation":    ("hub",              "Segmentation",     "4 profils K-means identifiés"),
    "page-catalogue":       ("directions_car",   "Catalogue",        "Analyse du parc vendu"),
    "page-geographie":      ("public",           "Géographie",       "Distribution territoriale"),
    "page-benchmark":       ("trending_up",      "Benchmark marché", "Comparaison SDES 2021-2024"),
    "page-recommandations": ("tips_and_updates", "Recommandations",  "Insights & plan d'action par segment"),
}

SEGS_OPTS  = [{"label": "Tous les segments", "value": "Tous"}] + [
    {"label": s, "value": s, "title": SEGMENT_TOOLTIP.get(s, "")}
    for s in sorted(df_seg["SEGMENT_NOM"].dropna().unique())]
GENRE_OPTS = [{"label": l, "value": v} for l, v in [("Tous", "Tous"), ("Homme", "Homme"), ("Femme", "Femme")]]


# Sidebar

def build_sidebar() -> html.Div:
    btns = [
        html.Button(
            [icon(ic, "icon-nav"), html.Span(lbl, className="text-[13px] font-medium")],
            id={"type": "nav-btn", "index": pid},
            className="flex items-center gap-3 px-3 py-2 mx-2 rounded-lg text-white/50 "
                      "hover:bg-white/8 hover:text-white/80 transition-all duration-150 "
                      "cursor-pointer border-0 w-[calc(100%-16px)] text-left",
            n_clicks=0,
        )
        for ic, lbl, pid in NAV_ITEMS
    ]

    return html.Div([
        # Logo
        html.A([
            html.Div([
                html.Div(
                    html.Img(src="/assets/logo-icon.svg",
                             style={"height": "20px", "width": "auto"}),
                    className="w-8 h-8 rounded-lg px-[2px] flex items-center justify-center",
                    style={"background": "rgba(106,215,36,0.12)"},
                ),
                html.Div([
                    html.Span("aramisauto", className="block text-[14px] font-semibold text-white tracking-tight"),
                    html.Span("Insight Dashboard", className="block text-[10px] font-medium",
                              style={"color": "rgba(255,255,255,0.4)"}),
                ]),
            ], className="flex items-center gap-2.5"),
        ], href="https://www.aramisauto.com", target="_blank",
           className="block px-5 py-5 no-underline hover:opacity-80 transition-opacity",
           style={"textDecoration": "none"}),


        html.Div("Menu", className="px-5 pt-3 pb-2 text-[10px] font-medium uppercase tracking-wider",
                 style={"color": "rgba(255,255,255,0.25)"}),
        html.Div(btns, id="nav-container"),

        html.Div(className="mx-5 my-3", style={"borderTop": "1px solid rgba(255,255,255,0.06)"}),


        html.Div("Filtres", className="px-5 pb-2 text-[10px] font-medium uppercase tracking-wider",
                 style={"color": "rgba(255,255,255,0.25)"}),
        html.Div([
            html.Label("Segment", className="block text-[10px] font-medium uppercase tracking-wider mb-1.5",
                       style={"color": "rgba(255,255,255,0.3)"}),
            dcc.Dropdown(id="filter-segment", options=SEGS_OPTS, value="Tous", clearable=False),
        ], className="px-3 mb-3"),
        html.Div([
            html.Label("Genre", className="block text-[10px] font-medium uppercase tracking-wider mb-1.5",
                       style={"color": "rgba(255,255,255,0.3)"}),
            dcc.Dropdown(id="filter-genre", options=GENRE_OPTS, value="Tous", clearable=False),
        ], className="px-3 mb-3"),

        html.Div(id="client-badge-sidebar"),


        html.Div([
            html.P([
                html.A("aramisauto.com", href="https://www.aramisauto.com", target="_blank",
                       style={"color": ARAMIS_LIME, "textDecoration": "none", "fontWeight": "500"}),
                html.Br(),
                html.Span("INSEE Filosofi 2021 - SDES 2021-2024", style={"color": "rgba(255,255,255,0.3)"}),
                html.Br(),
                html.Span("Données internes Jan-Mai 2024", style={"color": "rgba(255,255,255,0.3)"}),
            ], className="text-[10px] leading-relaxed m-0"),
            html.Div(style={"borderTop": "1px solid rgba(255,255,255,0.06)", "margin": "10px -20px 8px -20px"}),
            html.P([
                html.Span("Réalisé par : ", style={"color": "rgba(255,255,255,0.3)"}),
                html.Br(),
                html.Span("AMOUSSA Mansour | FAMI Zoumirath", style={"color": "rgba(255,255,255,0.3)"}),
            ], className="text-[10px] leading-relaxed m-0"),
        ], className="mt-auto px-5 py-5", style={"borderTop": "1px solid rgba(255,255,255,0.06)"}),
    ], className="w-60 min-h-screen flex flex-col fixed left-0 top-0 z-50 overflow-y-auto",
       style={"background": ARAMIS_DARK})

# Layout principal

app.layout = html.Div([
    dcc.Store(id="current-page", data="page-overview"),
    dcc.Location(id="url", refresh=False),

    build_sidebar(),

    html.Div([
        html.Div(id="topbar",
                 className="bg-white/80 backdrop-blur-lg px-8 h-14 flex items-center justify-between sticky top-0 z-40",
                 style={"borderBottom": "1px solid rgba(0,0,0,0.04)"}),
        html.Div(id="page-content", className="p-6"),
    ], style={"marginLeft": "240px", "width": "calc(100vw - 240px)", "minHeight": "100vh", "background": "#f8f9fa"}),
])


# Callbacks

@callback(Output("current-page", "data"),
          Input({"type": "nav-btn", "index": dash.ALL}, "n_clicks"),
          prevent_initial_call=True)
def update_page(_):
    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update
    return json.loads(ctx.triggered[0]["prop_id"].split(".")[0])["index"]


@callback(Output("nav-container", "children"),
          Input("current-page", "data"))
def update_nav(current_page):
    btns = []
    for ic, lbl, pid in NAV_ITEMS:
        active = pid == current_page
        style = {"background": "rgba(106,215,36,0.12)", "color": "#6ad724"} if active else {}
        base_cls = ("flex items-center gap-3 px-3 py-2 mx-2 rounded-lg text-[13px] font-medium "
                    "transition-all duration-150 cursor-pointer border-0 text-left w-[calc(100%-16px)]")
        cls = f"{base_cls} {'text-white' if active else 'text-white/50 hover:bg-white/8 hover:text-white/80'}"
        btns.append(html.Button(
            [icon(ic, "icon-nav"), html.Span(lbl, className="text-[13px] font-medium")],
            id={"type": "nav-btn", "index": pid}, className=cls, style=style, n_clicks=0,
        ))
    return btns


@callback(Output("topbar", "children"),
          Input("current-page", "data"),
          Input("filter-segment", "value"))
def update_topbar(page, filtre_seg):
    _, title, subtitle = PAGE_META.get(page, PAGE_META["page-overview"])
    n = len(df_seg) if filtre_seg == "Tous" else len(df_seg[df_seg["SEGMENT_NOM"] == filtre_seg])
    label = f"{n:,} clients" + (f" · {filtre_seg}" if filtre_seg != "Tous" else "")
    return [
        html.Div([
            html.P(title, className="text-sm font-semibold leading-none m-0", style={"color": "#003c57"}),
            html.P(subtitle, className="text-[11px] text-gray-400 mt-0.5 m-0"),
        ]),
        html.Div([
            icon("filter_list", "icon-xs"),
            html.Span(label, className="text-[11px] font-medium"),
        ], className="flex items-center gap-1.5 rounded-full px-3 py-1.5",
           style={"background": "rgba(0,60,87,0.06)", "color": "#003c57"}),
    ]


@callback(Output("client-badge-sidebar", "children"),
          Input("filter-segment", "value"),
          Input("filter-genre", "value"))
def update_badge(filtre_seg, filtre_genre):
    df_f = _apply_filters(filtre_seg, filtre_genre)
    return html.Div([
        icon("group", "icon-xs"),
        html.Span(f"{len(df_f):,} clients", className="text-[11px] font-medium"),
    ], className="flex items-center gap-1.5 mx-3 px-3 py-2 rounded-lg mb-2",
       style={"background": "rgba(106,215,36,0.08)", "color": "#6ad724"})


@callback(Output("page-content", "children"),
          Input("current-page", "data"),
          Input("filter-segment", "value"),
          Input("filter-genre", "value"))
def render_page(page, filtre_seg, filtre_genre):
    df_f = _apply_filters(filtre_seg, filtre_genre)

    if len(df_f) == 0:
        return html.Div([
            icon("search_off", "text-5xl text-gray-200"),
            html.P("Aucune donnée pour cette combinaison de filtres.", className="text-gray-400 text-sm mt-3"),
        ], className="flex flex-col items-center justify-center py-24")

    router = {
        "page-overview":        lambda: page_overview(df_f),
        "page-hypotheses":      lambda: page_hypotheses(df_f),
        "page-segmentation":    lambda: page_segmentation(df_f, df_seg),
        "page-catalogue":       lambda: page_catalogue(df_f, filtre_seg, df_seg),
        "page-geographie":      lambda: page_geographie(df_f, filtre_seg),
        "page-benchmark":       lambda: page_benchmark(df_f, df_sdes, df_seg),
        "page-recommandations": lambda: page_recommandations(df_seg),
    }
    return router.get(page, lambda: html.P("Page introuvable."))()


def _apply_filters(filtre_seg: str, filtre_genre: str):
    """Applique les filtres segment et genre sur df_seg."""
    df_f = df_seg.copy()
    if filtre_seg != "Tous":
        df_f = df_f[df_f["SEGMENT_NOM"] == filtre_seg]
    if filtre_genre == "Homme":
        df_f = df_f[df_f["IS_MALE"] == 1]
    elif filtre_genre == "Femme":
        df_f = df_f[df_f["IS_MALE"] == 0]
    return df_f


# Lancement

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=8050)
