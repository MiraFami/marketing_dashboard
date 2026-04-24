"""
Composants UI réutilisables (cartes, grilles, icônes, etc.)
"""
import pandas as pd
from dash import dcc, html, dash_table
from utils.charts import hex_to_rgba


_GRID_GAP = 16
_CARD_SHADOW = "0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.02)"

# Couleurs aramisauto
ARAMIS_DARK   = "#003c57"
ARAMIS_LIME   = "#6ad724"
ARAMIS_INDIGO = "#605de7"


def icon(name: str, cls: str = "") -> html.Span:
    """Icône Material Icons."""
    return html.Span(name, className=f"material-icons-round {cls}".strip())


def kpi_card(icon_name: str, value: str, label: str, color: str = "#3B82F6") -> html.Div:
    """Carte KPI simple."""
    return html.Div([
        html.Div(icon(icon_name, "icon-nav"),
                 className="w-8 h-8 rounded-lg flex items-center justify-center mb-3",
                 style={"background": hex_to_rgba(color, 0.08), "color": color}),
        html.Div(value, className="text-xl font-bold text-gray-900 tracking-tight leading-none"),
        html.Div(label, className="text-[10px] font-medium text-gray-400 uppercase tracking-wider mt-1.5"),
    ], className="bg-white rounded-2xl p-5 hover:-translate-y-0.5 transition-all duration-200 cursor-default",
       style={"boxShadow": _CARD_SHADOW})


def chart_card(figure, height: str = "100%") -> html.Div:
    """Wrapper pour un graphe Plotly."""
    return html.Div(
        dcc.Graph(
            figure=figure,
            config={"displaylogo": False, "responsive": True,
                    "modeBarButtonsToRemove": ["lasso2d", "select2d"]},
            style={"height": height, "width": "100%"},
        ),
        className="bg-white rounded-2xl overflow-hidden p-2 w-full",
        style={"boxShadow": _CARD_SHADOW},
    )


def section_hd(icon_name: str, label: str) -> html.Div:
    """Titre de section."""
    return html.Div([
        icon(icon_name, "icon-sm"),
        html.Span(label),
    ], className="flex items-center gap-2 text-[11px] font-semibold uppercase tracking-wider mt-8 mb-4",
       style={"color": ARAMIS_DARK, "opacity": "0.4"})


def info_banner(text: str) -> html.Div:
    """Bandeau d'info."""
    return html.Div([
        icon("info", "icon-sm text-gray-400"),
        html.Span(text, className="text-sm text-gray-500"),
    ], className="flex items-start gap-2 bg-gray-50 rounded-xl p-3 mb-5")


def grid(*cols, gap: int = 4, extra: str = "") -> html.Div:
    """Grille flex-wrap (le grid CSS Tailwind marche mal avec le CDN Dash)."""
    gap_px = gap * 4
    cls = extra if extra else None
    return html.Div(
        list(cols),
        className=cls,
        style={"display": "flex", "flexWrap": "wrap", "gap": f"{gap_px}px", "marginBottom": "16px"},
    )


def col(children, xs: int = 12, md: int = None, lg: int = None,
        xl: int = None, extra: str = "") -> html.Div:
    """Colonne sur 12 (flex-basis)."""
    best = xl or lg or md or xs
    pct = round(best / 12 * 100, 2)
    body = children if isinstance(children, list) else [children]
    return html.Div(
        body,
        style={
            "flex": "1 1 auto",
            "width": f"calc({pct}% - {_GRID_GAP}px)",
            "minWidth": "280px" if best <= 4 else "0",
            "maxWidth": "100%",
        },
        className=extra if extra else None,
    )


def seg_metric(val: str, lbl: str) -> html.Div:
    """Petite métrique pour les cartes segment."""
    return html.Div([
        html.Div(val, className="text-sm font-semibold text-gray-700"),
        html.Div(lbl, className="text-[10px] text-gray-400 font-normal"),
    ], className="flex flex-col gap-0.5")


def tbl(df_data: pd.DataFrame) -> dash_table.DataTable:
    """DataTable Dash sans pagination."""
    return dash_table.DataTable(
        data=df_data.to_dict("records"),
        columns=[{"name": str(c), "id": str(c)} for c in df_data.columns],
        style_table={"overflowX": "auto"},
        page_action="none",
    )
