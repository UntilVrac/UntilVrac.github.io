from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
path.append(BRICKSTOCK_PATH)

import sqlite3
from serveur_tools.scripts_gestion_bdd.admin_bdd import *
from serveur_tools.scripts_gestion_bdd.bdd_verif import *
import serveur_tools.requetes_api as api
from serveur_tools.json_tools import save_json, upload_json

def __update_pieces_in_set(connexion:sqlite3.Connection, curseur:sqlite3.Cursor, id_set:int, pieces:dict) -> None :
    """
    entrées :
        connexion (sqlite3.Connect) et curseur (sqlite3.Cursor), la connexion à utiliser
        id_set (int), id du set
        pieces (dict), liste des pièces sous la forme d'un dictionnaire {id_piece (int) : quantite (int)}

    met à jour la liste des pièces du set
    """
    curseur.execute('''DELETE FROM piece_dans_set WHERE id_set = ?;''', (id_set,))
    for p in pieces :
        assert type(p) == int
        assert type(pieces[p]) == int
        assert piece_in_database(p)
        curseur.execute('''INSERT INTO piece_dans_set VALUES (?, ?, ?);''', (id_set, p, pieces[p]))
    connexion.commit()
    connexion.close()

def update_pieces_in_set(id_set:int, pieces:dict) -> bool :
    """
    entrées :
        id_set (int), id du set
        pieces (dict), liste des pièces sous la forme d'un dictionnaire {id_piece (int) : quantite (int)}

    met à jour la liste des pièces du set
    si MODE_SANS_ECHEC est True, renvoie True si l'ajout a pu être effectué et False sinon
    sinon renvoie True
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    if MODE_SANS_ECHEC :
        try :
            __update_pieces_in_set(connexion, curseur, id_set, pieces)
        except :
            connexion.close()
            return False
        else :
            return True
    else :
        __update_pieces_in_set(connexion, curseur, id_set, pieces)
        return True

def __update_minifig_in_set(connexion:sqlite3.Connection, curseur:sqlite3.Cursor, id_set:int, minifigs:dict) -> None :
    """
    entrées :
        connexion (sqlite3.Connect) et curseur (sqlite3.Cursor), la connexion à utiliser
        id_set (int), id du set
        minifigs (dict), liste des minifigs sous la forme d'un dictionnaire {id_minifig (str) : quantite (int)}

    met à jour la liste des minifigs du set
    """
    curseur.execute('''DELETE FROM minifig_dans_set WHERE id_set = ?;''', (id_set,))
    for m in minifigs :
        assert type(m) == str
        assert type(minifigs[m]) == int
        assert minifig_in_database(m)
        curseur.execute('''INSERT INTO minifig_dans_set VALUES (?, ?, ?);''', (id_set, m, minifigs[m]))
    connexion.commit()
    connexion.close()

def update_minifig_in_set(id_set:int, minifigs:dict) -> bool :
    """
    entrées :
        id_set (int), id du set
        minifigs (dict), liste des minifigs sous la forme d'un dictionnaire {id_minifig (str) : quantite (int)}

    met à jour la liste des minifigs du set
    si MODE_SANS_ECHEC est True, renvoie True si l'ajout a pu être effectué et False sinon
    sinon renvoie True
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    if MODE_SANS_ECHEC :
        try :
            __update_minifig_in_set(connexion, curseur, id_set, minifigs)
        except :
            connexion.close()
            return False
        else :
            return True
    else :
        __update_minifig_in_set(connexion, curseur, id_set, minifigs)
        return True

def __update_statut_exemplaires(connexion:sqlite3.Connection, curseur:sqlite3.Cursor, exemplaires:dict) -> bool :
    """
    entrées :
        connexion (sqlite3.Connect) et curseur (sqlite3.Cursor), la connexion à utiliser
        exemplaires (dict), la liste des exemplaires sous la forme d'une dictionnaire {id de l'exemplaire (int) : statut (construit ou détruit)}

    met à jour les statuts des exemplaires
    """
    for e in exemplaires :
        assert exemplaires[e] in ("construit", "détruit")
        curseur.execute('''UPDATE Sets SET statut = ? WHERE id_exemplaire = ?;''', (exemplaires[e], e))
        connexion.commit()
        connexion.close()

