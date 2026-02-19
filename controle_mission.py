import json
from astro_utils import distance_3d, alerte_systeme

def analyser_telemetrie():
    try:
        # Chargement des deux fichiers nécessaires
        with open('space_data/telemetrie.json', 'r', encoding='utf-8') as f:
            telemetrie = json.load(f)
            
        with open('space_data/config_systeme.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        releves = telemetrie.get('releves', [])
        seuils = config.get('seuils_alerte', {})
        vaisseau = telemetrie.get('vaisseau', 'Inconnu')
        
        print(f"=== Analyse de télémétrie — {vaisseau} ===\n")
        
        # Calcul et affichage des distances parcourues entre chaque relevé
        for i in range(1, len(releves)):
            pos_precedente = releves[i-1]['position_km']
            pos_actuelle = releves[i]['position_km']
            
            distance = distance_3d(pos_precedente, pos_actuelle)
            # Affichage avec séparateur de milliers et 1 décimale
            print(f"Relevé {i} → {i+1} : Distance parcourue = {distance:,.1f} km")
            
        print("\n=== Alertes détectées ===")
        
        # Analyse des alertes pour chaque relevé
        for releve in releves:
            alertes = alerte_systeme(releve, seuils)
            if alertes:
                timestamp = releve.get('timestamp')
                for alerte in alertes:
                    print(f"[{timestamp}] ⚠️  {alerte}")
                    
    except FileNotFoundError as e:
        print(f"Erreur d'accès aux fichiers de données : {e}")

if __name__ == '__main__':
    analyser_telemetrie()