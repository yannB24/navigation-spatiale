import os
import json
import time
import subprocess
from datetime import datetime

# Import des modules que tu as créés précédemment
try:
    from astro_utils import alerte_systeme
    from archiveur import scanner_et_archiver
    from tableaudebord import generer_tableau_de_bord
except ImportError:
    print("⚠️  Attention : modules manquants. Vérifie tes fichiers astro_utils.py, archiveur.py et tableau_de_bord.py.")

# ==========================================
# CLASSES DE SECURITE ET DE LOG
# ==========================================
class ErreurTelemetrie(Exception): pass
class SeuilDepasse(ErreurTelemetrie): pass
class DonneesManquantes(ErreurTelemetrie): pass
class HorodatageInvalide(ErreurTelemetrie): pass

class LogMission:
    def __init__(self, mission_id):
        self.mission_id = mission_id
        self.filepath = f"space_data/logs/{self.mission_id}.log"
        self.erreurs = 0

    def __enter__(self):
        self.start_time = time.time()
        self.fichier = open(self.filepath, 'a', encoding='utf-8')
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fichier.write(f"=== SESSION {ts} | {self.mission_id} ===\n")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.erreurs += 1
            self.fichier.write(f"[CRITIQUE] {exc_type.__name__}: {exc_val}\n")
        duree = time.time() - self.start_time
        self.fichier.write(f"=== FIN DE SESSION | Durée: {duree:.3f}s | Erreurs: {self.erreurs} ===\n\n")
        self.fichier.close()
        return False

    def ecrire(self, niveau, msg):
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.fichier.write(f"[{ts}] [{niveau}] {msg}\n")

