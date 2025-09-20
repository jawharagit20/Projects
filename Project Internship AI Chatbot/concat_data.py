import pandas as pd
import os
from datetime import datetime

# Dossier contenant tous les CSV
DATA_DIR = "data/"

# ---------------------------
# Charger produits (fixe)
# ---------------------------
produits_file = os.path.join(DATA_DIR, "produits.csv")
if os.path.exists(produits_file):
    produits = pd.read_csv(produits_file)
    print("Produits chargés :", len(produits))
else:
    produits = pd.DataFrame()
    print("produits.csv manquant !")

# ---------------------------
# 2Charger et concaténer tous les fichiers de stock (ancien et jour)
# ---------------------------
stock_list = []

for file in os.listdir(DATA_DIR):
    if file.startswith("stock") and file.endswith(".csv"):
        # Extraire la date à partir du nom du fichier si possible
        date_str = file.replace("stock", "").replace(".csv", "").replace("_", "")
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            # Si le fichier n'a pas de date, utiliser la date du jour
            date = datetime.today().date()
        df = pd.read_csv(os.path.join(DATA_DIR, file))
        df["Date"] = date
        stock_list.append(df)

if stock_list:
    stock_global = pd.concat(stock_list, ignore_index=True)
    print("Stock chargé (historique complet) :", len(stock_global))
else:
    stock_global = pd.DataFrame()
    print("⚠ Aucun fichier stock trouvé !")

# ---------------------------
# Charger et concaténer tous les fichiers de commandes (ancien et jour)
# ---------------------------
commandes_list = []

for file in os.listdir(DATA_DIR):
    if file.startswith("commandes") and file.endswith(".csv"):
        date_str = file.replace("commandes", "").replace(".csv", "").replace("_", "")
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except:
            date = datetime.today().date()
        df = pd.read_csv(os.path.join(DATA_DIR, file))
        df["Date"] = date
        commandes_list.append(df)

if commandes_list:
    commandes_global = pd.concat(commandes_list, ignore_index=True)
    print("Commandes chargées (historique complet) :", len(commandes_global))
    commandes_global['Date_Commande'] = pd.to_datetime(commandes_global['Date_Commande'], errors='coerce')
else:
    commandes_global = pd.DataFrame()
    print("⚠ Aucun fichier commandes trouvé !")

# ---------------------------
# Fonctions de questions simples pour le chatbot
# ---------------------------

# Stock d'un produit à une date donnée
def get_stock(produit_ref, date):
    res = stock_global[(stock_global["Référence_Produit"] == produit_ref) &
                       (stock_global["Date"] == date)]
    if not res.empty:
        return f"Stock de {produit_ref} le {date} : {int(res['Stock_Final'].values[0])}"
    return "Aucune donnée trouvée."

# Commandes en retard
def get_commandes_retard(date):
    retard = commandes_global[commandes_global["Date_Livraison_Prévue"] < str(date)]
    if not retard.empty:
        return retard
    return "Aucune commande en retard."

