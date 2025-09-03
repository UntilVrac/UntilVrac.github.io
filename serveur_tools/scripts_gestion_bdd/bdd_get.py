from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
path.append(BRICKSTOCK_PATH)

import sqlite3
from os import remove
from serveur_tools.scripts_gestion_bdd.admin_bdd import *
from serveur_tools.scripts_gestion_bdd.bdd_verif import *
from serveur_tools.scripts_gestion_bdd.bdd_count import *
import serveur_tools.scrap_data as scrap
import serveur_tools.requetes_api as api
from serveur_tools.json_tools import save_json, upload_json

def get_id_categorie(nom:str) -> int :
    """
    nom (str), nom de la catégorie

    renvoie l'id de la catégorie la plus précise portant ce nom
    renvoie None si aucune catégorie ne porte ce nom
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    r = []
    curseur.execute('''SELECT id_categorie FROM Categories WHERE nom = ?;''', (nom,))
    for e in curseur :
        r.append(e[0])
    if len(r) == 0 :
        r = None
    elif len(r) == 1 :
        r = r[0]
    else :
        r = max(r)
    connexion.close()
    return r

def get_liste_id_categories() -> list :
    """
    renvoie la liste des id_categories
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute('''SELECT id_categorie FROM Categories;''')
    r = []
    for e in curseur :
        r.append(e[0])
    connexion.close()
    return r

def get_liste_categories_dict() -> list :
    """
    renvoie une liste de dictionnaires {id_categorie : liste des id des sous_catégories}
    """
    liste_cat = get_liste_id_categories()
    liste_cat_dict = {}
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    for cat in liste_cat :
        curseur.execute('''SELECT id_categorie FROM Categories WHERE categorie_sup = ?;''', (cat,))
        r = []
        for e in curseur :
            r.append(e[0])
        liste_cat_dict[cat] = r
    connexion.close()
    return liste_cat_dict

def get_categorie_sup(cat:int) -> int :
        """
        cat (int), id de la catégorie

        renvoie l'id de la catégorie parente de cette catégorie
        renvoie -1 si la catégorie n'a pas de catégorie parente
        renvoie None si aucune catégorie ne porte cet id
        """
        if not categorie_in_database(cat) :
            return None
        connexion = sqlite3.connect(DATABASE_NAME)
        curseur = connexion.cursor()
        curseur.execute('''SELECT categorie_sup FROM Categories WHERE id_categorie = ?;''', (cat,))
        r = []
        for e in curseur :
            r.append(e[0])
        connexion.close()
        assert len(r) == 1
        if r[0] == None :
            return -1
        else :
            return r[0]

def get_liste_sous_categories(id_categorie:int, direct:bool=True) -> list :
    """
    entrées :
        id_categorie (int), id de la catégorie
        direct (bool)

    renvoie la liste des id des sous catégories de cette catégorie (uniquement les id des sous-catégories directes si direct est True ou les id de toutes les sous-catégories si direct est False)
    """
    if direct :
        connexion = sqlite3.connect(DATABASE_NAME)
        curseur = connexion.cursor()
        curseur.execute('''SELECT id_categorie FROM Categories WHERE categorie_sup = ?;''', (id_categorie,))
        r = []
        for e in curseur :
            r.append(e[0])
        connexion.close()
        return r
    else :
        r = get_liste_sous_categories(id_categorie, direct=True)
        sc = r
        for id in r :
            sc += get_liste_sous_categories(id, direct=False)
        return r

def get_infos_categorie(id_categorie:int) -> dict :
    """
    id_categorie : l'id de la catégorie
    
    renvoie le dictionnaire {id_categorie : int, nom_categorie : str, id_categorie_sup : int, image_ref : str, liste_sous_categories : list} correspondant (avec liste_sous_categories, la liste des id des sous-catégories directes de cette catégorie) ou None si la catégorie n'existe pas
    renvoie None si la catégorie n'existe pas
    """
    print(id_categorie)
    if not categorie_in_database(id_categorie) :
        return None
    else :
        connexion = sqlite3.connect(DATABASE_NAME)
        curseur = connexion.cursor()
        curseur.execute('''SELECT id_categorie, nom, categorie_sup, image_ref FROM Categories WHERE id_categorie = ?;''', (id_categorie,))
        r = []
        for e in curseur :
            r.append(e)
        connexion.close()
        return {"id_categorie" : e[0], "nom_categorie" : e[1], "id_categorie_sup" : e[2], "liste_sous_categories" : get_liste_sous_categories(id_categorie), "image_ref" : e[3]}