# ==========================================
# UTILITAIRES DE BASE
# ==========================================
def charger_json_securise(chemin):
    try:
        with open(chemin, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

def valider_releve(releve, seuils):
    if "timestamp" not in releve: 
        raise DonneesManquantes("timestamp manquant")
    try:
        datetime.fromisoformat(releve["timestamp"].replace("Z", "+00:00"))
    except ValueError:
        raise HorodatageInvalide(releve["timestamp"])
        
    c_actuel = releve.get("carburant_pourcent", 100)
    c_min = seuils.get("carburant_min_pourcent", 20)
    if c_actuel < c_min:
        raise SeuilDepasse(f"Carburant à {c_actuel}%")
    return True

# ==========================================
# PROGRAMME PRINCIPAL
# ==========================================
def main():
    # Création des dossiers au démarrage
    config = charger_json_securise("space_data/config_systeme.json") or {}
    for rep in config.get("repertoires", {}).values():
        os.makedirs(rep, exist_ok=True)
        
    while True:
        # Nettoyage de l'écran (Bonus)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("╔════════════════════════════════════════════╗")
        print("║   🚀 CENTRE DE CONTRÔLE SPATIAL — v4.7.2   ║")
        print("╠════════════════════════════════════════════╣")
        print("║  1. 📋 Lister les missions                 ║")
        print("║  2. 🔍 Détail d'une mission                ║")
        print("║  3. 📡 Télémétrie en direct                ║")
        print("║  4. 👨‍🚀 Gestion des équipages               ║")
        print("║  5. 📝 Ajouter une entrée au journal       ║")
        print("║  6. ⚠️  Diagnostic des systèmes             ║")
        print("║  7. 🗂️  Archiver les données                ║")
        print("║  8. 📊 Générer le tableau de bord          ║")
        print("║  9. ⚙️  Configuration                       ║")
        print("║  0. 🚪 Quitter                             ║")
        print("╚════════════════════════════════════════════╝")
        
        choix = input("\n> Sélectionnez une option : ")
        print("-" * 46)
        
        try:
            if choix == "1":
                data = charger_json_securise("space_data/missions.json")
                for m in data.get("missions", []):
                    print(f"[{m['id']}] {m['nom']} → {m['destination']} ({m['statut']})")
            
            elif choix == "2":
                m_data = charger_json_securise("space_data/missions.json")
                eq_data = charger_json_securise("space_data/equipages.json")
                mid = input("ID de la mission (ex: MSN-001) : ")
                mission = next((m for m in m_data.get("missions", []) if m["id"] == mid), None)
                
                if mission:
                    print(f"\nNom : {mission['nom']}\nLancement : {mission['date_lancement']}")
                    print("Équipage :")
                    for membre in mission['equipage']:
                        nom_propre = membre.split(". ")[-1] if ". " in membre else membre
                        profil = next((a for a in eq_data.get("astronautes", []) if a['nom'] == nom_propre), None)
                        if profil:
                            print(f"  - {profil['nom']} ({profil['specialite']} | {profil['heures_vol_spatial']}h vol)")
                        else:
                            print(f"  - {membre}")
                else:
                    print("Mission introuvable.")

            elif choix == "3":
                tel = charger_json_securise("space_data/telemetrie.json")
                seuils = config.get("seuils_alerte", {})
                print("Derniers relevés télémétriques :")
                for r in tel.get("releves", [])[-3:]:
                    print(f"\n[{r['timestamp']}] Alt: {r['altitude_km']:,}km, Vit: {r['vitesse_km_s']}km/s")
                    alertes = alerte_systeme(r, seuils)
                    for a in alertes: 
                        print(f"  ⚠️ {a}")

            elif choix == "4":
                eq = charger_json_securise("space_data/equipages.json")
                recherche = input("Rechercher un astronaute (nom ou nationalité) : ").lower()
                trouve = False
                for a in eq.get("astronautes", []):
                    if recherche in a['nom'].lower() or recherche in a['nationalite'].lower():
                        print(f"- {a['nom']} ({a['nationalite']}) — {a['specialite']}")
                        trouve = True
                if not trouve: print("Aucune correspondance.")

            elif choix == "5":
                m_id = input("ID de la mission pour le log (ex: MSN-001) : ")
                with LogMission(m_id) as log:
                    date_log = input("Date (YYYY-MM-DD) : ")
                    auteur = input("Auteur : ")
                    msg = input("Message : ")
                    
                    chemin_j = 'space_data/logs/journal.json'
                    journal = charger_json_securise(chemin_j) or []
                    journal.append({"date": date_log, "auteur": auteur, "message": msg})
                    
                    with open(chemin_j, 'w', encoding='utf-8') as f:
                        json.dump(journal, f, indent=2, ensure_ascii=False)
                        
                    log.ecrire("INFO", f"Nouvelle entrée ajoutée par {auteur}")
                    print("[OK] Journal mis à jour et log sauvegardé.")

            elif choix == "6":
                print("Lancement du diagnostic global...")
                tel = charger_json_securise("space_data/telemetrie.json")
                seuils = config.get("seuils_alerte", {})
                
                # Bonus : Ping réseau fictif
                print("\n[Réseau] Test de communication...")
                cmd = ["ping", "-n", "1", "127.0.0.1"] if os.name == 'nt' else ["ping", "-c", "1", "127.0.0.1"]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("[OK] Connexion nominale.")

                print("\n[Systèmes] Vérification des relevés...")
                erreurs = 0
                for r in tel.get("releves", []):
                    try:
                        valider_releve(r, seuils)
                    except ErreurTelemetrie as e:
                        print(f"❌ Relevé {r.get('timestamp')} : {e.__class__.__name__} - {e}")
                        erreurs += 1
                
                if erreurs == 0:
                    print("✅ Tous les relevés sont valides.")

            elif choix == "7":
                scanner_et_archiver()

            elif choix == "8":
                generer_tableau_de_bord()

            elif choix == "9":
                print("Configuration système :")
                print(f"Version : {config.get('version_logiciel')}")
                print("Seuils d'alerte :")
                for k, v in config.get("seuils_alerte", {}).items():
                    print(f"  - {k} : {v}")

            elif choix == "0":
                print("Fermeture du simulateur. Bon vol ! 🚀")
                break
            else:
                print("Option invalide.")

        except Exception as e:
            # Sécurité ultime : le programme ne crashe jamais
            print(f"⚠️ Erreur système capturée : {e}")

        input("\nAppuyez sur Entrée pour continuer...")

if __name__ == '__main__':
    main()