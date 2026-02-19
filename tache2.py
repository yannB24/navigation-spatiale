import os
import json

def preparer_arborescence():
    config_path = 'space_data/config_systeme.json'
    base_dir = 'space_data'
    
    try:
        # On charge les chemins depuis le fichier de config
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        repertoires = config.get('repertoires', {})
        
        print("Vérification de l'arborescence du centre de contrôle...")
        
        # Parcours et création des répertoires s'ils manquent
        for nom, chemin in repertoires.items():
            if os.path.exists(chemin):
                print(f"  [✓] {chemin} — existe déjà")
            else:
                os.makedirs(chemin)
                print(f"  [+] {chemin} — créé")
                
        print(f"\nContenu de {base_dir}/ :")
        
        # Lecture du dossier parent pour afficher l'arborescence finale
        # os.listdir récupère tout, on trie ensuite si c'est un dossier ou un fichier
        for element in os.listdir(base_dir):
            chemin_complet = os.path.join(base_dir, element)
            
            if os.path.isdir(chemin_complet):
                print(f"  📁 {element}/")
            elif os.path.isfile(chemin_complet):
                print(f"  📄 {element}")
                
    except FileNotFoundError:
        print(f"Erreur : impossible de trouver {config_path}")
    except json.JSONDecodeError:
        print("Erreur : le fichier config_systeme.json est mal formaté.")

if __name__ == '__main__':
    preparer_arborescence()