def get_categorie_racine(cat:int) -> int :
    """
    cat (int), id de la catégorie

    renvoie l'id de la catégorie racine de cette catégorie
    renvoie -1 si cette catégorie est sa propre racine
    renvoie None si aucune catégorie ne porte cet id
    """
    if not categorie_in_database(cat) :
        return None
    cat_path = []
    cat_sup = get_categorie_sup(cat)
    while cat_sup != -1 :
        cat_path.append(cat_sup)
        cat_sup = get_categorie_sup(cat_sup)
    if cat_path == [] :
        return -1
    else :
        return cat_path[-1]
    
def get_liste_categories_racines() -> list :
    """
    renvoie la liste des id des catégories racines
    """
    return [e for e in get_liste_id_categories() if get_categorie_racine(e) == -1]

def get_masse_of_piece(id_design:int) -> float :
    """
    id_design : id du design de la pièce
    
    renvoie la masse de ce design
    renvoie None si le design n'existe pas
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute('''SELECT masse FROM Design WHERE id_design = ?;''', (id_design,))
    r = []
    for e in curseur :
        r.append(e[0])
    if len(r) == 0 :
        r = None
    else :
        assert len(r) == 1
        r = r[0]
    connexion.close()
    return r

def get_liste_tons() -> list :
    """
    renvoie la liste des tons sous la forme d'une liste de dictionnaires {id_ton : int, nom_ton : str, rgb_ref : str}
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute('''SELECT id_ton, nom, rgb_ref FROM Tons ORDER BY id_ton;''')
    r = []
    for e in curseur :
        r.append({"id_ton" : e[0], "nom_ton" : e[1], "rgb_ref" : e[2]})
    connexion.close()
    return r

def get_liste_couleurs(transparence:bool=None) -> dict :
    """
    transparence (bool ou None), défini un filtre de recherche : si transparence est True, seules les couleurs transparentes seront renvoyées, si transparence est False, seules et couleurs opaques seront renvoyées et si transparence est None, toutes les couleurs seront renvoyées

    renvoie le dictionnaire {id_ton : liste des id des couleurs de ce ton}
    """
    if transparence == None :
        filtre_transparence = ""
    elif transparence == True :
        filtre_transparence = ' AND est_transparent = "True"'
    else :
        filtre_transparence = ' AND est_transparent = "False"'
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    r = {}
    for t in get_liste_tons() :
        r[t["id_ton"]] = []
        curseur.execute(f'''SELECT id_couleur FROM Couleurs WHERE ton = ?{filtre_transparence} ORDER BY id_couleur;''', (t["id_ton"],))
        for e in curseur :
            r[t["id_ton"]].append(e[0])
    connexion.close()
    return r

def get_liste_couleurs_id(transparence:bool=None) -> list :
    """
    transparence (bool ou None), défini un filtre de recherche : si transparence est True, seules les couleurs transparentes seront renvoyées, si transparence est False, seules et couleurs opaques seront renvoyées et si transparence est None, toutes les couleurs seront renvoyées

    renvoie la liste des id des couleurs correspondantes
    """
    liste = []
    dico_couleurs = get_liste_couleurs(transparence=transparence)
    for t in dico_couleurs :
        liste += dico_couleurs[t]
    return liste

