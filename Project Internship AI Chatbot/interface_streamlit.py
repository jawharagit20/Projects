import streamlit as st
import pandas as pd
import requests
import time
import re
from datetime import datetime
from concat_data import produits, stock_global, commandes_global
from kpi import commandes_clients_ce_mois, commandes_fournisseurs_ce_mois, stock_total_ce_mois, valeur_stock, produits_en_rupture, taux_livraison, commandes_en_retard, produits_a_reapprovisionner,stock_total_produit
from historique import charger_historique, sauvegarder_historique
from commandes_utils import *
from produits_utils import *
from stock_utils import *

class FAQBot:
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model_name = "llama3.2:3b"

        # Initialisation correcte des attributs
        self.produits = produits if 'produits' in globals() else pd.DataFrame()
        self.stock = stock_global if 'stock_global' in globals() else pd.DataFrame()
        self.commandes = commandes_global if 'commandes_global' in globals() else pd.DataFrame()
        
        # Chargement des données dans le dictionnaire dataframes
        self.dataframes = {
            "produits": self.produits,
            "stock": self.stock,
            "commandes": self.commandes
        }

    # ------------ preparer le contexte de data -------------

    def _prepare_data_context(self):
        """Prépare le contexte des données pour Ollama de manière optimisée"""
        context = "Voici les données disponibles:\n\n"

        for name, df in self.dataframes.items():
            if not df.empty:
                # Résumé concis des données
                context += f"=== {name.upper()} ===\n"
                context += f"Colonnes: {', '.join(df.columns)}\n"
                context += f"Nombre d'entrées: {len(df)}\n"
                context += f"Période couverte: du {df['Date'].min()} au {df['Date'].max()}\n" if 'Date' in df.columns else ""

                # Aperçu très limité pour éviter les prompts trop longs
                context += "Exemple de données:\n"
                context += df.head(51).to_string(index=False) + "\n\n"

        # Ajouter les KPIs disponibles
        context += "=== KPIs DISPONIBLES ===\n"
        context += "- Valeur totale du stock\n"
        context += "- Produits en rupture de stock\n"
        context += "- Taux de livraison à temps\n"
        context += "- Commandes en retard\n"
        context += "- Produits à réapprovisionner\n\n"

        return context

    def _ask_ollama(self, question, context):
        """Envoie la question et le contexte à Ollama avec timeout augmenté"""
        try:
            prompt = f"""
            Tu es un assistant expert en analyse de données pour Yazaki. Tu as accès aux données suivantes:

            {context}

            Question: {question}

            Réponds de manière précise et concise en français. Si les données ne permettent pas de répondre, dis-le.
            Utilise les données fournies pour donner une réponse précise.
            """

            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False
            }

            # Timeout augmenté à 120 secondes
            response = requests.post(self.ollama_url, json=payload, timeout=120)

            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'Désolé, je n\'ai pas pu générer de réponse.')
            else:
                return f"Erreur Ollama: {response.status_code} - {response.text}"

        except requests.exceptions.ConnectionError:
            return "❌ Impossible de se connecter à Ollama. Assurez-vous qu'Ollama est démarré sur localhost:11434"
        except requests.exceptions.ReadTimeout:
            return "⏰ Le système met trop de temps à répondre. Essayez avec une question plus précise."
        except Exception as e:
            return f"❌ Erreur lors de l'appel à Ollama: {str(e)}"

    def _extract_date(self, question: str):
        """Extrait une date au format JJ/MM/AAAA ou AAAA-MM-JJ de la question"""
        match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", question)
        if match:
            try:
                return datetime.strptime(match.group(1), "%d/%m/%Y").date()
            except:
                return None
        match = re.search(r"(\d{4}-\d{2}-\d{2})", question)
        if match:
            try:
                return datetime.strptime(match.group(1), "%Y-%m-%d").date()
            except:
                return None
        return None

    # -------- Appel à Ollama ---------

    def _ask_ollama(self, question, context):
        try:
            prompt = f"""
Tu es un assistant expert en analyse de données pour Yazaki. Tu as accès aux données suivantes:

{context}

Question: {question}

Réponds de manière précise et concise en français. Si les données ne permettent pas de répondre, dis-le.
Utilise les données fournies pour donner une réponse précise.
"""
            payload = {"model": self.model_name, "prompt": prompt, "stream": False}
            response = requests.post(self.ollama_url, json=payload, timeout=120)
            if response.status_code == 200:
                return response.json().get('response', 'Désolé, je n\'ai pas pu générer de réponse.')
            return f"Erreur Ollama: {response.status_code} - {response.text}"
        except requests.exceptions.ConnectionError:
            return "❌ Impossible de se connecter à Ollama. Vérifiez Ollama."
        except requests.exceptions.ReadTimeout:
            return "⏰ Temps de réponse trop long. Essayez une question plus précise."
        except Exception as e:
            return f"❌ Erreur lors de l'appel à Ollama: {str(e)}"
        
    # --- À ajouter dans la classe FAQBot ---
    def handle_analytic_question(self, question: str) -> str:
        """
        Détecte si la question est analytique et envoie un prompt léger à Ollama.
        Exemple : optimisation des stocks, réduction des ruptures, amélioration des KPI.
        """
        q_lower = question.lower()

        # Détection de mots-clés analytiques
        analytic_keywords = [
        "optimiser", "réduire les ruptures", "améliorer la gestion des stocks",
        "améliorer", "comment faire pour", "réduction des ruptures", "gestion des stocks"
        ]

        if any(keyword in q_lower for keyword in analytic_keywords):
        # Préparer un contexte léger pour éviter les timeouts
            context = "Résumé des KPI disponibles:\n"
            context += f"- Valeur totale du stock: {valeur_stock()} MAD\n"
            context += f"- Produits en rupture: {len(produits_en_rupture())}\n"
            context += f"- Taux de livraison à temps: {taux_livraison()} %\n"
            context += f"- Commandes en retard: {len(commandes_en_retard())}\n"
            context += f"- Produits à réapprovisionner: {len(produits_a_reapprovisionner())}\n"

        # Envoi à Ollama
            return self._ask_ollama(
                question=f"{question}\nDonne une réponse analytique et des recommandations concrètes.",
                context=context
        )

    # Retourne None si ce n'est pas une question analytique
        return None


    # --------- Fonction principale ask ----

    def ask(self, question: str) -> str:
        q = question.lower()
        date_filter = self._extract_date(question)

    # ---------------- Produits ----------------
    # Fournisseur principal
        if any(keyword in q for keyword in ["fournisseur principal", "fournisseur du produit", "fournisseur principal du produit", "qui fournit", "fournisseur de"]):
            match = re.search(r"([A-Za-z0-9]+)\s*$", q.strip())
            if match:
                ref = match.group(1).upper()
                info = get_produit_info(ref)
                if isinstance(info, str):
                    return info
                return f" Fournisseur principal de {ref} : {get_fournisseur_principal(ref)}"

    # Famille/catégorie 
        if any(keyword in q for keyword in ["famille", "catégorie", "type de produit","Famille du produit"]):
            match = re.search(r"(?:famille|catégorie|type).*?produit.*?([A-Za-z0-9]+(?:\s+[A-Za-z0-9]+)*)", q)
            if match:
                ref = match.group(1).upper().replace(" ", "")
                return f" Famille du produit {ref} : {get_famille_produit(ref)}"

    # Coût/prix
        if any(keyword in q for keyword in ["Cout unitaire du produit","coût", "prix", "cout", "combien coûte"]):
            match = re.search(r"([A-Za-z0-9]+)\s*$", q.strip())
            if match:
                ref = match.group(1).upper()
                info = get_produit_info(ref)
                if isinstance(info, str):  # Produit non trouvé
                    return info
                return f" Coût unitaire de {ref} : {get_cout_unitaire(ref)}"


    # Délai de livraison
        match = None
        if any(keyword in q for keyword in ["délai de livraison du produit","délai de livraison", "delai", "temps de livraison"]):
            match = re.search(r"([A-Za-z0-9]+)\s*$", q.strip())
            if match:
                ref = match.group(1).upper()
                info = get_produit_info(ref)
                if isinstance(info, str):
                    return info
                return f" Délai de livraison de {ref} : {get_delai_livraison(ref)} jours"

    # Seuil de réapprovisionnement
        if any(keyword in q for keyword in [" Seuil de réapprovisionnement du produit "," Seuil de réappro du produit ","seuil de réappro", "seuil de reappro", "seuil de réapprovisionnement","seuil", "réapprovisionnement minimum"]):
            match = re.search(r"([A-Za-z0-9]+)\s*$", q.strip())
            if match:
                ref = match.group(1).upper()  # Normalisation
                info = get_produit_info(ref)
                if isinstance(info, str):  # Produit non trouvé
                    return info
                return f" Seuil de réapprovisionnement du produit {ref} : {get_seuil_reappro(ref)}"

    # Poids unitaire
        if any(keyword in q for keyword in ["Poids unitaire du produit ","poids", "poids unitaire"]):
            match = re.search(r"([A-Za-z0-9]+)\s*$", q.strip())
            if match:
                ref = match.group(1).upper()  # Normalisation
                info = get_produit_info(ref)
                if isinstance(info, str):  # Produit non trouvé
                    return info
                return f" Poids unitaire du produit {ref} : {get_poids_unitaire(ref)}"

    # Liste des produits d’une famille
        if any(keyword in q for keyword in ["liste des produits par la famille","liste des produits", "produits du la famille", "produits dans la famille"]):
            match = re.search(r"([A-Za-z0-9]+)\s*$", q.strip())
            if match:
                fam = match.group(1).strip()
                result = list_produits_par_famille(fam)
                return f" Produits de la famille {fam} :{result}"

    # Produit le plus cher
        if any(keyword in q for keyword in ["produits les plus cher", "les produits les plus cher","plus cher", "coût maximum"]):
            return f" Produit le plus cher : {produit_plus_cher()}"

    # Liste des familles
        if any(keyword in q for keyword in ["liste des familles", "quelles familles", "familles disponibles"]):
            return f" Familles disponibles : {list_familles()}"

    # Produits par famille (détails complets)
        if any(keyword in q for keyword in ["détails famille", "infos famille", "les produits de la famille"]):
            match = re.search(r"([A-Za-z0-9]+)\s*$", q.strip())
            if match:
                fam = match.group(1).strip()
                produits = produits_par_famille(fam)
                if not produits:
                    return f"⚠ Aucun produit trouvé pour la famille {fam}."
                if isinstance(produits, pd.DataFrame):
                    refs = ", ".join(produits['Référence_Produit'].tolist())
                else:  # Si c'est déjà une liste de dicts
                    refs = ", ".join([p['Référence_Produit'] for p in produits])
                return f" Produits de la famille {fam} : {refs}"

    # ---------------- Commandes ----------------
        # Contrepartie 
        if any(keyword in q for keyword in [" la contrepartie de la commande","contrepartie", "client", "fournisseur", "qui a commandé"]):
            match = re.search(r"([A-Za-z0-9]+)\s*$", q.strip())
            if match:
                num = match.group(1).upper()
                info = get_contrepartie(num)
                if isinstance(info, str):
                    return info
                return f" Contrepartie de la commande {num} : {get_contrepartie(num)}"

        # Statut 
        if any(keyword in q for keyword in [" le statut de commande","statut de commande", "statut", "état", "avancement", "situation", "où en est"]):
            match = re.search(r"([A-Za-z0-9]+)\s*$", q.strip())
            if match:
                num = match.group(1).upper()
                info = get_statut_commande(num)
                if isinstance(info, str):
                    return info
                return f" Statut de la commande {num} : {get_statut_commande(num)}"

        # Quantité 
        if any(keyword in q for keyword in ["la quantité de commande","la quantité de commande","quantité de commande","quantité", "nombre", "combien", "nb articles"]):
            match = re.search(r"([A-Za-z0-9]+)\s*$", q.strip())
            if match:
                num = match.group(1).upper()
                info = get_quantite_commande(num)
                if isinstance(info, str):
                    return info
                return f" Quantité de la commande {num} : {get_quantite_commande(num)}"

        # Type de commande 
        if any(keyword in q for keyword in ["le type de commande"," le type de la commande","type", "catégorie", "nature"]):
            match = re.search(r"(?:type|catégorie|nature).*?commande.*?([A-Za-z0-9]+(?:\s+[A-Za-z0-9]+)*)", q)
            if match:
                num = match.group(1).upper().replace(" ", "")
                info = get_type_commande(num) 
                if isinstance(info, str):
                    return info
                return f" Type de la commande {num} : {get_type_commande(num)}"

        # Livraison prévue 
        if any(keyword in q for keyword in ["la date de livraison prevue de la commande"," date de livraison prévue de commande","livraison prévue", "date prévue pour la livraison de commande","date prévue pour la livraison de","date prévue", "quand sera livré", "quand est prévue"]):
            match = re.search(r"([A-Za-z0-9]+)\s*$", q.strip())
            if match:
                num = match.group(1).upper()
                info = get_date_livraison_prevue(num)
                if isinstance(info, str):
                    return info
                return f" Livraison prévue de la commande {num} : {get_date_livraison_prevue(num)}"

        # Livraison réelle
        if any(keyword in q for keyword in ["livraison réelle de commande","livraison reelle de commande","livraison réelle", "livraison effectuée", "date réelle", "quand a été livré"]):
            match = re.search(r"([A-Za-z0-9]+)\s*$", q.strip())
            if match:
                num = match.group(1).upper()
                info = get_date_livraison_reelle(num)
                if isinstance(info, str):
                    return info
                return f" Livraison réelle de {num} : {get_date_livraison_reelle(num)}"

        # Commandes en retard 
        if any(keyword in q for keyword in ["commandes en retard", "retard de commande", "commandes qui sont en retard", 
                                       "quelles commandes sont en retard", "liste des commandes en retard"]):
            info = commandes_en_retard() 
            if isinstance(info, str):
                return info
            return f"⏰ Commandes en retard : {commandes_en_retard()+"\n"}"
        
        # Commandes par produit
        if any(keyword in q for keyword in ["donner les commandes du produit","commandes du produit", "commandes pour le produit", "quel produit"]):
            match = re.search(r"produit\s+([A-Za-z0-9]+)", q, re.IGNORECASE)
            if match:
                ref = match.group(1).upper()
                info = commandes_par_produit(ref)
                if isinstance(info, str):
                    return info
                # Formatage en texte lisible
                lignes = [
                    f"📦 {ligne['Type_Commande']} {ligne['Num_Commande']} (Qté: {ligne['Quantité']}, Contrepartie: {ligne['Contrepartie']})"
                    for ligne in info
                ]
                return f"📦 Commandes pour le produit {ref} :\n" + "\n".join(lignes)

                # Commandes par type (Client / Fournisseur)
        if any(keyword in q for keyword in ["commandes client", "commandes fournisseur", "type de commande"]):
            match = re.search(r"(client|fournisseur)", q, re.IGNORECASE)
            if match:
                type_commande = match.group(1).capitalize()
                info = commandes_par_type(type_commande)
                if isinstance(info, str):
                    return info
                # Formatage en texte lisible
                lignes = [
                    f"📦 {ligne['Type_Commande']} {ligne['Num_Commande']} ({ligne['Référence_Produit']}, Qté: {ligne['Quantité']}, Contrepartie: {ligne['Contrepartie']})"
                    for ligne in info
                ]
                return f"📦 Commandes de type {type_commande} :\n" + "\n".join(lignes)

        
      # --- Détails complets d'une commande pour un client ---
        q = q.lower()
        if any(keyword in q for keyword in ["donner en détail la commande de","donner les commandes du produit","commandes du produit","commandes pour le produit","quel produit"]):
            # Extraire le code client
            match = re.search(r"donner en détail la commande de\s+([A-Za-z0-9]+)", q, re.IGNORECASE)
            if match:
                client = match.group(1).upper()

                if 'Num_Commande' not in commandes_global.columns:
                    return "❌ La colonne 'Num_Commande' n'existe pas dans les commandes."

                # Filtrer toutes les commandes de ce client
                commandes_client = commandes_global[
                commandes_global['Num_Commande'].str.strip().str.upper().str.contains(client)
                ]

                if commandes_client.empty:
                    return f"❌ Aucune commande trouvée pour le client {client}."

                # Construire un texte détaillé
                details = []
                for idex, ligne in commandes_client.iterrows():
                    details.append(
                        f"📦 Commande {ligne.get('Num_Commande', 'N/A')} :\n "
                        f"Produit {ligne.get('Référence_Produit', 'N/A')} \n, "
                        f"Quantité: {ligne.get('Quantité', 'N/A')} \n, "
                        f"Statut: {ligne.get('Statut_Commande', 'N/A')} \n, "
                        f"Type: {ligne.get('Type_Commande', 'N/A')} \n, "
                        f"Livraison prévue: {ligne.get('Date_Livraison_Prévue', 'N/A')}\n, "
                        f"Livraison réelle: {ligne.get('Date_Livraison_Réelle', 'N/A')}\n,"
                        f"Contrepartie : {ligne.get('Contrepartie', 'N/A')}")
                return "\n".join(details)

    # ---------------- Stock ----------------
       # --- Stock initial ---
        if any(keyword in q for keyword in ["le stock initial", "le stock initial du produit", "stock initial du produit","quel est le stock initial du produit", "stock au départ", "stock début", "stock de départ"]):
            match = re.search(r"(?:de|du|d['’])\s*([A-Za-z0-9]+)", q, re.IGNORECASE)
            if match:
                ref = match.group(1).upper().replace(" ", "")
                result = get_stock_initial(ref, date_filter)
                if isinstance(result, str):  # si la fonction renvoie un message d'erreur
                    return result
                date_str = f" au {date_filter}" if date_filter else ""
                return f" Stock initial de {ref}{date_str} : {result}"
            else:
                return " Référence produit introuvable dans la question."



        # --- Stock final ---
        if any(keyword in q for keyword in ["stock final du produit", "stockfin", "stock fin"]):
            match = re.search(r"(?:de|du|d['’])\s*([A-Za-z0-9]+)", q, re.IGNORECASE)
            if match:
                ref = match.group(1).upper()
                stock = get_stock_final(ref, date_filter)
                if isinstance(stock, str):
                    return stock
                date_str = f" au {date_filter}" if date_filter else ""
                return f" Stock final de {ref}{date_str} : {stock}"
            else:
                return " Référence produit non détectée dans la question."


        # --- Produits en rupture ---
        if "produits en rupture" in q:
            result = produits_en_rupture()
            # Si result est une chaîne (tous les produits déjà formatés)
            return f" Produits en rupture :\n{result}"

        # --- Produits urgents ---
        if any(keyword in q for keyword in ["Quels sont les produits urgents","donner les produits urgents","produits urgents", "stocks urgents", "réapprovisionnement urgent"]):
            result = produits_urgents(date=date_filter)
            return f" Produits urgents :\n{result}"
        
        # --- Évolution stock ---
        if any(keyword in q for keyword in ["l'évolution du stock pour le produit","donner l'évolution du stock du ","quel est l'évolution du stock","évolution du stock", "historique du stock", "suivi du stock", "stock passé"]):
        # Extraire la référence depuis la question
            match = re.search(r"(?:stock.*?)([A-Za-z0-9]+)", q)
            if match:
                ref = match.group(1).upper().strip()
                result = evolution_stock(ref)
                return f"📊 Évolution du stock pour {ref} :\n{result}"
            else:
                return "❌ Merci de préciser une référence produit (ex: évolution du stock P001)."


    # ---------------- Informations complètes ----------------

        if any(keyword in q for keyword in ["de toutes les informations", "toutes les informations","infos complètes", "détails complets", "tous les détails"]):
        # Cas spécifiques rupture
            if "produits en rupture" in q:
                result = produits_en_rupture(date=date_filter)
                return f"⚠ Produits en rupture : {result}"

        # Cas spécifiques urgents
            if "produits urgents" in q:
                result = produits_urgents(date=date_filter)
                return f"⚠ Produits urgents : {result}"

        # Recherche de la référence produit
            match = re.search(r"(?:toutes les informations de|infos complètes de|détails complets de|tous les détails de).*?([A-Za-z0-9]+)",q)
            if not match:
                match = re.search(r"produit.*?([A-Za-z0-9]{4})$", q)

            if match:
                ref = match.group(1).upper().replace(" ", "")
                date_str = f" le {date_filter}" if date_filter else ""

                infos = {
                    "Fournisseur": get_fournisseur_principal(ref),"\n"
                    "Famille": get_famille_produit(ref),"\n"
                    "Coût unitaire": get_cout_unitaire(ref),"\n"
                    "Stock initial": get_stock_initial(ref, date_filter),"\n"
                    "Stock final": get_stock_final(ref, date_filter),"\n"
                    "Évolution stock": evolution_stock(ref)
                }

                return " Informations complètes du produit {}{} :\n{}".format(ref, date_str, "\n".join(f"{k}: {v}" for k, v in infos.items()))

            return "❌ Référence produit introuvable dans la question."

        
    # Détection et traitement des questions analytiques
        analytic_response = self.handle_analytic_question(question)
        if analytic_response:
            return analytic_response
    # ---------------- KPI ----------------
        if any(keyword in q for keyword in ["valeur du stock total","valeur du stock", "valeur totale", "montant du stock"]):
            result = valeur_stock(date=date_filter)
            return f"💰 Valeur totale du stock : {result} MAD"

        if any(keyword in q for keyword in ["taux de livraison", "pourcentage livraison", "livraison à temps"]):
            result = taux_livraison(date=date_filter)
            return f"🚚 Taux de livraison à temps : {result}%" if result is not None else "🚚 Pas de données disponibles"

        if any(keyword in q for keyword in ["produits à réapprovisionner", "réapprovisionnement nécessaire", "besoin de réappro"]):
            result = produits_a_reapprovisionner(date=date_filter)
            return f"📦 Produits à réapprovisionner : {result}"

        if any(keyword in q for keyword in ["commandes pour les clients","commandes des clients","commandes clients", "commandes des clients"]) and "ce mois" in q:
            return f"🛒 Commandes clients ce mois : {commandes_clients_ce_mois(self.commandes)}"

        q_lower = q.lower()
        if any(keyword in q_lower for keyword in ["commandes pour les fournisseurs","commandes des fournisseurs","commandes fournisseurs","commandes fournisseurs ce mois","commandes fournisseurs pour ce mois", "commandes fournisseurs de ce mois","commandes aux fournisseurs"]):
            return f"📦 Commandes fournisseurs ce mois : {commandes_fournisseurs_ce_mois(self.commandes)}"
        elif any(keyword in q_lower for keyword in ["commandes pour les fournisseurs","commandes des fournisseurs","commandes fournisseurs","commandes aux fournisseurs"]):
            return f"📦 Total commandes fournisseurs : {len(self.commandes[self.commandes['Type_Commande'].str.lower() == 'fournisseur'])}"

        if "stock total" in q and "ce mois" in q:
            return f"📊 Stock total disponible ce mois : {stock_total_ce_mois(self.stock)}"

    # ---------------- Stock total par produit ----------------
        if any(keyword in q for keyword in ["donner le stock total de produit","donner le stock total","stock total de produit","stock total", "stock complet", "quantité totale"]):
            match = re.search(r"stock total.*produit.*?([A-Za-z0-9]+)", q)  
            if match:
                ref = match.group(1).upper().replace(" ", "")
                result = stock_total_produit(ref, self.stock, date=date_filter)
                return f"📊 Stock total du produit {ref} : {result}"

    # ---------------- Sinon → Ollama ----------------
        context = self._prepare_data_context()
        return self._ask_ollama(question, context)
    # -------------------------------------------------
    def normaliser_reference(ref):
        """Normalise une référence produit (majuscules, sans espaces)"""
        if isinstance(ref, str):
            return ref.upper().strip().replace(" ", "")
        return ref
    
