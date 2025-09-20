import json
import os

HISTORIQUE_FILE = "historique.json"

def charger_historique():
    """Charge l'historique depuis un fichier JSON"""
    if os.path.exists(HISTORIQUE_FILE):
        with open(HISTORIQUE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def sauvegarder_historique(historique):
    """Sauvegarde l'historique dans un fichier JSON"""
    with open(HISTORIQUE_FILE, "w", encoding="utf-8") as f:
        json.dump(historique, f, indent=4, ensure_ascii=False)
