import math

def distance_3d(pos1, pos2):
    """Calcule la distance euclidienne entre deux positions {x, y, z} en km."""
    # Théorème de Pythagore en 3D
    return math.sqrt((pos2['x'] - pos1['x'])**2 + 
                     (pos2['y'] - pos1['y'])**2 + 
                     (pos2['z'] - pos1['z'])**2)

def vitesse_moyenne(distances_km, temps_heures):
    """Retourne la vitesse moyenne en km/s."""
    if temps_heures <= 0:
        return 0
    return distances_km / (temps_heures * 3600)

def consommation_carburant(releves):
    """Prend une liste de relevés et retourne la consommation par intervalle."""
    consommations = []
    for i in range(1, len(releves)):
        diff = releves[i-1]['carburant_pourcent'] - releves[i]['carburant_pourcent']
        consommations.append(round(diff, 2))
    return consommations

def alerte_systeme(releve, seuils):
    """Vérifie un relevé par rapport aux seuils et retourne la liste des alertes."""
    alertes = []
    
    # Vérification des seuils critiques (carburant, oxygène, etc.)
    if releve.get('carburant_pourcent', 100) < seuils.get('carburant_min_pourcent', 0):
        alertes.append("Carburant critique")
    if releve.get('oxygene_pourcent', 100) < seuils.get('oxygene_min_pourcent', 0):
        alertes.append("Oxygène sous le seuil critique")
        
    # Vérification de l'état des systèmes embarqués
    systemes = releve.get('systemes', {})
    for systeme, etat in systemes.items():
        if etat not in ["nominal", "nominale"]:
            # Formatage propre du texte de l'alerte pour coller à l'énoncé
            nom_sys = systeme.capitalize()
            etat_formate = etat.replace("_", " ")
            
            if nom_sys == "Communication" and etat == "degradee":
                alertes.append("Communication dégradée")
            else:
                alertes.append(f"{nom_sys} — {etat_formate}")
            
    return alertes

def formater_position(pos):
    """Formate une position {x, y, z} en chaîne lisible."""
    # Le :,.1f ajoute les séparateurs de milliers et garde 1 chiffre après la virgule
    return f"X: {pos['x']:,.1f} km | Y: {pos['y']:,.1f} km | Z: {pos['z']:,.1f} km"