def get_couleur_data(id_couleur:int) -> tuple :
    """
    id_couleur (int), l'id de la couleur

    renvoie le dictionnaire, {id_couleur : int, id_bricklink : str, id_rebrickable : str, nom : str, nom_lego : str, nom_bricklink : str, nom_rebrickable : str, id_ton : int, est_transparent : bool, image_ref : str} correspondant
    renvoie None si la couleur n'existe pas
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    r = []
    curseur.execute('''SELECT id_couleur, id_couleur_bricklink, id_couleur_rebrickable, nom, nom_lego, nom_bricklink, nom_rebrickable, ton, est_transparent, image_ref FROM Couleurs WHERE id_couleur = ?;''', (id_couleur,))
    for e in curseur :
        r.append({
            "id_couleur" : e[0], 
            "id_bricklink" : e[1], 
            "id_rebrickable" : e[2], 
            "nom" : e[3], 
            "nom_lego" : e[4], 
            "nom_bricklink" : e[5], 
            "nom_rebrickable" : e[6], 
            "id_ton" : e[7], 
            "est_transparent" : {"True" : True, "False" : False}[e[8]], 
            "image_ref" : e[9]
        })
    connexion.close()
    if r == [] :
        return {}
    else :
        assert len(r) == 1
        return r[0]

def get_liste_sets_for_minifig(id_minifig:str) -> list :
    """
    id_minifig (str), id de la minifig

    renvoie la liste des sets contenant la minifig référencés sous la forme de listes [id_set, nom_anglais, nom_français]
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    r = []
    curseur.execute('''SELECT s.id_set, s.nom_anglais, s.nom_français FROM Sets as s JOIN minifig_dans_set as ms ON s.id_set = ms.id_set WHERE ms.id_minifig = ?;''', (id_minifig,))
    for e in curseur :
        r.append(list(e))
    connexion.close()
    return r

def get_liste_gammes_list() -> list :
    """
    renvoie la liste des gammes sous la forme d'une liste de tuples (id_gamme, nom_gamme)
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    r = []
    curseur.execute('''SELECT id_gamme, nom_gamme FROM Gammes ORDER nom_gamme;''')
    for e in curseur :
        r.append(e)
    connexion.close()
    return r

def get_liste_gammes_dict(racine:str=None) -> list :
    """
    racine (str), l'id de la gamme racine (None par défaut)

    renvoie la liste des gammes sous la forme d'une de dictionnaire {"id_gamme" : str, "nom_gamme" : str, "sous_gammes" : list} ou chaque dictionnaire correspond à une gamme ou sous-gamme
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    r = []
    if racine == None :
        curseur.execute('''SELECT id_gamme, nom_gamme FROM Gammes WHERE id_gamme_parente is NULL ORDER nom_gamme;''')
    else :
        curseur.execute('''SELECT id_gamme, nom_gamme FROM Gammes WHERE id_gamme_parente = ? ORDER nom_gamme;''', (racine,))
    for e in curseur :
        r.append({"id_gamme" : e[0], "nom_gamme" : e[1]})
    # print(r)
    connexion.close()
    for e in r :
        e["sous_gammes"] = get_liste_gammes_dict(e["id_gamme"])
    return r

def get_liste_sous_gammes(id_gamme:str) -> tuple :
    """
    id_gamme (str), l'id de la gamme

    renvoie la liste des id de ses sous-gammes sous la forme d'un tuple
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute('''SELECT id_gamme FROM Gammes WHERE id_gamme_parente = ? ORDER nom_gamme;''', (id_gamme,))
    r = []
    for e in curseur :
        r.append(e[0])
    connexion.close()
    r = tuple(r)
    for e in r :
        r += get_liste_sous_gammes(e)
    return r

def get_liste_annees_for_set() -> list :
    """
    renvoie la liste des années (int) des sets sans doublons et triée dans l'ordre décroissant
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    r = []
    curseur.execute('''SELECT DISTINCT annee FROM Sets ORDER BY annee DESC;''')
    for e in curseur :
        r.append(e[0])
    connexion.close()
    return r

