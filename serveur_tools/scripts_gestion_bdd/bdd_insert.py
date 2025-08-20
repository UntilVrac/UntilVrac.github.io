from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
path.append(BRICKSTOCK_PATH)
from time import sleep
from tqdm import tqdm

import sqlite3
from serveur_tools.scripts_gestion_bdd.admin_bdd import *
from serveur_tools.scripts_gestion_bdd.bdd_verif import *
from serveur_tools.scripts_gestion_bdd.bdd_get import *
import serveur_tools.requetes_api as api
import serveur_tools.scrap_data as scrap
from serveur_tools.json_tools import save_json

def __ajouter_categorie(connexion:sqlite3.Connection, curseur:sqlite3.Cursor, id_categorie:int, nom_categorie:str, categorie_sup:int, image_ref:str) -> None :
    """
    entrées :
        connexion (sqlite3.Connect) et curseur (sqlite3.Cursor) la connexion à utiliser
        id_categorie (int), nom_categorie (str), categorie_sup (int) et image_ref (str), les informations de la catégorie à ajouter
    
    ajoute la catégorie à la base de données
    """
    assert not categorie_in_database(id_categorie)
    if categorie_sup != None :
        assert categorie_in_database(categorie_sup)
        assert id_categorie not in get_liste_sous_categories(categorie_sup)
    curseur.execute('''INSERT INTO Categories VALUES (?, ?, ?, ?);''', (id_categorie, nom_categorie, categorie_sup, image_ref))
    connexion.commit()
    connexion.close()

