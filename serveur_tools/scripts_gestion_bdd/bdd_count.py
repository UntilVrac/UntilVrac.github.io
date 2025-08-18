from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/"
path.append(BRICKSTOCK_PATH)

import sqlite3
from serveur_tools.scripts_gestion_bdd.admin_bdd import *

def count_minifigs_in_set(id_set:int) -> int :
    """
    id_set (int), l'id du set

    renvoie le nombre de minifig contenus dans le set
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute('''SELECT SUM(quantite) FROM minifig_dans_set WHERE id_set = ?;''', (id_set,))
    r = []
    for e in curseur :
        r.append(e[0])
    connexion.close()
    assert len(r) == 1
    if r[0] == None :
        return 0
    else :
        return r[0]

def count_pieces_in_set(id_set) -> int :
    """
    id_set (int), id du set

    renvoie le nombre de pièces contenus dans le set, d'après la base de données
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute('''SELECT SUM(quantite) FROM piece_dans_set WHERE id_set = ?;''', (id_set,))
    r = []
    for e in curseur :
        r.append(e[0])
    connexion.close()
    assert len(r) == 1
    if r[0] == None :
        return 0
    else :
        return r[0]
    


def count_exemplaires_in_moc(id_set:int) -> int :
    """
    id_set (int), id du set

    renvoie le nombre d'exemplaires de ce set présents dans la collection
    """
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    curseur.execute('''SELECT COUNT(*) FROM Sets WHERE id_set = ?;''', (id_set,))
    r = []
    for e in curseur :
        r.append(e[0])
    connexion.close()
    assert len(r) == 1
    return r[0]