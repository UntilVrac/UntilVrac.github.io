from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
path.append(BRICKSTOCK_PATH)

import sqlite3
from serveur_tools.scripts_gestion_bdd.admin_bdd import *



def categorie_in_database(id_categorie:int) -> bool :
    """
    id_categorie (int), l'id de la catégorie à tester

    renvoie True si cet est présent dans la base de données et False sinon
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    r = []
    curseur.execute('''SELECT id_categorie FROM Categories WHERE id_categorie = ?;''', (id_categorie,))
    for e in curseur :
        r.append(e)
    r = len(r) != 0
    connexion.close()
    return r

def design_in_database(id_design:int) -> bool :
    """
    id_design (int), l'id du design à tester

    renvoie True si cet id est présent dans la base de données et False sinon
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    r = []
    curseur.execute('''SELECT * FROM Design WHERE id_design = ?;''', (id_design,))
    for e in curseur :
        r.append(e)
    r = len(r) != 0
    connexion.close()
    return r

def ton_in_database(id_ton:int) -> bool :
    """
    id_ton (int), l'id du ton à tester

    renvoie True si cet id est présent dans la base de données et False sinon
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    r = []
    curseur.execute('''SELECT * FROM Tons WHERE id_ton = ?;''', (id_ton,))
    for e in curseur :
        r.append(e)
    r = len(r) != 0
    connexion.close()
    return r

def couleur_is_new(id_couleur:int, id_bricklink:int, id_rebrickable:int) -> bool :
    """
    id_couleur (int), id_bricklink (int) et id_rebrickable (int), les id à tester

    renvoie True si aucun des id n'est utilisé dans la base de données et False sinon
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    r = []
    curseur.execute('''SELECT * FROM Couleurs WHERE id_couleur = ? OR id_couleur_bricklink = ? OR id_couleur_rebrickable = ?;''', (id_couleur, id_bricklink, id_rebrickable))
    for e in curseur :
        r.append(e)
    connexion.close()
    return len(r) == 0

def minifig_is_new(id_minifig:int, id_rebrickable:str) -> bool :
    """
    id_minig (int) et id_rebrickable (str), les id à tester

    renvoie True si aucun des id n'est utilisé dans la base de données et False sinon
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    r = []
    curseur.execute('''SELECT * FROM Minifigures WHERE id_minifig = ? OR id_rebrickable = ?;''', (id_minifig, id_rebrickable))
    for e in curseur :
        r.append(e)
    connexion.close()
    return len(r) == 0

def set_in_database(id_set:int) -> bool :
    """
    id_set (int), l'id du set à tester

    renvoie True si cet id est présent dans la base de données et False sinon
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    r = []
    curseur.execute('''SELECT * FROM Sets WHERE id_set = ?;''', (id_set,))
    for e in curseur :
        r.append(e)
    connexion.close()
    assert len(r) in (0, 1)
    return len(r) == 1

def piece_in_database(id_piece:int) -> bool :
    """
    id_piece (int), l'id de la pièce à tester

    renvoie True si cet id est présent dans la base de données et False sinon
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute('''SELECT * FROM Piece WHERE id_piece = ?;''', (id_piece,))
    r = []
    for e in curseur :
        r.append(e)
    connexion.close()
    assert len(r) in (0, 1)
    return len(r) == 1

def minifig_in_database(id_minifigure:str) -> bool :
    """
    id_minifigure (str), id de la minifig à tester

    renvoie True si cet id est présent dans la base de données et False sinon
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute('''SELECT * FROM Minifigures WHERE id_minifig = ?;''', (id_minifigure,))
    r = []
    for e in curseur :
        r.append(e)
    connexion.close()
    assert len(r) in (0, 1)
    return len(r) == 1

def gamme_in_database(id_gamme:str) -> bool :
    """
    id_gamme (str), id de la gamme à tester

    renvoie True si cet id est présent dans la base de données et False sinon
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute('''SELECT * FROM Gammes WHERE id_gamme = ?;''', (id_gamme,))
    r = []
    for e in curseur :
        r.append(e)
    connexion.close()
    assert len(r) in (0, 1)
    return len(r) == 1



def piece_est_dans_moc(id_piece:int) -> bool :
    """
    id_piece (int), id de la pièce à tester

    renvoie True si l'id est présent dans la collection et False sinon
    """
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    curseur.execute('''SELECT * FROM Pieces WHERE id_piece = ?;''', (id_piece,))
    r = []
    for e in curseur :
        r.append(e)
    connexion.close()
    assert len(r) in (0, 1)
    return len(r) == 1

def minifig_est_dans_moc(id_minifig:str) -> bool :
    """
    id_minifig (str), l'id de la minifig à tester

    renvoie True si l'id est présent dans la collection et False sinon
    """
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    curseur.execute('''SELECT * FROM Minifigs WHERE id_minifig = ?;''', (id_minifig,))
    r = []
    for e in curseur :
        r.append(e)
    connexion.close()
    assert len(r) in (0, 1)
    return len(r) == 1

def rangement_est_compartimente(id_rangement:int) -> bool :
    """
    id_rangement (int), id du rangement à tester

    renvoie True si le rangement est compartimenté et False sinon (contient directement des pièces de Lego)
    """
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    # curseur.execute('''SELECT COUNT(*) FROM Rangements_physiques WHERE rangement_parent = ?;''', (id_rangement,))
    curseur.execute('''SELECT nb_compartiments FROM Rangements_physiques WHERE id_rangement = ?;''', (id_rangement,))
    r = []
    for e in curseur :
        r.append(e[0])
    connexion.close()
    # return r[0] > 0
    return r[0] == 1



if __name__ == "__main__" :
    print(rangement_est_compartimente(1))