def ajouter_categorie(id_categorie:int, nom_categorie:str, image_ref:str, categorie_sup:int=None) -> bool :
    """
    entrées :
        id_categorie (int), nom_categorie (str), categorie_sup (int) (None par défaut) et image_ref (str), les informations de la catégorie à ajouter
    
    ajoute la catégorie à la base de données
    si MODE_SANS_ECHEC est True, renvoie True si l'ajout a pu être effectué et False sinon
    sinon renvoie True
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    if MODE_SANS_ECHEC :
        try :
            __ajouter_categorie(connexion, curseur, id_categorie, nom_categorie, categorie_sup, image_ref)
        except :
            connexion.close()
            return False
        else :
            return True
    else :
        __ajouter_categorie(connexion, curseur, id_categorie, nom_categorie, categorie_sup, image_ref)
        return True
    
def __ajouter_design(connexion:sqlite3.Connection, curseur:sqlite3.Cursor, id_design:int, id_lego:int, id_bricklink:int, nom:str, nom_lego:str, nom_bricklink:str, dimensions:str, categorie:int, transparent:bool) -> None :
    """
    entrées :
        connexion (sqlite3.Connect) et curseur (sqlite3.Cursor) la connexion à utiliser
        id_design (int), id_lego (int), id_bricklink (str), nom (str), nom_lego (str), nom_bricklink (str), dimensions (str), categorie (int) et transparent (bool), les infos du design
    
    ajoute le design à la base de données
    """
    if id_lego == None :
        datas_api = api.get_design_data_for_insert_in_bdd(("id_bricklink", id_bricklink))
        id_lego = int(datas_api["list_id_lego"][0])
    else :
        datas_api = api.get_design_data_for_insert_in_bdd(("id_lego", id_lego))
        if id_bricklink == None :
            id_bricklink = datas_api["id_bricklink"]
    id_rebrickable, nom_rebrickable = datas_api["id_rebrickable"], datas_api["nom_rebrickable"]
    assert not design_in_database(id_design)
    bricklink_data = scrap.get_part_infos(id_bricklink)
    try :
        quantite_mur_pick_a_prick = 0
        dimensions_piece_brut = dimensions.split("x")
        temp = dimensions_piece_brut
        dimensions_piece_brut = []
        for e in temp :
            while e.startswith(" ") :
                e = e[1:]
            while e.endswith(" ") :
                e = e[:-1]
            dimensions_piece_brut.append(e)
        assert len(dimensions_piece_brut) == 3
        dimensions_piece = []
        for dim in dimensions_piece_brut :
            dim = dim.split(" ")
            assert len(dim) in (1, 2)
            if len(dim) == 1 :
                dimensions_piece.append(int(dim[0]))
            else :
                assert dim[1] in ("1/3", "2/3")
                dimensions_piece.append(int(dim[0]) + {"1/3" : 1 / 3, "2/3" : 2 / 3}[dim[1]])
        volume_piece = dimensions_piece[0] * dimensions_piece[1] * dimensions_piece[2]
        quantite_mur_pick_a_prick = VOLUME_PICK_A_BRICK // volume_piece
    except :
        quantite_mur_pick_a_prick = None
    image_ref = api.get_image_ref_design(id_bricklink, id_rebrickable, get_liste_couleurs(transparence=transparent), {c : get_couleur_data(c) for c in get_liste_couleurs_id()})
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute('''
INSERT INTO Design
(id_design, id_lego, id_bricklink, id_rebrickable, nom, nom_lego, nom_bricklink, nom_rebrickable, dimensions_stud, dimensions_cm, categorie, masse, quantite_mur_pick_a_brick, image_ref)
VALUES
(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
''', (id_design, id_lego, id_bricklink, id_rebrickable, nom, nom_lego, nom_bricklink, nom_rebrickable, dimensions, bricklink_data["dimensions_cm"], categorie, bricklink_data["masse"], quantite_mur_pick_a_prick, image_ref))
    connexion.commit()
    connexion.close()

def ajouter_design(id_design:int, id_lego:int, id_bricklink:int, nom:str, nom_lego:str, nom_bricklink:str, dimensions:str, categorie:int, transparent:bool) -> bool :
    """
    entrées :
        id_design (int), id_lego (int), id_bricklink (str), nom (str), nom_lego (str), nom_bricklink (str), dimensions (str), categorie (int) et transparent (bool), les infos du design
    
    ajoute le design à la base de données
    si MODE_SANS_ECHEC est True, renvoie True si l'ajout a pu être effectué et False sinon
    sinon renvoie True
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    if MODE_SANS_ECHEC :
        try :
            __ajouter_design(connexion, curseur, id_design, id_lego, id_bricklink, nom, nom_lego, nom_bricklink, dimensions, categorie, transparent)
        except :
            connexion.close()
            return False
        else :
            return True
    else :
        __ajouter_design(connexion, curseur, id_design, id_lego, id_bricklink, nom, nom_lego, nom_bricklink, dimensions, categorie, transparent)
        return True

def __ajouter_piece(connexion:sqlite3.Connection, curseur:sqlite3.Cursor, id_piece:int, id_design:int, id_couleur:int, prix_site_lego:float) -> None :
    """
    entrées :
        connexion (sqlite3.Connect) et curseur (sqlite3.Cursor), la connexion à utiliser
        id_piece (int), id_design (int), id_couleur (int), prix_site_lego (float), les infos de la pièce
    
    ajoute la pièce à la base de données
    """
    assert not piece_in_database(id_piece)
    assert design_in_database(id_design)
    img = api.get_image_ref_piece(id_piece, id_design, id_couleur, get_design_info(id_design), get_couleur_data(id_couleur))
    connexion = sqlite3.connect(DATABASE_NAME)
    connexion2 = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    curseur2 = connexion2.cursor()
    curseur.execute('''INSERT INTO Piece (id_piece, id_design, id_couleur, prix_site_lego, image_ref) VALUES (?, ?, ?, ?, ?);''', (id_piece, id_design, id_couleur, prix_site_lego, img))
    curseur2.execute('''INSERT INTO Pieces (id_piece, quantite, disponible, endommagge) VALUES (?, 0, 0, 0);''', (id_piece,))
    connexion.commit()
    connexion2.commit()
    connexion.close()
    connexion2.close()
    

