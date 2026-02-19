import json
def load_missions():
    filepath = 'space_data/missions.json'
    
    try:
        # Ouvrons le fichier JSON en lecture
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Faisons une extraction de la liste des missions
        missions = data.get('missions', [])
        
        print("=== Centre de contrôle — Missions enregistrées ===")
        print(f"Total : {len(missions)} missions\n")
        
        # Faisons un affichage formaté pour chaque mission
        for m in missions:
            print(f"[{m['id']}] {m['nom']} → {m['destination']} (statut: {m['statut']})")
            
    except FileNotFoundError:
        print(f"Erreur : le fichier {filepath} est introuvable.")
    except Exception as e:
        print(f"Une erreur est survenue : {e}")

if __name__ == '__main__':
    load_missions()
   
