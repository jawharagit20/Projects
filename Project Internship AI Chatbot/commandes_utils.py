# commandes_utils.py
import pandas as pd
from datetime import datetime
from data_loader import commandes_global  # utiliser le dataframe déjà chargé

# Fonctions pour le FAQBot
def get_commande_info(num_commande):
    """
    Retourne toutes les informations d'une commande à partir de son numéro.
    """
    df = commandes_global[commandes_global['Num_Commande'].str.upper() == num_commande.upper()]
    if df.empty:
        return f"❌ Commande {num_commande} non trouvée."
    return df.to_dict(orient='records')[0]  # dictionnaire complet de la ligne

def commandes_par_num_commande(num_commande):
    """
    Retourne toutes les lignes correspondant à un numéro de commande.
    Utile si une commande regroupe plusieurs produits.
    """
    df = commandes_global[commandes_global['Num_Commande'].str.upper() == num_commande.upper()]
    if df.empty:
        return f"❌ Aucune commande trouvée pour le numéro {num_commande}."
    return df.to_dict(orient='records')

def get_statut_commande(num_commande):
    """
    Retourne le statut d'une commande.
    """
    info = get_commande_info(num_commande)
    if isinstance(info, dict):
        return info.get('Statut_Commande', 'Information non disponible')
    return info

def get_date_livraison_prevue(num_commande):
    """
    Retourne la date de livraison prévue.
    """
    info = get_commande_info(num_commande)
    if isinstance(info, dict):
        return info.get('Date_Livraison_Prévue', 'Information non disponible')
    return info

def get_date_livraison_reelle(num_commande):
    """ Retourne la date de livraison réelle."""
    info = get_commande_info(num_commande)
    if isinstance(info, dict):
        return info.get('Date_Livraison_Réelle', 'Information non disponible')
    return info

def get_quantite_commande(num_commande):
    """ Retourne la quantité commandée."""
    info = get_commande_info(num_commande)
    if isinstance(info, dict):
        return info.get('Quantité', 'Information non disponible')
    return info

def get_type_commande(num_commande):
    """ Retourne le type de commande (Client / Fournisseur)."""
    info = get_commande_info(num_commande)
    if isinstance(info, dict):
        return info.get('Type_Commande', 'Information non disponible')
    return info

def get_contrepartie(num_commande):
    """Retourne la contrepartie de la commande."""
    info = get_commande_info(num_commande)
    if isinstance(info, dict):
        return info.get('Contrepartie', 'Information non disponible')
    return info

def commandes_en_retard():
    """Retourne toutes les commandes dont la date de livraison prévue est passée et qui ne sont pas encore livrées."""
    if commandes_global.empty:
        return "Aucune commande disponible."
    commandes_global["Date_Livraison_Prévue"] = pd.to_datetime(commandes_global["Date_Livraison_Prévue"], errors='coerce').dt.date
    commandes_global["Date_Livraison_Réelle"] = pd.to_datetime(commandes_global["Date_Livraison_Réelle"], errors='coerce').dt.date
    today = datetime.today().date()
    retard = commandes_global[
        (commandes_global["Statut_Commande"].str.lower() == "retard")
    ]
    if retard.empty:
        return "Aucune commande en retard."

     # ---- Formatage propre ----
    lignes = []
    for _, row in retard.iterrows():
        lignes.append(
            f"📦 {row['Type_Commande']} {row['Num_Commande']} "
            f"({row['Référence_Produit']}, Qté: {row['Quantité']}) "
            f"prévue le {row['Date_Livraison_Prévue']} "
            f"➡ Statut: {row['Statut_Commande']}, Contrepartie: {row['Contrepartie']}"
        )
    return "\n".join(lignes)

def commandes_par_produit(ref):
    """Retourne toutes les commandes pour un produit donné."""
    df = commandes_global[commandes_global['Référence_Produit'].str.upper() == ref.upper()]
    if df.empty:
        return f"❌ Aucune commande trouvée pour le produit {ref}."
    return df.to_dict(orient='records')

def commandes_par_type(type_commande):
    """Retourne toutes les commandes selon le type (Client / Fournisseur)."""
    df = commandes_global[commandes_global['Type_Commande'].str.lower() == type_commande.lower()]
    if df.empty:
        return f"❌ Aucune commande trouvée pour le type '{type_commande}'."
    return df.to_dict(orient='records')