def ajouter_piece(id_piece:int, id_design:int, id_couleur:int, prix_site_lego:float) -> bool :
    """
    entrées :
        id_piece (int), id_design (int), id_couleur (int), prix_site_lego (float), les infos de la pièce
    
    ajoute la pièce à la base de données
    si MODE_SANS_ECHEC est True, renvoie True si l'ajout a pu être effectué et False sinon
    sinon renvoie True
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    if MODE_SANS_ECHEC :
        try :
            __ajouter_piece(connexion, curseur, id_piece, id_design, id_couleur, prix_site_lego)
        except :
            connexion.close()
            return False
        else :
            return True
    else :
        __ajouter_piece(connexion, curseur, id_piece, id_design, id_couleur, prix_site_lego)
        return True

def __ajouter_ton(connexion:sqlite3.Connection, curseur:sqlite3.Cursor, id_ton:int, nom:str, rgb_ref:str) -> None :
    """
    entrées :
        connexion (sqlite3.Connect) et curseur (sqlite3.Cursor), la connexion à utiliser
        id_ton (int), nom (str), rgb_ref (str), les infos du ton

    ajoute le ton à la base de données
    """
    assert not ton_in_database(id_ton)
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute('''INSERT INTO Tons (id_ton, nom, rgb_ref) VALUES (?, ?, ?);''', (id_ton, nom, rgb_ref))
    connexion.commit()
    connexion.close()

def ajouter_ton(id_ton:int, nom:str, rgb_ref:str) -> bool :
    """
    entrées :
        id_ton (int), nom (str), rgb_ref (str), les infos du ton

    ajoute le ton à la base de données
    si MODE_SANS_ECHEC est True, renvoie True si l'ajout a pu être effectué et False sinon
    sinon renvoie True
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    if MODE_SANS_ECHEC :
        try :
            __ajouter_ton(connexion, curseur, id_ton, nom, rgb_ref)
        except :
            connexion.close()
            return False
        else :
            return True
    else :
        __ajouter_ton(connexion, curseur, id_ton, nom, rgb_ref)
        return True
    
def __ajouter_couleur(connexion:sqlite3.Connection, curseur:sqlite3.Cursor, id_couleur:int, id_couleur_bricklink:int, id_couleur_rebrickable:int, nom:str, nom_lego:str, nom_bricklink:str, nom_rebrickable:str, id_ton:int, est_transparent:bool, image_ref:str) -> None :
    """
    entrées :
        connexion (sqlite3.Connect) et curseur (sqlite3.Cursor), la connexion à utiliser
        id_couleur (int), id_couleur_bricklink (int), id_couleur_rebrickable (int), nom (str), nom_lego (str), nom_bricklink (str), nom_rebrickable (str), id_ton (int), est_transparent (bool) et image_ref (str), les infos de la couleur

    ajoute la couleur à la base de données
    """
    assert ton_in_database(id_ton)
    assert couleur_is_new(id_couleur, id_couleur_bricklink, id_couleur_rebrickable)
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute('''INSERT INTO Couleurs (id_couleur, id_couleur_bricklink, id_couleur_rebrickable, nom, nom_lego, nom_bricklink, nom_rebrickable, ton, est_transparent, image_ref) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''', (id_couleur, id_couleur_bricklink, id_couleur_rebrickable, nom, nom_lego, nom_bricklink, nom_rebrickable, id_ton, str(est_transparent), image_ref))
    connexion.commit()
    connexion.close()

