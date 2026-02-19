import os
import json
from datetime import datetime
from astro_utils import distance_3d, alerte_systeme

def charger_tous_les_json(dossier):
    """Charge dynamiquement tous les fichiers JSON d'un dossier."""
    donnees = {}
    for fichier in os.listdir(dossier):
        if fichier.endswith('.json'):
            chemin = os.path.join(dossier, fichier)
            try:
                with open(chemin, 'r', encoding='utf-8') as f:
                    nom_cle = fichier.replace('.json', '')
                    donnees[nom_cle] = json.load(f)
            except Exception:
                pass # Si un fichier plante, on l'ignore silencieusement pour le dashboard
    return donnees

def generer_tableau_de_bord():
    # 1. Chargement global
    dossier_data = 'space_data/'
    donnees = charger_tous_les_json(dossier_data)
    
    missions = donnees.get('missions', {}).get('missions', [])
    equipages = donnees.get('equipages', {}).get('astronautes', [])
    telemetrie = donnees.get('telemetrie', {})
    config = donnees.get('config_systeme', {})
    
    # Ciblage de la mission demandée
    mission = next((m for m in missions if m['id'] == 'MSN-001'), None)
    if not mission:
        print("Erreur : Mission MSN-001 introuvable.")
        return

    # 2. Croisement avec les équipages
    equipage_details = []
    for membre in mission['equipage']:
        # Récupère juste le nom sans le grade (ex: "Cmdr. Léa Fontaine" -> "Léa Fontaine")
        nom_propre = membre.split(". ")[-1] if ". " in membre else membre
        profil = next((a for a in equipages if a['nom'] == nom_propre), None)
        if profil:
            equipage_details.append(profil)

    # 3. Analyse mathématique de la télémétrie
    releves = telemetrie.get('releves', [])
    seuils = config.get('seuils_alerte', {})
    
    distance_totale = 0
    for i in range(1, len(releves)):
        distance_totale += distance_3d(releves[i-1]['position_km'], releves[i]['position_km'])
        
    # Calcul du temps (compatibilité ISO 8601)
    t_debut = datetime.fromisoformat(releves[0]['timestamp'].replace("Z", "+00:00"))
    t_fin = datetime.fromisoformat(releves[-1]['timestamp'].replace("Z", "+00:00"))
    
    duree_heures = (t_fin - t_debut).total_seconds() / 3600
    jours_vol = (t_fin - t_debut).days + 1
    
    vitesse_moy = (distance_totale / (duree_heures * 3600)) if duree_heures > 0 else 0
    conso_totale = releves[0]['carburant_pourcent'] - releves[-1]['carburant_pourcent']
    taux_conso_h = conso_totale / duree_heures if duree_heures > 0 else 0
    
    # 4. Traitement des alertes
    alertes_formattees = []
    for releve in releves:
        alertes = alerte_systeme(releve, seuils)
        if alertes:
            t_releve = datetime.fromisoformat(releve['timestamp'].replace("Z", "+00:00"))
            jour_relatif = (t_releve - t_debut).days + 1
            for a in alertes:
                alertes_formattees.append(f"[J+{jour_relatif}] {a}")

    # 5. Rendu ASCII
    r_fin = releves[-1]
    pos = r_fin['position_km']
    carb_restant = r_fin['carburant_pourcent']
    o2_restant = r_fin['oxygene_pourcent']
    
    # Petites barres de progression visuelles
    bar_carb = "█" * int(carb_restant/10) + "░" * (10 - int(carb_restant/10))
    bar_o2 = "█" * int(o2_restant/10) + "░" * (10 - int(o2_restant/10))

    def ligne_ascii(texte):
        # Maintient la bordure droite alignée à 63 caractères
        print(f"║  {texte}".ljust(63) + "║")

    print("╔══════════════════════════════════════════════════════════════╗")
    print(f"║           🛰️  TABLEAU DE BORD — {mission['nom'].upper()} ({mission['id']})        ║")
    print("╠══════════════════════════════════════════════════════════════╣")
    ligne_ascii(f"Vaisseau    : {telemetrie['vaisseau']}")
    ligne_ascii(f"Destination : {mission['destination']}")
    ligne_ascii(f"Lancé le    : {mission['date_lancement']}")
    ligne_ascii(f"Jour de vol : J+{jours_vol}")
    print("╠══════════════════════════════════════════════════════════════╣")
    ligne_ascii("ÉQUIPAGE")
    for p in equipage_details:
        ligne_ascii(f"├─ {p['grade']} {p['nom']} ({p['nationalite']}) — {p['heures_vol_spatial']}h vol")
    print("╠══════════════════════════════════════════════════════════════╣")
    ligne_ascii("TÉLÉMÉTRIE (dernier relevé)")
    ligne_ascii(f"├─ Position    : X: {pos['x']:,.0f} | Y: {pos['y']:,.0f} | Z: {pos['z']:,.0f} km")
    ligne_ascii(f"├─ Altitude    : {r_fin['altitude_km']:,} km")
    ligne_ascii(f"├─ Vitesse     : {r_fin['vitesse_km_s']} km/s")
    ligne_ascii(f"├─ Carburant   : {carb_restant}%  {bar_carb}")
    ligne_ascii(f"├─ Oxygène     : {o2_restant}%  {bar_o2}")
    ligne_ascii(f"└─ Temp. cab.  : {r_fin['temperature_cabine_c']}°C")
    print("╠══════════════════════════════════════════════════════════════╣")
    ligne_ascii("ANALYSE DE TRAJET")
    ligne_ascii(f"├─ Distance parcourue  : {distance_totale:,.0f} km")
    ligne_ascii(f"├─ Vitesse moyenne     : {vitesse_moy:.2f} km/s")
    ligne_ascii(f"├─ Conso. carburant    : {taux_conso_h:.2f}%/h")
    ligne_ascii(f"└─ Seuil alerte carburant : {seuils.get('carburant_min_pourcent', 20)}%")
    print("╠══════════════════════════════════════════════════════════════╣")
    ligne_ascii("⚠️  ALERTES")
    for idx, alerte in enumerate(alertes_formattees):
        prefix = "└─" if idx == len(alertes_formattees) - 1 else "├─"
        ligne_ascii(f"{prefix} {alerte}")
    print("╚══════════════════════════════════════════════════════════════╝")

    # 6. Exportation JSON
    rapport_final = {
        "mission_id": mission['id'],
        "distance_totale_km": round(distance_totale, 2),
        "vitesse_moyenne_km_s": round(vitesse_moy, 2),
        "taux_conso_carburant_par_heure": round(taux_conso_h, 2),
        "alertes": alertes_formattees
    }
    
    chemin_export = f"space_data/rapports/dashboard_{mission['id']}.json"
    with open(chemin_export, 'w', encoding='utf-8') as f:
        json.dump(rapport_final, f, indent=2, ensure_ascii=False)
        
    print(f"\n[OK] Rapport exporté dans {chemin_export}")

if __name__ == '__main__':
    generer_tableau_de_bord()