import json
import os
def ajouter_entree_journal():
    chemin_journal = 'space_data/logs/journal.json'
    print("=== Nouveau journal de bord ===")
    date_log = input("Date (YYYY-MM-DD) : ")
    auteur = input("Auteur : ")
    message = input("Message : ")
    #Construction du dictionnaire pour la nouvelle entrée
    nouvelle_entree = {
        "date": date_log,
        "auteur": auteur,
        "message": message
    }
    #Initialisons la liste du journal
    journal = []
    #Si le fichier existe déjà, on charge son contenu pour ne pas l'écraser
    if os.path.exists(chemin_journal):
        try:
            with open(chemin_journal, 'r', encoding='utf-8') as f:
                journal = json.load(f)
        except json.JSONDecodeError:
            #Si le fichier est vide ou mal formaté, on garde la liste vide
            pass          
    # Ajout de la nouvelle entrée
    journal.append(nouvelle_entree)
    # Sauvegarde dans le fichier JSON
    with open(chemin_journal, 'w', encoding='utf-8') as f:
        json.dump(journal, f, indent=2, ensure_ascii=False)    
    print(f"\n[OK] Entrée ajoutée au journal ({len(journal)} entrées au total).")
if __name__ == '__main__':
    ajouter_entree_journal()