def update_statut_exemplaires(exemplaires:dict) -> bool :
    """
    entrées :
        exemplaires (dict), la liste des exemplaires sous la forme d'une dictionnaire {id de l'exemplaire (int) : statut (construit ou détruit)}

    met à jour les statuts des exemplaires
    si MODE_SANS_ECHEC est True, renvoie True si l'ajout a pu être effectué et False sinon
    sinon renvoie True
    """
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    if MODE_SANS_ECHEC :
        try :
            __update_statut_exemplaires(connexion, curseur, exemplaires)
        except :
            connexion.close()
            return False
        else :
            return True
    else :
        __update_statut_exemplaires(connexion, curseur, exemplaires)
        return True

def __update_moc_piece_qt(connexion:sqlite3.Connection, curseur:sqlite3.Cursor, id_piece:int, quantite:int, disponible:int, endommagee:int) -> None :
    """
    entrées :
        connexion (sqlite3.Connect) et curseur (sqlite3.Cursor), la connexion à utiliser
        id_piece (int), l'id de la pièce
        quantite (int), disponible (int), endommagee (int), les nouvelles quantités

    met à jour les quantités de la pièce dans la collection
    """
    assert piece_est_dans_moc(id_piece)
    curseur.execute('''UPDATE Pieces SET quantite = ?, disponible = ?, endommagee = ? WHERE id_piece = ?;''', (quantite, disponible, endommagee, id_piece))
    connexion.commit()
    connexion.close()

def update_moc_piece_qt(id_piece:int, quantite:int, disponible:int, endommagee:int) -> bool :
    """
    entrées :
        id_piece (int), l'id de la pièce
        quantite (int), disponible (int), endommagee (int), les nouvelles quantités

    met à jour les quantités de la pièce dans la collection
    si MODE_SANS_ECHEC est True, renvoie True si l'ajout a pu être effectué et False sinon
    sinon renvoie True
    """
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    if MODE_SANS_ECHEC :
        try :
            __update_moc_piece_qt(connexion, curseur, id_piece, quantite, disponible, endommagee)
        except :
            connexion.close()
            return False
        else :
            return True
    else :
        __update_moc_piece_qt(connexion, curseur, id_piece, quantite, disponible, endommagee)
        return True
    
def __update_moc_minifig_qt(connexion:sqlite3.Connection, curseur:sqlite3.Cursor, id_minifig:str, quantite:int) -> None :
    """
    entrées :
        connexion (sqlite3.Connect) et curseur (sqlite3.Cursor), la connexion à utiliser
        id_piece (int), l'id de la pièce
        quantite (int) la nouvelle quantité

    met à jour la quantité de la minifig dans la collection
    """
    assert minifig_est_dans_moc(id_minifig)
    curseur.execute('''UPDATE Minifigs SET nb_exemplaires = ? WHERE id_minifig = ?;''', (quantite, id_minifig))
    connexion.commit()
    connexion.close()
    
def update_moc_minifig_qt(id_minifig:str, quantite:int) -> bool :
    """
    entrées :
        id_piece (int), l'id de la pièce
        quantite (int) la nouvelle quantité

    met à jour la quantité de la minifig dans la collection
    si MODE_SANS_ECHEC est True, renvoie True si l'ajout a pu être effectué et False sinon
    sinon renvoie True
    """
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    if MODE_SANS_ECHEC :
        try :
            __update_moc_minifig_qt(connexion, curseur, id_minifig, quantite)
        except :
            connexion.close()
            return False
        else :
            return True
    else :
        __update_moc_minifig_qt(connexion, curseur, id_minifig, quantite)
        return True
    
