import os
import time
from datetime import datetime

class LogMission:
    """Gestionnaire de contexte pour écrire des logs de mission horodatés."""

    def __init__(self, mission_id, dossier_logs="space_data/logs/"):
        self.mission_id = mission_id
        self.dossier_logs = dossier_logs
        self.filepath = os.path.join(self.dossier_logs, f"{self.mission_id}.log")
        self.erreurs = 0
        self.start_time = 0
        self.fichier = None
        
        # S'assure que le dossier existe
        os.makedirs(self.dossier_logs, exist_ok=True)

    def __enter__(self):
        # Ouvre le fichier en mode ajout ('a' pour append)
        self.fichier = open(self.filepath, 'a', encoding='utf-8')
        self.start_time = time.time()
        
        maintenant = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # En-tête de session
        self.fichier.write("========================================\n")
        self.fichier.write(f"SESSION OUVERTE — {maintenant}\n")
        self.fichier.write(f"Mission : {self.mission_id}\n")
        self.fichier.write("========================================\n")
        
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Gestion des exceptions s'il y a eu un crash dans le bloc 'with'
        if exc_type is not None:
            self.erreurs += 1
            maintenant = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.fichier.write(f"[{maintenant}] [CRITICAL] Exception capturée : {exc_type.__name__} — {exc_val}\n")
            
        duree = time.time() - self.start_time
        maintenant = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Pied de session
        self.fichier.write("========================================\n")
        self.fichier.write(f"SESSION FERMÉE — {maintenant}\n")
        self.fichier.write(f"Durée : {duree:.3f}s | Erreurs : {self.erreurs}\n")
        self.fichier.write("========================================\n")
        
        # Fermeture propre et indispensable
        self.fichier.close()
        
        # On retourne False pour propager l'erreur (le script plantera mais le log sera sauvegardé)
        return False

    def ecrire(self, niveau, message):
        maintenant = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fichier.write(f"[{maintenant}] [{niveau}] {message}\n")


if __name__ == '__main__':
    # Test 1 : Exécution normale
    print("Test 1 : Session normale en cours...")
    with LogMission("MSN-001") as log:
        log.ecrire("INFO", "Début de la séquence d'approche lunaire")
        log.ecrire("INFO", "Activation des rétrofusées")
        log.ecrire("WARNING", "Légère déviation de trajectoire détectée")
        log.ecrire("INFO", "Correction appliquée — retour sur trajectoire nominale")
    print("Test 1 terminé.")

    # Test 2 : Exécution avec plantage volontaire
    print("\nTest 2 : Session avec erreur en cours...")
    try:
        with LogMission("MSN-001") as log:
            log.ecrire("INFO", "Test de communication")
            # On simule un crash
            raise ConnectionError("Perte du signal principal")
    except ConnectionError:
        print("Test 2 terminé : l'erreur a bien été propagée et loggée.")
        
    print("\nVérifie le fichier space_data/logs/MSN-001.log !")