from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/"
path.append(BRICKSTOCK_PATH)

import sqlite3
from serveur_tools.scripts_gestion_bdd.admin_bdd import DATABASE_NAME
from serveur_tools.scripts_gestion_bdd.bdd_insert import auto_insert_pieces_du_set
from serveur_tools.json_tools import save_json
from serveur_tools.requetes_api import get_image_ref_set
from tqdm import tqdm



def update1() :
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute('''SELECT id_set FROM Sets;''')
    r = []
    for e in curseur :
        r.append(e[0])
    connexion.close()
    l = len(r)

    deb = 1
    i = deb

    for s in r[deb - 1:] :
    # for s in [r[deb - 1]] :
        print(f"{i}/{l}")
        save_json(auto_insert_pieces_du_set(s, i, l), f"/data_save/piece_in_set_data/{s}.json")
        i += 1
    print("end")

def update2() :
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute('''SELECT id_set, image_ref FROM Sets;''')
    r = {}
    for e in curseur :
        r[e[0]] = e[1]
    save_json(r, "/data_save/save_image_ref_sets.json")
    for s in tqdm(r) :
        curseur.execute('''UPDATE Sets SET image_ref = ? WHERE id_set = ?;''', (get_image_ref_set(s), s))
    connexion.commit()
    connexion.close()
    print("end")