import pandas as pd
import os

# Charger le CSV produits
DATA_DIR = "data"
produits_file = os.path.join(DATA_DIR, "produits.csv")

if os.path.exists(produits_file):
    produits_df = pd.read_csv(produits_file)
else:
    produits_df = pd.DataFrame()
    print("⚠ produits.csv manquant !")

# Fonctions 
def get_produit_info(ref):
    """
    Retourne toutes les informations d'un produit à partir de sa référence.
    """
    df = produits_df[produits_df['Référence_Produit'].str.upper() == ref.upper()]
    if df.empty:
        return f"❌ Produit {ref} non trouvé."
    return df.to_dict(orient='records')[0]  # Retourne un dictionnaire avec toutes les colonnes


def get_fournisseur_principal(ref):
    """
    Retourne le fournisseur principal du produit.
    """
    info = get_produit_info(ref)
    if isinstance(info, dict):
        return info.get('Fournisseur_Principal', 'Information non disponible')
    return info


def get_delai_livraison(ref):
    """
    Retourne le délai de livraison en jours du produit.
    """
    info = get_produit_info(ref)
    if isinstance(info, dict):
        return info.get('Délai_Livraison_Jours', 'Information non disponible')
    return info


def get_cout_unitaire(ref):
    """
    Retourne le coût unitaire du produit.
    """
    info = get_produit_info(ref)
    if isinstance(info, dict):
        return info.get('Coût_Unitaire', 'Information non disponible')
    return info


def get_seuil_reappro(ref):
    """
    Retourne le seuil de réapprovisionnement du produit.
    """
    info = get_produit_info(ref)
    if isinstance(info, dict):
        return info.get('Seuil_Réappro', 'Information non disponible')
    return info


def get_poids_unitaire(ref):
    """
    Retourne le poids unitaire du produit.
    """
    info = get_produit_info(ref)
    if isinstance(info, dict):
        return info.get('Poids_Unitaire', 'Information non disponible')
    return info


def list_produits_par_famille(famille_name):
    """
    Retourne la liste des produits d'une famille donnée.
    """
    df = produits_df[produits_df['Famille'].str.lower() == famille_name.lower()]
    if df.empty:
        return f"❌ Aucune produit trouvé pour la famille '{famille_name}'."
    return df['Référence_Produit'].tolist()


def produit_plus_cher():
    """
    Retourne le produit avec le coût unitaire le plus élevé.
    """
    if produits_df.empty:
        return "⚠ Aucun produit disponible."
    max_cout = produits_df['Coût_Unitaire'].max()  # Trouve le coût maximum
    produits_max = produits_df[produits_df['Coût_Unitaire'] == max_cout]  # Tous les produits avec ce coût
    return ", ".join(produits_max['Référence_Produit'].tolist())
# Ajout de fonctions sur la colonne Famille

def list_familles():
    """
    Retourne la liste unique de toutes les familles présentes dans le CSV.
    """
    if produits_df.empty:
        return "⚠ Aucun produit disponible."
    return produits_df['Famille'].unique().tolist()


def produits_par_famille(famille_name):
    """
    Retourne tous les produits d'une famille donnée.
    """
    df = produits_df[produits_df['Famille'].str.lower() == famille_name.lower()]
    if df.empty:
        return f"❌ Aucune produit trouvé pour la famille '{famille_name}'."
    return df.to_dict(orient='records')

def get_famille_produit(ref):
    """
    Retourne la famille d'un produit à partir de sa référence.
    """
    df = produits_df[produits_df['Référence_Produit'].str.upper() == ref.upper()]
    if df.empty:
        return f"❌ Produit {ref} non trouvé."
    return df.iloc[0].get('Famille', 'Information non disponible')

def get_designation(ref):
    """Retourne la désignation du produit à partir de sa référence."""
    info = get_produit_info(ref)
    if isinstance(info, dict):
        return info.get('Désignation', 'Information non disponible')
    return info