def get_set_data(id_set:int) -> dict :
    """
    id_set (int), id du set

    renvoie le dictionnaire {id_set : int, nom_anglais : str, nom_français : str, id_gamme : str, nom_gamme : str, image_ref : str, annee : int, nb_pieces : int, tranche_age : str, lien_amazon : str} correspondant
    """
    assert set_in_database(id_set)
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute('''SELECT s.id_set, s.nom_anglais, s.nom_français, g.id_gamme, g.nom_gamme, s.image_ref, s.annee, s.nb_pieces, s.tranche_age, s.lien_Amazon FROM Sets as s JOIN Gammes as g ON s.gamme = g.id_gamme WHERE s.id_set = ?;''', (id_set,))
    r = []
    for e in curseur :
        item = {
            "id_set" : e[0], 
            "nom_anglais" : e[1], 
            "nom_français" : e[2], 
            "id_gamme" : e[3], 
            "gamme" : e[4], 
            "image_ref" : e[5], 
            "annee" : e[6], 
            "nb_pieces" : e[7], 
            "tranche_age" : e[8], 
            "lien_amazon" : e[9]
        }
        r.append(item)
    if len(r) != 1 :
        print(id_set, len(r))
    assert len(r) == 1
    return r[0]

def get_minifig_in_set(id_set:int) -> list :
    """
    id_set (int), id du set
    
    renvoie la liste de des minifigs du set sous la forme d'une liste de dictionnaires {id_minifig : str, nom : str, image_ref : str, quantite : int} 
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    r = []
    curseur.execute('''
SELECT m.id_minifig, m.nom, m.image_ref, ms.quantite
FROM Minifigures as m JOIN minifig_dans_set as ms
ON m.id_minifig = ms.id_minifig
WHERE ms.id_set = ?;
''', (id_set,))
    for e in curseur :
        r.append({"id_minifig" : e[0], "nom" : e[1], "image_ref" : e[2], "quantite" : e[3]})
    connexion.close()
    return r

def get_minifig_data(id_minifig:int) -> list :
    """
    id_minifig (str), id de la minifigure

    renvoie le dictionnaire {id_minifig : str, id_rebrickable : str, nom : str, id_gamme : str, nom_gamme : str, image_ref : str} correspondant
    """
    assert minifig_in_database(id_minifig)
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    r = []
    curseur.execute('''SELECT m.id_minifig, m.id_rebrickable, m.nom, g.id_gamme, g.nom_gamme, m.image_ref FROM Minifigures as m JOIN Gammes as g ON m.gamme = g.id_gamme WHERE m.id_minifig = ?;''', (id_minifig,))
    for e in curseur :
        r.append({
            "id_minifig" : e[0], 
            "id_rebrickable" : e[1], 
            "nom" : e[2], 
            "id_gamme" : e[3], 
            "nom_gamme" : e[4], 
            "image_ref" : e[5], 
            "quantite" : get_minifig_quantity_from_moc(e[0]), 
            "sets" : get_liste_sets_for_minifig(e[0])
        })
    connexion.close()
    assert len(r) == 1
    return r[0]

def get_quantite_minifig_in_set(id_minifig:str, id_set:int) -> int :
    """
    entrées :
        id_minifig (str), id de la minifig
        id_set (int), id du set

    renvoie le nombre d'exemplaires de cette minifig présents dans ce set
    """
    assert minifig_in_database(id_minifig)
    assert set_in_database(id_set)
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    r = []
    curseur.execute('''SELECT quantite FROM minifig_dans_set WHERE id_set = ? AND id_minifig = ?;''', (id_set, id_minifig))
    for e in curseur :
        r.append(e[0])
    connexion.close()
    assert len(r) in (0, 1)
    if len(r) == 1 :
        return r[0]
    else :
        return 0

def get_piece_info(id_piece:int) -> dict :
    """
    id_piece (int), id de la pièce

    renvoie le dictionnaire {id_piece : int, id_lego : int, id_design : int, nom : str, id_categorie : int, nom_categorie : str, dimensions : str, masse : float, id_couleur : int, couleur : str, image_ref : str, quantite : int, disponible : int, endommagee : int, categorie_span : str} correspondant
    """
    # prix_site_lego : float, prix_mur_pick_a_brick : float, prix_legoland : float, prix_bricklink : tuple (prix min, prix moy, prix max), 
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute('''SELECT p.id_piece, p.id_design, d.nom, cat.id_categorie, cat.nom, d.dimensions_stud, d.dimensions_cm, d.masse, col.id_couleur, col.nom, p.image_ref, p.prix_site_lego, d.quantite_mur_pick_a_brick
FROM Piece as p JOIN Design as d JOIN Couleurs as col JOIN Categories as cat JOIN Tons as t
ON p.id_design = d.id_design AND p.id_couleur = col.id_couleur AND d.categorie = cat.id_categorie AND t.id_ton = col.ton
WHERE p.id_piece = ?;''', (id_piece,))
    r = []
    for e in curseur :
        dict_item = {
            "id_piece" : e[0], 
            "id_design" : e[1], 
            "nom" : e[2], 
            "id_categorie" : e[3], 
            "nom_categorie" : e[4], 
            "dimensions_stud" : e[5], 
            'dimensions_cm' : e[6], 
            "masse" : e[7], 
            "id_couleur" : e[8], 
            "nom_couleur" : e[9], 
            "image_ref" : e[10], 
            # "prix_site_lego" : e[11]
        }
        # dict_item["prix_site_lego"] = scrap.get_prix_piece_site_lego(dict_item["id_lego"])
        # dict_item["prix_mur_pick_a_brick"] = round(PRIX_PICK_A_BRICK / e[12], 2)
        # dict_item["prix_legoland"] = round(PRIX_LEGOLAND * dict_item["masse"] / 100, 2)
        # dict_item["prix_bricklink"] = scrap.get_prix_piece(dict_item["id_piece"])
        if piece_est_dans_moc(dict_item["id_piece"]) :
            moc_data = get_piece_data_from_moc(dict_item["id_piece"])
            dict_item["quantite"], dict_item["disponible"], dict_item["endommagee"] = moc_data["quantite"], moc_data["disponible"], moc_data["endommagee"]
        else :
            dict_item["quantite"], dict_item["disponible"], dict_item["endommagee"] = 0, 0, 0
        r.append(dict_item)
    connexion.close()
    assert len(r) == 1
    r = r[0]
    cat_id = get_categorie_racine(r["id_categorie"])
    if cat_id == -1 :
        span = f'<a href="http://localhost:1520/BrickStock/pieces?categorie={r["id_categorie"]}">{r["nom_categorie"]}</a>'
    else :
        cat = get_infos_categorie(cat_id)
        span = f'<a href="http://localhost:1520/BrickStock/pieces?categorie={cat["id_categorie"]}>{cat["nom_categorie"]}</a> > <a href="http://localhost:1520/BrickStock/pieces?categorie={r["id_categorie"]}">{r["nom_categorie"]}</a>'
    r["categorie_span"] = span
    return r

def get_design_info(id_design:int) -> dict :
    """
    id_design (int), id du design

    renvoie le dictionnaire {id_design : int, id_lego : str, id_bricklink : str, id_rebrickable : str, nom : str, nom_lego : str, nom_bricklink : str, nom_rebrickable : str, dimensions_stud : str, dimensions_cm : str, id_categorie : int, nom_categorie : str, masse : float, quantite_mur_pick_a_brick : int, image_ref : str} correspondant
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute("""
SELECT d.id_design, d.id_lego, d.id_bricklink, d.id_rebrickable, d.nom, d.nom_lego, d.nom_bricklink, d.nom_rebrickable, d.dimensions_stud, d.dimensions_cm, c.id_categorie, c.nom, d.masse, d.quantite_mur_pick_a_brick, d.image_ref
FROM Design as d JOIN Categories as c ON d.categorie = c.id_categorie
WHERE d.id_design = ?;
""", (id_design,))
    r = []
    for e in curseur :
        dict_item = {
            "id_design" : e[0], 
            "id_lego" : e[1], 
            "id_bricklink" : e[2], 
            "id_rebrickable" : e[3], 
            "nom" : e[4], 
            "nom_lego" : e[5], 
            "nom_bricklink" : e[6], 
            "nom_rebrickable" : e[7], 
            "dimensions_stud" : e[8], 
            "dimensions_cm" : e[9], 
            "id_categorie" : e[10], 
            "nom_categorie" : e[11], 
            "masse" : e[12], 
            "quantite_mur_pick_a_brick" : e[13], 
            "image_ref" : e[14]
        }
        r.append(dict_item)
    connexion.close()
    assert len(r) == 1
    r = r[0]
    cat_id = get_categorie_racine(r["id_categorie"])
    if cat_id == -1 :
        span = f'<a href="http://localhost:1520/BrickStock/designs?categorie={r["id_categorie"]}">{r["nom_categorie"]}</a>'
    else :
        print(cat_id)
        cat = get_infos_categorie(cat_id)
        span = f'<a href="http://localhost:1520/BrickStock/designs?categorie={cat["id_categorie"]}>{cat["nom_categorie"]}</a> > <a href="http://localhost:1520/BrickStock/designs?categorie={r["id_categorie"]}">{r["nom_categorie"]}</a>'
    r["categorie_span"] = span
    return r

