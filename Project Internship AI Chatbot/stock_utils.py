import pandas as pd
import os
import glob

# Chargement dynamique des fichiers de stock

DATA_DIR = "data"
stock_files = glob.glob(os.path.join(DATA_DIR, "stock_*.csv"))

# Fusionner tous les fichiers de stock dans un seul DataFrame
stocks_df_list = []
for f in stock_files:
    df = pd.read_csv(f)
    stocks_df_list.append(df)

if stocks_df_list:
    stocks_df = pd.concat(stocks_df_list, ignore_index=True)
else:
    stocks_df = pd.DataFrame()
    print("⚠ Aucun fichier de stock trouvé !")
# ------
def get_stock_produit(ref, date=None):
    """
    Retourne toutes les infos de stock pour un produit donné.
    Si 'date' est fournie, filtre sur cette date.
    """
    df = stocks_df[stocks_df['Référence_Produit'].str.upper() == ref.upper()]
    if date:
        df = df[df['Date'] == date]

    if df.empty:
        return f"❌ Aucune donnée trouvée pour le produit {ref}."
    return df.to_dict(orient="records")

# ---- Stock Initial & Final ----

def get_stock_initial(ref, date=None):
    """
    Retourne le stock initial d’un produit à une date donnée (ou toutes les dates si None).
    """
    df = stocks_df[stocks_df['Référence_Produit'].str.upper() == ref.upper()]
    if date:
        df = df[df['Date'] == date]

    if df.empty:
        return f"❌ Pas de stock initial pour {ref}."
    return df[['Date', 'Stock_Initial']].to_dict(orient="records")


def get_stock_final(ref, date=None):
    """
    Retourne le stock final d’un produit à une date donnée (ou toutes les dates si None).
    """
    df = stocks_df[stocks_df['Référence_Produit'].str.upper() == ref.upper()]
    if date:
        df = df[df['Date'] == date]

    if df.empty:
        return f"❌ Pas de stock final pour {ref}."
    return df[['Date', 'Stock_Final']].to_dict(orient="records")

# ---- Statut ----

def get_statut_stock(ref, date=None):
    """
    Retourne le statut (OK, URGENT, RUPTURE) d’un produit.
    """
    df = stocks_df[stocks_df['Référence_Produit'].str.upper() == ref.upper()]
    if date:
        df = df[df['Date'] == date]

    if df.empty:
        return f"❌ Pas de statut trouvé pour {ref}."
    return df[['Date', 'Statut']].to_dict(orient="records")
# ---- Site ----

def get_stock_site(site_name, date=None):
    """
    Retourne tous les produits et leurs stocks d’un site donné.
    """
    df = stocks_df[stocks_df['Site'].str.lower() == site_name.lower()]
    if date:
        df = df[df['Date'] == date]

    if df.empty:
        return f"❌ Aucun produit trouvé pour le site {site_name}."
    return df.to_dict(orient="records")


def get_stock_produit_site(ref, site_name, date=None):
    """
    Retourne les infos de stock d’un produit précis dans un site donné.
    """
    df = stocks_df[
        (stocks_df['Référence_Produit'].str.upper() == ref.upper()) &
        (stocks_df['Site'].str.lower() == site_name.lower())
    ]
    if date:
        df = df[df['Date'] == date]

    if df.empty:
        return f"❌ Pas de stock trouvé pour {ref} dans {site_name}."
    return df.to_dict(orient="records")

# ---- Produits par statut ----

def produits_en_rupture(date=None):
    df = stocks_df[stocks_df['Statut'] == "RUPTURE"]
    if date:
        df = df[df['Date'] == date]
    if df.empty:
        return "✅ Aucun produit en rupture."
    ruptures = df[['Référence_Produit', 'Site', 'Date']].to_dict(orient="records")
    lignes = []
    for r in ruptures:
        lignes.append(f"📦 {r['Référence_Produit']} | 📍 {r['Site']} | 📅 {r['Date']}")

    return "\n".join(lignes)

def produits_urgents(date=None):
    df = stocks_df[stocks_df['Statut'] == "URGENT"]
    if date:
        df = df[df['Date'] == date]
    if df.empty:
        return "✅ Aucun produit en URGENT."
    urgents = df[['Référence_Produit', 'Site', 'Date']].to_dict(orient="records")
    # Formater en liste lisible
    lignes = []
    for u in urgents:
        lignes.append(f"⚡ {u['Référence_Produit']} | 📍 {u['Site']} | 📅 {u['Date']}")

    return "\n".join(lignes)
    
# ---- Evolution ----

def evolution_stock(ref):
    """
    Retourne l’évolution du stock final d’un produit sur toutes les dates disponibles.
    """
    df = stocks_df[stocks_df['Référence_Produit'].str.upper() == ref.upper()]
    if df.empty:
        return f"❌ Pas d’historique pour le produit {ref}."
    historique = df[['Date', 'Stock_Initial', 'Stock_Final', 'Statut']].to_dict(orient="records")
    # Formatage lisible
    lignes = []
    for h in historique:
        lignes.append(
            f"📅 {h['Date']} | 📦 Stock Initial: {h['Stock_Initial']} | 🔻 Stock Final: {h['Stock_Final']} | 📊 Statut: {h['Statut']}"
        )
    return "\n".join(lignes)
# Ajoutez cette méthode pour formater les résultats du stock
def _format_stock_result(self, result):
    """Formate les résultats complexes du stock pour l'affichage"""
    if isinstance(result, str):
        return result
    elif isinstance(result, list) and result:
        if len(result) == 1:
            # Retourne juste la valeur si un seul élément
            item = result[0]
            if 'Stock_Initial' in item:
                return item['Stock_Initial']
            elif 'Stock_Final' in item:
                return item['Stock_Final']
        return f"{len(result)} enregistrement(s) trouvé(s)"
    return "Aucune donnée disponible"
    