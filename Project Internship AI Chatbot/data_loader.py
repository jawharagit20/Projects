# ---------------------------- 
# Fichier : data_loader.py
# Description : Chargement et préparation des données produits, stock et commandes
# ----------------------------

from datetime import datetime
import os
import pandas as pd

DATA_DIR = "data"

# ----------------------------
# 1️⃣ Charger produits fixes
# ----------------------------
produits_file = os.path.join(DATA_DIR, "produits.csv")
produits = pd.read_csv(produits_file) if os.path.exists(produits_file) else pd.DataFrame()
if produits.empty:
    print("⚠ produits.csv manquant !")
else:
    print(f"Produits chargés : {len(produits)}")

# ----------------------------
# 2️⃣ Fonction générique pour charger les fichiers journaliers
# ----------------------------
def charger_csv_journalier(prefix):
    """
    Charge tous les fichiers CSV commençant par `prefix` dans le dossier DATA_DIR
    et ajoute une colonne 'Date' extraite du nom de fichier ou utilisant la date du jour.
    """
    files_list = []
    for file in os.listdir(DATA_DIR):
        if file.startswith(prefix) and file.endswith(".csv"):
            df = pd.read_csv(os.path.join(DATA_DIR, file))

            # Extraction de la date depuis le nom du fichier
            try:
                date_str = file.replace(prefix, "").replace(".csv", "").replace("_", "")
                date_val = datetime.strptime(date_str, "%Y-%m-%d").date()
            except:
                date_val = datetime.today().date()  # fallback si date non trouvée

            df["Date"] = date_val
            files_list.append(df)

    if files_list:
        return pd.concat(files_list, ignore_index=True)
    else:
        print(f"⚠ Aucun fichier {prefix} trouvé !")
        return pd.DataFrame()

# ----------------------------
# 3️⃣ Charger stock et commandes
# ----------------------------
stock_global = charger_csv_journalier("stock")
commandes_global = charger_csv_journalier("commandes")

print(f"Stock chargé : {len(stock_global)} lignes")
print(f"Commandes chargées : {len(commandes_global)} lignes")

# ----------------------------
# 4️⃣ Fonctions utilitaires pour le chatbot / KPI
# ----------------------------
def get_stock(produit_ref, date):
    """
    Retourne le stock d'un produit à une date donnée
    """
    res = stock_global[
        (stock_global["Référence_Produit"].str.upper() == produit_ref.upper()) &
        (stock_global["Date"] == date)
    ]
    if not res.empty:
        return f"Stock de {produit_ref} le {date} : {int(res['Stock_Final'].values[0])}"
    return "Aucune donnée trouvée."

def get_commandes_retard(date):
    """
    Retourne les commandes en retard à une date donnée
    """
    if commandes_global.empty:
        return "Aucune commande disponible."
    commandes_global["Date_Livraison_Prévue"] = pd.to_datetime(commandes_global["Date_Livraison_Prévue"], errors='coerce').dt.date
    retard = commandes_global[commandes_global["Date_Livraison_Prévue"] < date]
    if not retard.empty:
        return retard
    return "Aucune commande en retard."
