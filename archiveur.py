import os
import json
import subprocess
from datetime import datetime

def scanner_et_archiver():
    dossier_cible = 'space_data/'
    config_path = 'space_data/config_systeme.json'
    rapport_path = 'space_data/rapports/inventaire.json'

    try:
        # Récupération des extensions depuis la config
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        ext_autorisees = config.get('extensions_autorisees', [])
    except FileNotFoundError:
        print(f"Erreur : {config_path} introuvable.")
        return

    print("=== 🗂️  Scanner de fichiers — Centre de contrôle ===\n")
    print(f"Scan de {dossier_cible}...")

    fichiers_trouves = []
    taille_totale = 0

    # os.walk parcourt l'arborescence récursivement
    for racine, dossiers, fichiers in os.walk(dossier_cible):
        for nom_fichier in fichiers:
            # Séparation du nom et de l'extension
            _, ext = os.path.splitext(nom_fichier)
            
            if ext in ext_autorisees:
                chemin_complet = os.path.join(racine, nom_fichier)
                # Normalisation des barres obliques pour l'affichage (Windows vs Linux)
                chemin_propre = chemin_complet.replace('\\', '/')
                
                # On évite de scanner notre propre fichier d'inventaire
                if chemin_propre == rapport_path:
                    continue
                    
                taille = os.path.getsize(chemin_complet)
                mtime = os.path.getmtime(chemin_complet)
                date_modif = datetime.fromtimestamp(mtime)
                
                taille_totale += taille
                taille_kb = taille / 1024
                date_str = date_modif.strftime('%Y-%m-%d %H:%M')
                
                print(f"  📄 {chemin_propre} ({taille_kb:.1f} KB) — modifié le {date_str}")
                
                fichiers_trouves.append({
                    "chemin": chemin_propre,
                    "taille_octets": taille,
                    "derniere_modification": date_modif.isoformat(),
                    "extension": ext
                })

    # Préparation des données JSON
    inventaire = {
        "date_scan": datetime.now().isoformat(timespec='seconds'),
        "total_fichiers": len(fichiers_trouves),
        "taille_totale_octets": taille_totale,
        "fichiers": fichiers_trouves
    }

    # Sauvegarde du rapport
    os.makedirs(os.path.dirname(rapport_path), exist_ok=True)
    with open(rapport_path, 'w', encoding='utf-8') as f:
        json.dump(inventaire, f, indent=2, ensure_ascii=False)

    taille_totale_kb = taille_totale / 1024
    print(f"\nTotal : {len(fichiers_trouves)} fichiers, {taille_totale_kb:.1f} KB")
    print(f"Inventaire sauvegardé → {rapport_path}")

    # Section Bonus : Archivage
    try:
        print("\n[Bonus] Compression du dossier de sauvegardes en cours...")
        archive_nom = "space_data/backup_archive.tar.gz"
        dossier_a_compresser = "space_data/backups/"
        
        # subprocess lance la commande système silencieusement
        subprocess.run(
            ["tar", "-czf", archive_nom, dossier_a_compresser], 
            check=True, 
            stderr=subprocess.DEVNULL
        )
        print(f"Archive créée avec succès → {archive_nom}")
    except Exception:
        print("Note : L'utilitaire 'tar' n'est pas disponible sur ce système pour le bonus.")

if __name__ == '__main__':
    scanner_et_archiver()