# Configuration de l'application Streamlit
st.set_page_config(
    page_title=" Assistant IA - Yazaki",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour améliorer l'interface
st.markdown("""
<style>


    /* Police globale pour tout le document */
    * {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", system-ui, sans-serif;
    }

    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", system-ui, sans-serif;
        font-weight: 600;
    }
    .chat-container {
        background-color: transparent;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        max-height: 600px;
        overflow-y: auto;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", system-ui, sans-serif;
    }
    .user-message {
        background-color: #c41e3a;
        color: white;
        border-radius: 15px;
        padding: 10px 15px;
        margin: 5px 0;
        max-width: 80%;
        margin-left: auto;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", system-ui, sans-serif;
    }
    .assistant-message {
        background-color: #E8F5E9;
        color: #333;
        border-radius: 15px;
        padding: 10px 15px;
        margin: 5px 0;
        max-width: 80%;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", system-ui, sans-serif;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", system-ui, sans-serif;
    }
    .new-chat-btn {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 10px 15px;
        margin: 10px 0;
        width: 100%;
        cursor: pointer;
        font-weight: bold;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", system-ui, sans-serif;
    }
    .history-item {
        padding: 8px 12px;
        margin: 5px 0;
        border-radius: 5px;
        cursor: pointer;
        background-color: #e9ecef;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", system-ui, sans-serif;
    }
    .history-item:hover {
        background-color: #dee2e6;
    }
    .stButton button {
        width: 100%;
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", system-ui, sans-serif;
    }
    .sidebar-logo {
        display: block;
        margin: 0 auto 1.5rem auto;
        max-width: 80%;
        height: auto;
        border-radius: 10px;
        opacity: 0.9;
        transition: opacity 0.3s ease;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
        background: linear-gradient(145deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05));
        padding: 8px;
    }
    .sidebar-logo:hover {
        opacity: 1;
        transform: scale(1.02);
    }
</style>

""", unsafe_allow_html=True)

# Initialisation des états de session
if "chats" not in st.session_state:
    st.session_state.chats = charger_historique()

# Toujours commencer avec un chat principal vide
if "current_chat" not in st.session_state:
    st.session_state.current_chat = "default"
    
    # Créer un nouveau chat principal vide pour cette session
    st.session_state.chats["default"] = {
        "messages": [],
        "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "title": "Chat Principal (Session actuelle)"
    }

if "show_new_chat" not in st.session_state:
    st.session_state.show_new_chat = False

# Titre principal
st.markdown('<h1 class="main-header"> Salut ! Comment puis-je vous aider ?</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center;">Plus votre question est claire, plus la réponse sera exacte.😊</p>', unsafe_allow_html=True)

# Initialisation du bot
try:
    bot = FAQBot()
    # Vérification du chargement des données
    if bot.produits.empty and bot.stock.empty and bot.commandes.empty:
        st.error("❌ Aucune donnée n'a pu être chargée. Vérifiez les fichiers dans le dossier data")
    
except Exception as e:
    st.error(f"❌ Erreur lors de l'initialisation du bot: {e}")
    st.stop()

#--------------logo pour sidebar --------
with st.sidebar:
    try:
        logo_url = "https://upload.wikimedia.org/wikipedia/de/thumb/d/da/Yazaki_Group_Logo.svg/1200px-Yazaki_Group_Logo.svg.png?20120719175411"
        st.markdown(f'<img src="{logo_url}" class="sidebar-logo">', unsafe_allow_html=True)
    except:
        st.markdown('<div class="sidebar-logo" style="text-align:center; padding:15px;"><h3>YAZAKI</h3></div>',
                    unsafe_allow_html=True)

# Sidebar avec historique et configuration
with st.sidebar:
    if st.button("📝 Nouveau Chat", key="new_chat_btn", help="Créer un nouveau chat", use_container_width=True):
    # Sauvegarder l'ancien chat principal dans l'historique
        if "default" in st.session_state.chats and st.session_state.chats["default"]["messages"]:
        # Créer un ID unique pour l'ancien chat
            old_chat_id = f"chat_{int(time.time())}"
            st.session_state.chats[old_chat_id] = st.session_state.chats["default"].copy()
            st.session_state.chats[old_chat_id]["title"] = f"Ancien chat du {datetime.now().strftime('%d/%m %H:%M')}"    
    # Réinitialiser le chat principal
        st.session_state.chats["default"] = {
            "messages": [],
            "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "title": "Chat Principal (Session actuelle)"
    }
    
    # Forcer le chat principal comme courant
        st.session_state.current_chat = "default"
        sauvegarder_historique(st.session_state.chats)
        st.rerun()

    # Vérification Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
    except requests.exceptions.ConnectionError:
        pass
    except Exception as e:
        pass

# Conteneur de chat avec défilement
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Affichage des messages de la conversation actuelle
    for message in st.session_state.chats[st.session_state.current_chat]["messages"]:
        if message["role"] == "user":
            st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="assistant-message"> {message["content"]}</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Entrée utilisateur
if prompt := st.chat_input("💬 Posez votre question ici..."):
    # Ajout du message utilisateur à la conversation actuelle
    st.session_state.chats[st.session_state.current_chat]["messages"].append({"role": "user", "content": prompt})
    
    # Génération de la réponse
    with st.spinner("🤖 L'assistante Yazaki analyse les données..."):
        reponse = bot.ask(prompt)
    
    # Ajout de la réponse à la conversation actuelle
    st.session_state.chats[st.session_state.current_chat]["messages"].append({"role": "assistant", "content": reponse})

    # Sauvegarder l’historique sur disque
    sauvegarder_historique(st.session_state.chats)

    # Rafraîchir l'affichage
    st.rerun()

# --- Sidebar: Liste des conversations ---
st.sidebar.markdown("### 💬 Conversations")
for chat_id, chat_data in st.session_state.chats.items():
    if chat_id == "default":
        display_name = " Chat Principal"
        is_current = chat_id == st.session_state.current_chat
    else:
        display_name = f" {chat_data.get('title', f'Conversation du {chat_data['created']}')}"
        is_current = False
        
    col1, col2 = st.sidebar.columns([4, 1])
    
    with col1:
        if st.button(display_name, key=f"select_{chat_id}", use_container_width=True):
            st.session_state.current_chat = chat_id
            st.rerun()
    
    with col2:
        if chat_id != "default":
            if st.button("🗑", key=f"delete_{chat_id}", help="Supprimer la conversation entière"):
                # Gestion de confirmation
                if st.session_state.get(f"confirm_delete_{chat_id}", False):
                    if chat_id == st.session_state.current_chat:
                        st.session_state.current_chat = "default"
                    del st.session_state.chats[chat_id]
                    sauvegarder_historique(st.session_state.chats)
                    st.rerun()
                else:
                    st.session_state[f"confirm_delete_{chat_id}"] = True
                    st.warning(f"Cliquer une autre fois pour confirmer la suppression {display_name} 🗑")
        else:
            st.button("🔒", key=f"lock_{chat_id}", disabled=True, help="Chat principal - ne peut pas être supprimé")
    
    # Indiquer visuellement le chat sélectionné
    if chat_id == st.session_state.current_chat:
        st.sidebar.markdown(
            f"<div style='color:#c41e3a; font-weight:bold; padding:4px; background-color:#e3f2fd; border-radius:6px; border:1px solid #1E88E5;'>→ {display_name}</div>",
            unsafe_allow_html=True
        )

st.sidebar.markdown("---")

# --- Boutons de contrôle pour la conversation actuelle ---
st.sidebar.markdown("<div style='text-align:center;'>", unsafe_allow_html=True)

# Vider les messages de la conversation actuelle
if st.sidebar.button("🧹 Vider cette conversation", use_container_width=True, help="Effacer tous les messages de cette conversation"):
    st.session_state.chats[st.session_state.current_chat]["messages"] = []
    sauvegarder_historique(st.session_state.chats)
    st.success("Messages effacés !")
    st.rerun()
st.sidebar.markdown("</div>", unsafe_allow_html=True)

with st.sidebar:
    st.header(" Aperçu des données")

    if not bot.produits.empty:
        with st.expander("📦 Produits"):
            st.write(f"Lignes: {len(bot.produits)}")
            st.write("Colonnes:", list(bot.produits.columns))
            st.dataframe(bot.produits, use_container_width=True)

    if not bot.stock.empty:
        with st.expander("📊 Stock"):
            st.write(f"Lignes: {len(bot.stock)}")
            st.write("Colonnes:", list(bot.stock.columns))
            if 'Date' in bot.stock.columns:
                st.write(f"Période: {bot.stock['Date'].min()} au {bot.stock['Date'].max()}")
            st.dataframe(bot.stock, use_container_width=True)

    if not bot.commandes.empty:
        with st.expander("💰 Commandes"):
            st.write(f"Lignes: {len(bot.commandes)}")
            st.write("Colonnes:", list(bot.commandes.columns))
            if 'Date' in bot.commandes.columns:
                st.write(f"Période: {bot.commandes['Date'].min()} au {bot.commandes['Date'].max()}")
            st.dataframe(bot.commandes, use_container_width=True)

# Footer avec statut
st.sidebar.markdown("---")
st.sidebar.caption(f"Modèle actuel: {bot.model_name}")
st.sidebar.caption(f"Conversations: {len(st.session_state.chats)} • Messages: {sum(len(chat['messages']) for chat in st.session_state.chats.values())}")





