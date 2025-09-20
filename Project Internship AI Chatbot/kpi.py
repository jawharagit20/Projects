import pandas as pd
from datetime import datetime
from concat_data import produits, stock_global, commandes_global


# =========================
# Utilitaires
# =========================
def _ensure_datetime(df, col):
    """Convertit une colonne en datetime si nécessaire (sécurisé)."""
    if not df.empty and col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df


def convert_to_date(date_obj):
    """Convertit un objet en date (sans heure)."""
    if isinstance(date_obj, pd.Timestamp):
        return date_obj.date()
    elif isinstance(date_obj, str):
        return pd.to_datetime(date_obj, errors="coerce").date()
    elif hasattr(date_obj, "date"):
        return date_obj.date()
    return date_obj


# =========================
# 1. Valeur totale du stock
# =========================
def valeur_stock(date=None):
    try:
        if stock_global.empty or produits.empty:
            return 0

        df = stock_global.copy()
        df = df.merge(
            produits[["Référence_Produit", "Coût_Unitaire"]],
            on="Référence_Produit",
            how="left",
        )

        df = _ensure_datetime(df, "Date")

        if date:
            date_obj = convert_to_date(date)
            df = df[df["Date"].dt.date == date_obj]

        df["Valeur_Stock"] = df["Stock_Final"] * df["Coût_Unitaire"]
        return round(df["Valeur_Stock"].sum(), 2)
    except Exception as e:
        print(f"Erreur valeur_stock: {e}")
        return 0


# =========================
# 2. Produits en rupture
# =========================
def produits_en_rupture(date=None):
    try:
        df = stock_global.copy()
        df = _ensure_datetime(df, "Date")

        if date:
            date_obj = convert_to_date(date)
            df = df[df["Date"].dt.date == date_obj]  # <-- ne filtre que si date fournie

        # Filtrer tous les produits en rupture
        ruptures = df[df["Stock_Final"] == 0]

        if ruptures.empty:
            return "✅ Aucun produit en rupture."
        
        resultats = []
        for _, row in ruptures.iterrows():
            resultats.append(f"📦 {row['Référence_Produit']} | 📍 {row['Entrepot']} | 📅 {row['Date'].date()}")
        return "\n".join(resultats)
    except Exception as e:
        print(f"Erreur produits_en_rupture: {e}")
        return []



# =========================
# 3. Taux de livraison à temps
# =========================
def taux_livraison(date=None):
    try:
        df = commandes_global.copy()
        df = _ensure_datetime(df, "Date")
        df = _ensure_datetime(df, "Date_Livraison_Prévue")
        df = _ensure_datetime(df, "Date_Livraison_Réelle")

        if date:
            date_obj = convert_to_date(date)
            df = df[df["Date"].dt.date <= date_obj]

        total = len(df)
        if total == 0:
            return None

        on_time = len(
            df[df["Date_Livraison_Réelle"] <= df["Date_Livraison_Prévue"]]
        )
        return round(on_time / total * 100, 2)
    except Exception as e:
        print(f"Erreur taux_livraison: {e}")
        return None


# =========================
# 4. Commandes en retard
# =========================
def commandes_en_retard(date=None):
    try:
        df = commandes_global.copy()
        df = _ensure_datetime(df, "Date")
        df = _ensure_datetime(df, "Date_Livraison_Prévue")
        df = _ensure_datetime(df, "Date_Livraison_Réelle")

        if date:
            date_obj = convert_to_date(date)
            df = df[df["Date"].dt.date <= date_obj]

        retard = df[df["Date_Livraison_Réelle"] > df["Date_Livraison_Prévue"]]
        return retard[["Num_Commande", "Référence_Produit"]].values.tolist()
    except Exception as e:
        print(f"Erreur commandes_en_retard: {e}")
        return []


# =========================
# 5. Produits à réapprovisionner
# =========================
def produits_a_reapprovisionner(date=None):
    try:
        df = stock_global.copy()
        df = df.merge(
            produits[["Référence_Produit", "Seuil_Réappro"]],
            on="Référence_Produit",
            how="left",
        )
        df = _ensure_datetime(df, "Date")

        if date:
            date_obj = convert_to_date(date)
            df = df[df["Date"].dt.date == date_obj]

        df = df[df["Stock_Final"] < df["Seuil_Réappro"]]
        return df["Référence_Produit"].tolist()
    except Exception as e:
        print(f"Erreur produits_a_reapprovisionner: {e}")
        return []


# =========================
# 6. Commandes clients du mois
# =========================
def commandes_clients_ce_mois(commandes_df):
    if commandes_df.empty:
        return 0

    commandes_df = _ensure_datetime(commandes_df, "Date_Commande")

    now = datetime.now()
    debut_mois = datetime(now.year, now.month, 1)

    commandes_mois = commandes_df[
        (commandes_df["Date_Commande"] >= debut_mois)
        & (commandes_df["Type_Commande"].str.lower() == "client")
    ]
    return len(commandes_mois)


# =========================
# 7. Stock total du mois
# =========================
def stock_total_ce_mois(stock_df: pd.DataFrame) -> int:
    if stock_df.empty:
        return 0

    stock_df = _ensure_datetime(stock_df, "Date")

    debut_mois = pd.to_datetime(datetime.today().strftime("%Y-%m-01"))
    fin_mois = pd.to_datetime(datetime.today())

    df_mois = stock_df[
        (stock_df["Date"] >= debut_mois) & (stock_df["Date"] <= fin_mois)
    ]

    if df_mois.empty:
        return 0

    dernier_stock = df_mois.sort_values("Date").groupby("Référence_Produit").tail(1)
    return int(dernier_stock["Stock_Final"].sum())


# =========================
# 8. Commandes fournisseurs du mois
# =========================
def commandes_fournisseurs_ce_mois(commandes_df: pd.DataFrame) -> int:
    if commandes_df.empty:
        return 0

    commandes_df = _ensure_datetime(commandes_df, "Date_Commande")

    if reference_date is None:
        reference_date = pd.to_datetime(datetime.today())
        
    debut_mois = reference_date.replace(day=1)
    fin_mois = reference_date

    df_mois = commandes_df[
        (commandes_df["Date_Commande"] >= debut_mois)
        & (commandes_df["Date_Commande"] <= fin_mois)
        & (commandes_df["Type_Commande"].str.lower().str.contains("fournisseur"))
    ]
    print(f"Commandes trouvées: {len(df_mois)}")
    return len(df_mois)


# =========================
# 9. Stock total d’un produit
# =========================
def stock_total_produit(ref_produit, stock_df, date=None):
    ref_produit = ref_produit.upper().replace(" ", "")
    df = stock_df.copy()
    df = _ensure_datetime(df, "Date")

    df = df[
        df["Référence_Produit"].str.upper().str.replace(" ", "") == ref_produit
    ]

    if date:
        date_obj = convert_to_date(date)
        df = df[df["Date"].dt.date == date_obj]

    if df.empty:
        return 0

    return int(df["Stock_Final"].sum())