def ajouter_couleur(id_couleur:int, id_couleur_bricklink:int, id_couleur_rebrickable:int, nom:str, nom_lego:str, nom_bricklink:str, nom_rebrickable:str, id_ton:int, est_transparent:bool, image_ref:str) -> bool :
    """
    entrées :
        id_couleur (int), id_couleur_bricklink (int), id_couleur_rebrickable (int), nom (str), nom_lego (str), nom_bricklink (str), nom_rebrickable (str), ton (int), est_transparent (bool) et image_ref (str), les infos de la couleur

    ajoute la couleur à la base de données
    si MODE_SANS_ECHEC est True, renvoie True si l'ajout a pu être effectué et False sinon
    sinon renvoie True
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    if MODE_SANS_ECHEC :
        try :
            __ajouter_couleur(connexion, curseur, id_couleur, id_couleur_bricklink, id_couleur_rebrickable, nom, nom_lego, nom_bricklink, nom_rebrickable, id_ton, est_transparent, image_ref)
        except :
            connexion.close()
            return False
        else :
            return True
    else :
        __ajouter_couleur(connexion, curseur, id_couleur, id_couleur_bricklink, id_couleur_rebrickable, nom, nom_lego, nom_bricklink, nom_rebrickable, id_ton, est_transparent, image_ref)
        return True

def __auto_insert_pieces_du_set(id_set, i, l) -> list :
    """
    id_set (int), id du set

    ajoute les pièces au set dans la base de données
    renvoie la liste des pièces du set qui ne sont pas déjà dans la base de données sous la forme d'une liste de dictionnaires :
    {design : les infos du design (dict), couleur : les infos de la couleur (dict)}

    les infos du design sont de la forme :
    {statut : "find", id_design : l'id du design} si le design est présent dans la base de données
    {statut : "unknown", "id_lego" : list, "id_bricklink" : str, "id_rebrickable" : str, "nom_rebrickable" : str} sinon

    les infos de la couleur sont de la forme :
    {statut : "find", id_couleur : l'id de la couleur} si la couleur est présente dans la base de données
    {statut : "unknown", nom_lego : list, id_bricklink : int, nom_bricklink : str, id_rebrickable : int, nom_rebrickable : str} sinon
    """
    
    def __find_piece_id_by_rebrickable_infos(part_num:str, color_id:int) -> int :
        """
        entrées :
            part_num (str), l'id rebrickable du design
            color_id (int), id rebrickable de la couleur

        renvoie l'id de la pièce correspondante si elle est présente dans la base de données et None sinon
        """
        connexion = sqlite3.connect(DATABASE_NAME)
        curseur = connexion.cursor()
        curseur.execute('''SELECT p.id_piece FROM Piece as p JOIN Design as d JOIN Couleurs as c ON p.id_design = d.id_design AND p.id_couleur = c.id_couleur WHERE d.id_rebrickable = ? AND c.id_couleur_rebrickable = ?;''', (part_num, color_id))
        r = []
        for e in curseur :
            r.append(e[0])
        connexion.close()
        if len(r) == 0 :
            return None
        else :
            return r[0]

    def __find_design_id_by_rebrickable_infos(part_num:str) -> int :
        """
        part_num (str) l'id rebrickable de la pièce
        
        renvoie l'id du design correspondant si il est présent dans la base de données et None sinon
        """
        connexion = sqlite3.connect(DATABASE_NAME)
        curseur = connexion.cursor()
        curseur.execute('''SELECT id_design FROM Design WHERE id_rebrickable = ?;''', (part_num,))
        r = []
        for e in curseur :
            r.append(e[0])
        connexion.close()
        if len(r) == 0 :
            return None
        else :
            return r[0]
        
    def __find_color_id_by_rebrickable_infos(color_id:int) -> int :
        """
        color_id (int), id rebrickable de la couleur

        renvoie l'id de la couleur correspondante si elle est présente dans la base de données et None sinon
        """
        connexion = sqlite3.connect(DATABASE_NAME)
        curseur = connexion.cursor()
        curseur.execute('''SELECT id_couleur FROM Couleurs WHERE id_couleur_rebrickable = ?;''', (color_id,))
        r = []
        for e in curseur :
            r.append(e[0])
        connexion.close()
        if len(r) == 0 :
            return None
        else :
            return r[0]

    liste_part = api.get_liste_parts_in_set(id_set)
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    r = []
    for part in tqdm(liste_part) :    # part : tuple (part_num rebrickable, color_id rebrickable, quantité)
        sleep(1)
        id_piece = __find_piece_id_by_rebrickable_infos(part[0], part[1])
        # print(part)
        if id_piece == None :
            infos = {}
            id_design = __find_design_id_by_rebrickable_infos(part[0])
            if id_design == None :
                infos["design"] = api.get_part_infos(part[0])
                infos["design"]["statut"] = "unknown"
            else :
                infos["design"] = {"statut" : "find", "id_design" : id_design}
            id_couleur = __find_color_id_by_rebrickable_infos(part[1])
            if id_couleur == None :
                infos["couleur"] = api.get_color_infos(part[1])
                infos["couleur"]["statut"] = "unknown"
            else :
                infos["couleur"] = {"statut" : "find", "id_couleur" : id_couleur}
            infos["quantite"] = part[2]
            r.append(infos)
        else :
            curseur.execute('''INSERT INTO piece_dans_set (id_set, id_piece, quantite) VALUES (?, ?, ?);''', (id_set, id_piece, part[2]))
    connexion.commit()
    connexion.close()
    return r

def auto_insert_pieces_du_set(id_set, i, l) :
    return __auto_insert_pieces_du_set(id_set, i, l)

def __ajouter_set(connexion:sqlite3.Connection, curseur:sqlite3.Cursor, id_set:int, nom_anglais:str, nom_français:str, id_gamme:str, annee:int, nb_pieces:int, tranche_age:str, lien_amazon:str) -> None :
    """
    entrées :
        connexion (sqlite3.Connect) et curseur (sqlite3.Cursor), la connexion à utiliser
        id_set (int), nom_anglais (str), nom_français (str), id_gamme (str), image_ref (str), annee (int), nb_pieces (int), tranche_age (str) et lien_amazon (str), les infos du set

    ajoute le set à la base de données
    """
    assert not set_in_database(id_set)
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute('''INSERT INTO Sets (id_set, nom_anglais, nom_français, gamme, image_ref, annee, nb_pieces, tranche_age, lien_amazon) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);''', (id_set, nom_anglais, nom_français, id_gamme, api.get_image_ref_set(id_set), annee, nb_pieces, tranche_age, lien_amazon))
    connexion.commit()
    connexion.close()
    liste_pieces_unknown = __auto_insert_pieces_du_set(id_set)
    save_json(liste_pieces_unknown, f"/data_save/piece_in_set_data/{id_set}.json")

def ajouter_set(id_set:int, nom_anglais:str, nom_français:str, id_gamme:str, annee:int, nb_pieces:int, tranche_age:str, lien_amazon:str) -> bool :
    """
    entrées :
        id_set (int), nom_anglais (str), nom_français (str), id_gamme (str), image_ref (str), annee (int), nb_pieces (int), tranche_age (str) et lien_amazon (str), les infos du set

    ajoute le set à la base de données
    si MODE_SANS_ECHEC est True, renvoie True si l'ajout a pu être effectué et False sinon
    sinon renvoie True
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    if MODE_SANS_ECHEC :
        try :
            __ajouter_set(connexion, curseur, id_set, nom_anglais, nom_français, id_gamme, annee, nb_pieces, tranche_age, lien_amazon)
        except :
            connexion.close()
            return False
        else :
            return True
    else :
        __ajouter_set(connexion, curseur, id_set, nom_anglais, nom_français, id_gamme, annee, nb_pieces, tranche_age, lien_amazon)
        return True

def __ajouter_minifig(connexion:sqlite3.Connection, curseur:sqlite3.Cursor, id_minifig:int, id_rebrickable:str, nom:str, id_gamme:str) -> None :    #, image_ref:str
    """
    entrées :
        connexion (sqlite3.Connect) et curseur (sqlite3.Cursor), la connexion à utiliser
        id_minifig (str), id_rebrickable (str), nom (str) et id_gamme (str), les infos de la minifig

    ajoute la minifig à la base de données
    """
    assert not minifig_in_database(id_minifig)
    assert minifig_is_new(id_minifig, id_rebrickable)
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    connexion2 = sqlite3.connect(MOC)
    curseur2 = connexion2.cursor()
    curseur.execute('''INSERT INTO Minifigures (id_minifig, id_rebrickable, nom, gamme, image_ref) VALUES (?, ?, ?, ?, ?);''', (id_minifig, id_rebrickable, nom, id_gamme, api.get_image_ref_minifig(id_minifig, id_rebrickable)))
    curseur2.execute('''INSERT INTO Minifigs VALUES (?, 0);''', (id_minifig,))
    connexion.commit()
    connexion2.commit()
    connexion.close()
    connexion2.close()

def ajouter_minifig(id_minifig:int, id_rebrickable:str, nom:str, id_gamme:str) -> bool :    #, image_ref:str
    """
    entrées :
        id_minifig (str), id_rebrickable (str), nom (str) et id_gamme (str), les infos de la minifig

    ajoute la minifig à la base de données
    si MODE_SANS_ECHEC est True, renvoie True si l'ajout a pu être effectué et False sinon
    sinon renvoie True
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    if MODE_SANS_ECHEC :
        try :
            __ajouter_minifig(connexion, curseur, id_minifig, id_rebrickable, nom, id_gamme)
        except :
            connexion.close()
            return False
        else :
            return True
    else :
        __ajouter_minifig(connexion, curseur, id_minifig, id_rebrickable, nom, id_gamme)
        return True

def __ajouter_gamme(connexion:sqlite3.Connection, curseur:sqlite3.Cursor, id_gamme:str, nom_gamme:str) -> None :
    """
    entrées :
        connexion (sqlite3.Connect) et curseur (sqlite3.Cursor), la connexion à utiliser
        id_gamme (str) et nom_gamme (str), les infos de la gamme

    ajoute la gamme à la base de données
    """
    assert not gamme_in_database(id_gamme)
    curseur.execute('''INSERT INTO Gammes (id_gamme, nom_gamme) VALUES (?, ?);''', (id_gamme, nom_gamme))
    connexion.commit()
    connexion.close()

def ajouter_gamme(id_gamme:str, nom_gamme:str) -> bool :
    """
    entrées :
        id_gamme (str) et nom_gamme (str), les infos de la gamme

    ajoute la gamme à la base de données
    si MODE_SANS_ECHEC est True, renvoie True si l'ajout a pu être effectué et False sinon
    sinon renvoie True
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    if MODE_SANS_ECHEC :
        try :
            __ajouter_gamme(id_gamme, nom_gamme)
        except :
            connexion.close()
            return False
        else :
            return True
    else :
        __ajouter_gamme(id_gamme, nom_gamme)
        return True



def __ajouter_exemplaire(connexion:sqlite3.Connection, curseur:sqlite3.Cursor, id_set:int, date_achat:str, statut:str) -> None :
    """
    entrées :
        connexion (sqlite3.Connect) et curseur (sqlite3.Cursor), la connexion à utiliser
        id_set (int), date_achat (str), statut ("construit" ou "détruit"), les infos de l'exemplaire

    ajoute l'exemplaire à la collection
    """
    assert statut in ("construit", "détruit")
    curseur.execute('''INSERT INTO Sets (id_set, date_achat, statut) VALUES (?, ?, ?);''', (id_set, date_achat, statut))
    connexion.commit()
    connexion.close()

def ajouter_exemplaire(id_set:int, date_achat:str, statut:str) -> bool :
    """
    entrées :
        id_set (int), date_achat (str), statut ("construit" ou "détruit"), les infos de l'exemplaire

    ajoute l'exemplaire à la collection
    si MODE_SANS_ECHEC est True, renvoie True si l'ajout a pu être effectué et False sinon
    sinon renvoie True
    """
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    if MODE_SANS_ECHEC :
        try :
            __ajouter_exemplaire(connexion, curseur, id_set, date_achat, statut)
        except :
            connexion.close()
            return False
        else :
            return True
    else :
        __ajouter_exemplaire(connexion, curseur, id_set, date_achat, statut)
        return True