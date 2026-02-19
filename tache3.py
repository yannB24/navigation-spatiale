import json
import os
def charger_json_securise(chemin):
    try:
        with open(chemin, 'r', encoding='utf-8') as f:
            data = json.load(f)  
        # Petite condition pour afficher le bon message si c'est le fichier missions
        if isinstance(data, dict) and "missions" in data:
            print(f"[OK] {chemin} chargé avec succès ({len(data['missions'])} missions)")
        else:
            print(f"[OK] {chemin} chargé avec succès")       
        return data   
    except FileNotFoundError:
        print(f"[ERREUR] {chemin} — Fichier introuvable.")
        return None
    except json.JSONDecodeError as e:
        print(f"[ERREUR] {chemin} — Format JSON invalide : {e}")
        return None
    except PermissionError:
        print(f"[ERREUR] {chemin} — Accès refusé.")
        return None
    except Exception as e:
        # Fallback pour toute autre erreur non prévue
        print(f"[ERREUR] {chemin} — Erreur inattendue : {e}")
        return None
if __name__ == '__main__':
    # Création rapide du fichier corrompu juste pour le test
    chemin_corrompu = "space_data/corrompu.json"
    if not os.path.exists(chemin_corrompu):
        with open(chemin_corrompu, "w", encoding="utf-8") as f:
            f.write("Ceci n'est pas du JSON valide, ça va planter.")
    # Exécution des 3 cas 
    data1 = charger_json_securise("space_data/missions.json")
    data2 = charger_json_securise("space_data/fantome.json")
    data3 = charger_json_securise("space_data/corrompu.json")