def __update_piece_unknown_in_set(id_set:int) -> None :
    """
    id_set (int), l'id du set

    met à jour la liste des pièces du set et celle des pièces inconnues
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
        curseur.execute('''SELECT id_couleur FROM Couleurs WHERE id_couleur_rebrickable = ?;''', (color_id))
        r = []
        for e in curseur :
            r.append(e[0])
        connexion.close()
        if len(r) == 0 :
            return None
        else :
            return r[0]

    filename = f"/data_save/piece_in_set_data/{id_set}.json"
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    json_data = upload_json(filename)
    if json_data != None :
        liste_part = []
        for part in json_data :
            find_design, find_color = False, False
            if part["design"]["statut"] == "find" :
                id_design = part["design"]["id_design"]
                assert type(id_design) == int
                find_design = True
            else :
                infos = {}
                infos["design"] = api.get_part_infos(part[0])
                infos["design"]["statut"] = "unknown"
            if part["couleur"]["statut"] == "find" :
                id_couleur = part["couleur"]["id_couleur"]
                assert type(id_couleur) == int
                find_color = True
            else :
                infos = {}
                infos["couleur"] = api.get_color_infos(part[1])
                infos["couleur"]["statut"] = "unknown"
            if find_design and find_color :
                quantite = part["quantite"]
                assert type(quantite) == int
                assert quantite > 0
                curseur.execute('''SELECT id_piece FROM Piece WHERE id_design = ? AND id_couleur = ?;''', (id_design, id_couleur))
                r = []
                for e in curseur :
                    r.append(e[0])
                assert len(r) >= 1
                curseur.execute('''INSERT INTO piece_dans_set (id_set, id_piece, quantite) VALUES (?, ?, ?);''', (id_set, r[0], quantite))
            else :
                liste_part.append(part)
        connexion.commit()
        connexion.close()
        if len(liste_part) == 0 :
            remove(filename)
        else :
            save_json(liste_part, filename)

def get_piece_in_set(id_set:int) -> list :
    """
    id_set (int), l'id du set

    renvoie la liste des pièces du set sous la forme d'une liste de tuples (id pièce, quantité)
    """
    __update_piece_unknown_in_set(id_set)
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    r = []
    curseur.execute('''SELECT id_piece, quantite FROM piece_dans_set WHERE id_set = ?;''', (id_set,))
    for e in curseur :
        r.append((e[0], e[1]))
    connexion.close()
    return r

def get_gamme_info(id_gamme:str) -> dict :
    """
    id_gamme (str), id de la gamme

    renvoie le dictionnaire {id_gamme : str, nom_gamme : str} correspondant
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute('''SELECT nom_gamme FROM Gammes WHERE id_gamme = ?;''', (id_gamme,))
    r = []
    for e in curseur :
        r.append(e[0])
    connexion.close()
    assert len(r) <= 1
    if len(r) == 1 :
        return {"id_gamme" : id_gamme, "nom_gamme" : r[0]}
    else :
        return {}