def __update_rangement_content(connexion:sqlite3.Connection, curseur:sqlite3.Cursor, id_rangement:int, liste_elements:list) -> None :
    """
    entrées :
        connexion (sqlite3.Connect) et curseur (sqlite3.Cursor), la connexion à utiliser
        id_rangement (int), l'id du rangement physique
        liste_elements (list), la liste des id des éléments (pièce ou design) contenu dans le rangement

    met à jour le contenu du rangement
    si MODE_SANS_ECHEC est True, renvoie True si l'ajout a pu être effectué et False sinon
    sinon ranvoie True
    """
    # curseur.execute('''SELECT id_rangement FROM Rangements_virtuels WHERE rangement_physique = ?;''', (id_rangement,))
    # r = []
    # for e in curseur :
    #     r.append(e[0])
    # assert len(r) == 1
    # id_rangement_virtuel = r[0]
    # curseur.execute('''DELETE FROM rangement_content WHERE id_rangement = ?;''', (id_rangement_virtuel,))
    curseur.execute('''DELETE FROM rangement_content WHERE id_rangement = ?;''', (id_rangement,))
    for id in liste_elements :
        # curseur.execute('''INSERT INTO rangement_content (id_rangement, id_element) VALUES (?, ?);''', (id_rangement_virtuel, id))
        curseur.execute('''INSERT INTO rangement_content (id_rangement, id_element) VALUES (?, ?);''', (id_rangement, id))
    connexion.commit()
    connexion.close()

def update_rangement_content(id_rangement:int, liste_elements:list) -> bool :
    """
    entrées :
        id_rangement (int), l'id du rangement physique
        liste_elements (list), la liste des id des éléments (pièce ou design) contenu dans le rangement

    met à jour le contenu du rangement
    si MODE_SANS_ECHEC est True, renvoie True si la mise à jour a pu être effectuée et False sinon
    sinon ranvoie True
    """
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    if MODE_SANS_ECHEC :
        try :
            __update_rangement_content(connexion, curseur, id_rangement, liste_elements)
        except :
            connexion.close()
            return False
        else :
            return True
    else :
        __update_rangement_content(connexion, curseur, id_rangement, liste_elements)
        return True
    
def supprimer_element_du_rangement(id_rangement:int, id_element:int) -> None :
    """
    entrées :
        id_rangement (int), l'id du rangement
        liste_elements (list), l'id de l'élément à supprimer
    
    supprime l'élément du rangement
    """
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    curseur.execute('''DELETE FROM rangement_content WHERE id_rangement = ? AND id_element = ?;''', (id_rangement, id_element))
    connexion.commit()
    connexion.close()

def change_parent_rangement(id_rangement:int, id_parent:int) -> None :
    """
    entrées :
        id_rangement (int), l'id du rangement
        id_parent (int), l'id du nouveau parent
    """
    assert rangement_est_compartimente(id_parent)
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    curseur.execute('''UPDATE Rangements_physiques SET rangement_parent = ? WHERE id_rangement = ?;''', (id_parent, id_rangement))
    connexion.commit()
    connexion.close()

def supprimer_rangement(id_rangement:int) -> None :
    """
    id_rangement (int), l'id du rangement à supprimer

    supprime le rangement
    """
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    curseur.execute('''SELECT id_rangement FROM Rangements_physiques WHERE rangement_parent = ?;''', (id_rangement,))
    r = []
    for e in curseur :
        r.append(e[0])
    # print(r)
    for e in r :
        supprimer_rangement(e)
    curseur.execute('''DELETE FROM rangement_content WHERE id_rangement = ?;''', (id_rangement,))
    curseur.execute('''DELETE FROM Rangements_virtuels WHERE rangement_physique = ?;''', (id_rangement,))
    curseur.execute('''DELETE FROM Rangements_physiques WHERE id_rangement = ?;''', (id_rangement,))
    connexion.commit()
    connexion.close()

def update_rangement_data(id_rangement:int, nom_rangement:str, type_rangement:str, nb_compartiments:int, compartimentation:str) -> None :
    """
    entrées :
        id_rangement (int), l'id du rangement
        nom_rangement (str), nb_compartiments (int) et compartimentation (str), les nouvelles valeurs

    met à jour les valeurs
    """
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    curseur.execute('''UPDATE Rangements_physiques SET nom_rangement = ? AND type_rangement = ? AND nb_compartiments = ? AND compartimentation = ? WHERE id_rangement = ?;''', (nom_rangement, type_rangement, nb_compartiments, compartimentation, id_rangement))
    connexion.commit()
    connexion.close()