import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PROC = os.path.join(BASE_DIR, "01_data", "processed")
DATA_EXT  = os.path.join(BASE_DIR, "01_data", "external")

# Constantes segments
SEGMENT_COLORS = {
    "Hyperconnectés":      "#EF4444",
    "Primo-Numériques":    "#3B82F6",
    "Seniors Premium":     "#10B981",
    "Opportunistes Budget":"#F59E0B",
}

SEGMENT_ICONS = {
    "Hyperconnectés":      "wifi",
    "Primo-Numériques":    "laptop",
    "Seniors Premium":     "workspace_premium",
    "Opportunistes Budget":"local_offer",
}

SEGMENT_DESC = {
    "Hyperconnectés":      "Navigateurs digitaux très actifs, prix médian 24k, ~50 ans",
    "Primo-Numériques":    "Acheteurs récents financés, prix médian 22k, 50% LOA/Crédit",
    "Seniors Premium":     "Coeur de cible, prix médian 26k, véhicules quasi-neufs",
    "Opportunistes Budget":"Budget optimisé, prix médian 15k, fort kilométrage, ~47 ans",
}

SEGMENT_TOOLTIP = {
    "Hyperconnectés":      "Clients qui consultent beaucoup le site avant d'acheter (736 sessions en moyenne). Panier moyen de 24k.",
    "Primo-Numériques":    "Acheteurs de véhicules récents qui utilisent le financement (50% en LOA/Crédit). Panier moyen de 22k.",
    "Seniors Premium":     "Segment le plus important (45% des clients). Acheteurs expérimentés, véhicules quasi-neufs, panier le plus élevé (26k).",
    "Opportunistes Budget":"Acheteurs sensibles au prix, véhicules à fort kilométrage. Les plus jeunes (~47 ans), panier moyen de 15k.",
}

# Chargement avec cache
@functools.lru_cache(maxsize=4)
def load_main_table() -> pd.DataFrame:
    path = os.path.join(DATA_PROC, "table_analyse_finale.csv")
    df = pd.read_csv(path, low_memory=False)
    df["DATE_PANIER"]  = pd.to_datetime(df["DATE_PANIER"],  errors="coerce")
    df["DATE_CREATION"]= pd.to_datetime(df["DATE_CREATION"],errors="coerce")
    df["MOIS_PANIER"]  = df["DATE_PANIER"].dt.to_period("M").astype(str)
    return df

@functools.lru_cache(maxsize=2)
def load_sdes_data() -> pd.DataFrame:
    path = os.path.join(DATA_EXT, "sdes_immatriculations_vn_energie_2021_2024.csv")
    return pd.read_csv(path)

@functools.lru_cache(maxsize=2)
def load_insee_revenus() -> pd.DataFrame:
    path = os.path.join(DATA_EXT, "insee_revenus_medians_dept_2021.csv")
    return pd.read_csv(path, dtype={"NUM_DEPT": str})

def get_kpis(df: pd.DataFrame) -> dict:
    d = df[df["SEGMENT_NOM"].notna()].copy()
    return {
        "nb_clients":       int(d["LEAD_ID"].nunique()),
        "ca_total":         float(d["PRIX_VENTE_TTC_COM"].sum()),
        "panier_moyen":     float(d["PRIX_VENTE_TTC_COM"].mean()),
        "taux_financement": float(d["A_FINANCEMENT"].mean() * 100),
        "taux_reprise":     float(d["A_REPRISE"].mean() * 100),
        "age_moyen":        float(d["AGE"].mean()),
        "pct_hommes":       float(d["IS_MALE"].mean() * 100),
        "nb_regions":       int(d["NOM_REGION"].nunique()),
        "nb_agences":       int(d["AGENCE_LIVRAISON_COM"].nunique()),
        "marque_top":       str(d["VEHICULE_MARQUE"].mode()[0]) if not d["VEHICULE_MARQUE"].isna().all() else "N/A",
    }