def get_element_type(id_element:int) -> str :
    """
    id_element (int), id de l'élément

    renvoie "pièce" si l'id correspond à une pièce, "design" si l'id correspond à un design et None si aucun élément ne porte cet id
    """
    if piece_in_database(id_element) :
        return "pièce"
    elif design_in_database(id_element) :
        return "design"
    else :
        return None



def get_piece_data_from_moc(id_piece:int) -> dict :
    """
    id_piece (int), id de la pièce

    renvoie le dictionnaire {id_piece : int, quantite : int, disponible : int, endommagee : int} correspondant
    """
    assert piece_est_dans_moc(id_piece)
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    curseur.execute('''SELECT quantite, disponible, endommagee FROM Pieces WHERE id_piece = ?;''', (id_piece,))
    r = []
    for e in curseur :
        r.append({"id_piece" : id_piece, "quantite" : e[0], "disponible" : e[1], "endommagee" : e[2]})
    connexion.close()
    assert len(r) == 1
    return r[0]

def get_set_data_from_moc(id_set:int) -> list :
    """
    id_set (int), id du set

    renvoie la liste des exemplaires du set sous la forme d'une liste de dictionnaires {id_exemplaire : int, id_set : int, date_achat : str, statut : ("construit" ou "détruit")}
    """
    if count_exemplaires_in_moc(id_set) == 0 :
        return []
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    curseur.execute('''SELECT id_exemplaire, date_achat, statut FROM Sets WHERE id_set = ?;''', (id_set,))
    r = []
    for e in curseur :
        r.append({"id_exemplaire" : e[0], "id_set" : id_set, "date_achat" : e[1], "statut" : e[2]})
    connexion.close()
    return r

