from datetime import datetime

# 1. Définition des exceptions personnalisées
class ErreurTelemetrie(Exception):
    """Exception de base pour les erreurs de télémétrie."""
    pass

class SeuilDepasse(ErreurTelemetrie):
    """Un seuil critique a été franchi."""
    pass

class DonneesManquantes(ErreurTelemetrie):
    """Un champ obligatoire est absent du relevé."""
    pass

class HorodatageInvalide(ErreurTelemetrie):
    """Le timestamp n'est pas au format ISO 8601."""
    pass
# 2. Fonction de validation
def valider_releve(releve, seuils):
    champs_obligatoires = [
        "timestamp", "vitesse_km_s", "carburant_pourcent", 
        "oxygene_pourcent", "temperature_cabine_c"
    ]
    
    # Étape 1 : Vérification des champs manquants
    manquants = [c for c in champs_obligatoires if c not in releve]
    if manquants:
        raise DonneesManquantes(f"Champs manquants: {', '.join(manquants)}")
        
    # Étape 2 : Vérification du timestamp
    ts_str = releve["timestamp"]
    try:
        # Le replace("Z", "+00:00") assure la compatibilité avec fromisoformat
        datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
    except ValueError:
        raise HorodatageInvalide(f'"{ts_str}" n\'est pas un format ISO 8601 valide')
        
    # Étape 3 : Vérification des seuils
    depassements = []
    
    c_actuel = releve["carburant_pourcent"]
    c_min = seuils.get("carburant_min_pourcent", 20.0)
    if c_actuel < c_min:
        depassements.append(f"carburant ({c_actuel}% < seuil {c_min}%)")
        
    o_actuel = releve["oxygene_pourcent"]
    o_min = seuils.get("oxygene_min_pourcent", 85.0)
    if o_actuel < o_min:
        depassements.append(f"oxygene ({o_actuel}% < seuil {o_min}%)")
        
    # S'il y a des dépassements, on lève l'alerte
    if depassements:
        raise SeuilDepasse(", ".join(depassements))
        
    return True

# 3. Zone de test
def tester_releve(nom_test, releve, seuils):
    try:
        valider_releve(releve, seuils)
        # Si c'est valide et qu'on a un timestamp, on l'affiche
        ts = releve.get("timestamp", nom_test)
        print(f"Relevé {ts} → ✅ Valide")
    except ErreurTelemetrie as e:
        # e.__class__.__name__ récupère le nom exact de l'exception (ex: SeuilDepasse)
        print(f"Relevé {nom_test} → ❌ {e.__class__.__name__} : {e}")

if __name__ == '__main__':
    # Configuration simulée pour le test
    seuils_test = {
        "carburant_min_pourcent": 20.0,
        "oxygene_min_pourcent": 85.0
    }
    
    # Données de test fournies par l'énoncé
    releve_valide = {
        "timestamp": "2026-03-18T12:00:00Z", "vitesse_km_s": 1.2,
        "carburant_pourcent": 42.1, "oxygene_pourcent": 91.8,
        "temperature_cabine_c": 17.8
    }
    releve_incomplet = {
        "timestamp": "2026-03-18T12:00:00Z", "vitesse_km_s": 1.2
    }
    releve_mauvaise_date = {
        "timestamp": "pas-une-date", "vitesse_km_s": 1.2,
        "carburant_pourcent": 42.1, "oxygene_pourcent": 91.8,
        "temperature_cabine_c": 17.8
    }
    releve_critique = {
        "timestamp": "2026-03-19T06:00:00Z", "vitesse_km_s": 1.0,
        "carburant_pourcent": 15.0, "oxygene_pourcent": 82.0,
        "temperature_cabine_c": 17.0
    }

    # Exécution des tests
    tester_releve("valide", releve_valide, seuils_test)
    tester_releve("incomplet", releve_incomplet, seuils_test)
    tester_releve("mauvaise date", releve_mauvaise_date, seuils_test)
    tester_releve("critique", releve_critique, seuils_test)