def get_minifig_quantity_from_moc(id_minifig:str) -> int :
    """
    id_minifig (str), id de la minifig

    renvoie le nombre d'exemplaire de cette minifig en stock dans la collection
    """
    assert minifig_est_dans_moc(id_minifig)
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    curseur.execute('''SELECT nb_exemplaires FROM Minifigs WHERE id_minifig = ?;''', (id_minifig,))
    r = []
    for e in curseur :
        r.append(e[0])
    connexion.close()
    assert len(r) == 1
    return r[0]

def get_rangements_infos(id_rangement:int) -> dict :
    """
    id_rangement (int), id du rangement

    renvoie les infos du rangement sous la forme d'un dictionnaire {"id_rangement" : int, "nom_rangement" : str, "type_rangement" : str, "nb_compartiments" : int, "compartimentation" : str} si le rangement existe et None sinon
    """
    if id_rangement in (None, 0) :
        return {"id_rangement" : 0, "nom_rangement" : "Collection", "type_rangement" : None, "nb_compartiments" : float("inf"), "compartimentation" : "inf x inf"}
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    curseur.execute('''SELECT nom_rangement, type_rangement, nb_compartiments, compartimentation FROM Rangements_physiques WHERE id_rangement = ?;''', (id_rangement,))
    r = []
    for e in curseur :
        r.append({
            "id_rangement" : id_rangement, 
            "nom_rangement" : e[0], 
            "type_rangement" : e[1], 
            "nb_compartiments" : e[2], 
            "compartimentation" : e[3]
        })
    connexion.close()
    if len(r) == 0 :
        return None
    else :
        return r[0]
    
def get_arbre_rangements(id_racine:int=None) -> dict :
    """
    id_racine (int), l'id de la racine de l'arbre à créer

    renvoie l'arbre des rangements physiques de la collection sous la forme de dictionnaires {"id_rangement" : int, "nom_rangement" : str, "contenu" : list (liste des noeuds enfants)} représentants chacun un noeud (la racine qui est la collection ayant None pour id)
    """
    if id_racine == 0 :
        id_racine = None
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    if id_racine == None :
        curseur.execute('''SELECT id_rangement FROM Rangements_physiques WHERE rangement_parent IS NULL;''')
    else :
        curseur.execute('''SELECT id_rangement FROM Rangements_physiques WHERE rangement_parent = ?;''', (id_racine,))
    # curseur.execute(f'''SELECT id_rangement FROM Rangements_physiques WHERE rangement_parent = {id_racine if id_racine != None else "NULL"};''')
    r = []
    for e in curseur :
        r.append(e[0])
    connexion.close()
    return {"id_rangement" : id_racine, "nom_rangement" : get_rangements_infos(id_racine)["nom_rangement"], "contenu" : [get_arbre_rangements(e) for e in r]}

def get_rangement_path(id_rangement:int) -> list :
    """
    id_rangement (int), id du rangement

    renvoie la liste des parents du rangement sous la forme d'une liste de dictionnaires {"id_rangement" : int, "nom_rangement" : str, "type_rangement" : str, "nb_compartiments" : int, "compartimentation" : str} si le rangement existe et None sinon
    """

    def __parcours(arbre:dict, element:int) -> list :
        """
        entrées :
            arbre (dict), l'arbre de rangements à parcourir
            element (int), l'id à trouver
        """
        path = []
        for e in arbre["contenu"] :
            path.append(e["id_rangement"])
            if e["id_rangement"] == element :
                return path
            else :
                search = __parcours(e, element)
                if search == None :
                    path.pop()
                else :
                    return path + search
        return None
    
    path = __parcours(get_arbre_rangements(), id_rangement)
    if path == None :
        path = []
    return [get_rangements_infos(e) for e in path]

def get_rangement_content(id_rangement:int) -> list :
    """
    id_rangement (int), id du rangement

    renvoie la liste des éléments contenu dans ce rangement sous la forme d'une liste de tuples (id de l'élément, type de l'élément ("pièce" ou "design"))
    """
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    # curseur.execute('''SELECT c.id_element FROM rangement_content as c JOIN Rangements_virtuels as v ON c.id_rangement = v.id_rangement WHERE v.rangement_physique = ?;''', (id_rangement,))
    curseur.execute('''SELECT id_element FROM rangement_content WHERE id_rangement = ?;''', (id_rangement,))
    r = []
    for e in curseur :
        r.append(e[0])
    connexion.close()
    return [(e, get_element_type(e)) for e in r]
    
def get_liste_id_rangements_for_qr_code_print() -> list :
    """
    renvoie la liste des id des rangements physique contenant directement des Lego (sans compartimentation)
    """
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    curseur.execute('''SELECT id_rangement FROM Rangements_physiques;''')
    # curseur.execute('''SELECT id_rangement FROM Rangements_physiques WHERE nb_compartiments = 1;''')
    r = []
    for e in curseur :
        r.append(e[0])
    connexion.close()
    # return r
    return [e for e in r if not rangement_est_compartimente(e)]

def get_rangement_parent(id_rangement:int) -> int :
    """
    id_rangement (int), l'id du rangement dont on veut connaitre le parent

    renvoie l'id du rangement parent (0 s'il s'agit de la Collection) (si l'id_rangement existe) et None sinon
    """
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    curseur.execute('''SELECT rangement_parent FROM Rangements_physiques WHERE id_rangement = ?;''', (id_rangement,))
    r = []
    for e in curseur :
        r.append(e[0])
    connexion.close()
    assert len(r) <= 1
    if len(r) == 0 :
        return None
    elif r[0] == None :
        return 0
    else :
        return r[0]
    
def get_rangement_for_element(element_id:int) -> int :
    """
    element_id (int), l'id de l'élément
    
    renvoie l'id du rangement qui contient cet élément s'il existe et None sinon
    """
    connexion = sqlite3.connect(MOC)
    curseur = connexion.cursor()
    curseur.execute('''SELECT id_rangement FROM rangement_content WHERE id_element = ?;''', (element_id,))
    r = []
    for e in curseur :
        r.append(e[0])
    connexion.close()
    if len(r) == 0 :
        return None
    else :
        return r[0]



if __name__ == "__main__" :
    pass
    # print(get_liste_categories_dict())
    # print(get_liste_sous_categories(11, direct=False))
    # print(get_infos_categorie(11))
    # print(get_arbre_rangements())
    # print(get_rangement_path(1))
    # print(get_liste_gammes_dict())
    print(get_liste_sous_gammes("sw"))