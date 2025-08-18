from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/workspaces/UntilVrac.github.io"
path.append(BRICKSTOCK_PATH)

from serveur_tools.scripts_gestion_bdd.admin_bdd import *
from serveur_tools.scripts_gestion_bdd.bdd_verif import *
from serveur_tools.scripts_gestion_bdd.bdd_get import *
from serveur_tools.scripts_gestion_bdd.bdd_count import *
from serveur_tools.scripts_gestion_bdd.bdd_insert import *



def search_piece(params:dict) -> list :
    """
    params (dict), paramètres fournis

    renvoie la liste des résultats de la recherche sous la forme d'une liste de dictionnaires {id_piece : int, id_lego : int, id_design : int, nom : str, id_categorie : int, nom_categorie : str, dimensions : str, masse : float, id_couleur : int, couleur : str, image_ref : str, prix_site_lego : float, prix_mur_pick_a_brick : float, prix_legoland : float, prix_bricklink : tuple (prix min, prix moy, prix max)}
    """
    list_params = ("nom", "id_design", "ton", "couleur", "opaque", "transparent", "dimensions", "categorie")
    requete_init = """
SELECT p.id_piece FROM Piece as p JOIN Design as d JOIN Couleurs as col JOIN Categories as cat JOIN Tons as t
ON p.id_design = d.id_design AND p.id_couleur = col.id_couleur AND d.categorie = cat.id_categorie AND t.id_ton = col.ton
"""
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()

    def __search_piece() -> None :
        """
        execute la requête sql après prise en compte des paramètres fournis
        """
        if "sous_categorie" in params :
            if params["sous_categorie"] not in (None, "Null", "null", "", " ") :
                params["categorie"] = params["sous_categorie"]
            params.pop("sous_categorie")
        requete_sql = requete_init
        i = 0
        tables = {"id_design" : "p.id_design", "ton" : "t.id_ton", "couleur" : "p.id_couleur", "dimensions" : "d.dimensions", "categorie" : "cat.id_categorie"}
        for p in params :
            print(p)
            assert p in list_params
            if p not in ("opaque", "transparent") :
                if i == 0 :
                    requete_sql += "WHERE "
                else :
                    requete_sql += " AND "
                if p == "nom" :
                    nom = params[p].split(" ")
                    requete_sql += f'(d.nom LIKE "%{nom[0]}%" OR d.nom_Lego LIKE "%{nom[0]}%" OR d.nom_Bricklink LIKE "%{nom[0]}%")'
                    if len(nom) > 1 :
                        for mot in nom[1:] :
                            requete_sql += f' AND (d.nom LIKE "%{mot}%" OR d.nom_Lego LIKE "%{mot}%" OR d.nom_Bricklink LIKE "%{mot}%")'
                elif type(params[p]) == str :
                    requete_sql += f'{tables[p]} = "{params[p]}"'
                else :
                    requete_sql += f"{tables[p]} = {params[p]}"
                i += 1
        if "opaque" in params or "transparent" in params :
            if not("opaque" in params and "transparent" in params) :
                if i == 0 :
                    requete_sql += " WHERE "
                else :
                    requete_sql += " AND "
                if "opaque" in params :
                    requete_sql += 'col.est_transparent = "False"'
                else :
                    requete_sql += 'col.est_transparent = "True"'
        requete_sql += ";"
        curseur.execute(requete_sql)

    def __get_results(curseur:sqlite3.Cursor) -> list :
        """
        curseur (sqlitE.Cursor), le Cursor ayant exécuté la requête sql

        renvoie la liste des résultats sous la forme d'une liste de dictionnaires {id_piece : int, id_lego : int, id_design : int, nom : str, id_categorie : int, nom_categorie : str, dimensions : str, masse : float, id_couleur : int, couleur : str, image_ref : str, prix_site_lego : float, prix_mur_pick_a_brick : float, prix_legoland : float, prix_bricklink : tuple (prix min, prix moy, prix max)}
        """
        r = []
        for e in curseur :
            r.append(get_piece_info(e[0]))
        return r

    if MODE_SANS_ECHEC :
        try :
            __search_piece()
        except :
            curseur.execute(requete_init + ";")
    else :
        __search_piece()
    r = __get_results(curseur)
    connexion.close()
    return [{k : (e[k] if e[k] != None else "∅") for k in e} for e in r]

def search_design(params:dict) -> list :
    """
    params (dict), paramètres fournis

    renvoie une liste de dictionnaires {id_design : int, id_lego : str, id_bricklink : str, id_rebrickable : str, nom : str, nom_lego : str, nom_bricklink : str, nom_rebrickable : str, dimensions_stud : str, dimensions_cm : str, id_categorie : int, nom_categorie : str, masse : float, quantite_mur_pick_a_brick : int, image_ref : str}
    """
    list_params = ("nom", "dimensions", "categorie")
    requete_init = """SELECT d.id_design FROM Design as d JOIN Categories as cat ON d.categorie = cat.id_categorie"""
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()

    def __search_design() -> None :
        """
        execute la requête sql après prise en compte des paramètres fournis
        """
        if "sous_categorie" in params :
            if params["sous_categorie"] not in (None, "Null", "null", "", " ") :
                params["categorie"] = params["sous_categorie"]
            params.pop("sous_categorie")
        requete_sql = requete_init
        i = 0
        for p in params :
            assert p in list_params
            if i == 0 :
                requete_sql += " WHERE "
            else :
                requete_sql += " AND "
            tables = {"dimensions" : "d.dimensions", "categorie" : "cat.id_categorie"}
            if p == "nom" :
                nom = params[p].split(" ")
                requete_sql += f'(d.nom LIKE "%{nom[0]}%" OR d.nom_Lego LIKE "%{nom[0]}%" OR d.nom_Bricklink LIKE "%{nom[0]}%")'
                if len(nom) > 1 :
                    for mot in nom[1:] :
                        requete_sql += f' AND (d.nom LIKE "%{mot}%" OR d.nom_Lego LIKE "%{mot}%" OR d.nom_Bricklink LIKE "%{mot}%")'
            elif type(params[p]) == str :
                requete_sql += f'{tables[p]} = "{params[p]}"'
            else :
                requete_sql += f"{tables[p]} = {params[p]}"
            i += 1
        requete_sql += ";"
        curseur.execute(requete_sql)

    def __get_results(curseur:sqlite3.Cursor) -> list :
        """
        curseur (sqlitE.Cursor), le Cursor ayant exécuté la requête sql

        renvoie la liste des résultats sous la forme d'une liste de dictionnaires {id_design : int, id_lego : str, id_bricklink : str, id_rebrickable : str, nom : str, nom_lego : str, nom_bricklink : str, nom_rebrickable : str, dimensions_stud : str, dimensions_cm : str, id_categorie : int, nom_categorie : str, masse : float, quantite_mur_pick_a_brick : int, image_ref : str}
        """
        r = []
        for e in curseur :
            r.append(get_design_info(e[0]))
        return r
    
    if MODE_SANS_ECHEC :
        try :
            __search_design()
        except :
            curseur.execute(requete_init + ";")
    else :
        __search_design()
    r = __get_results(curseur)
    connexion.close()
    return r

def search_set(params:dict) -> list :
    """
    params (dict), paramètres fournis

    renvoie la liste des résultats sous la forme d'une liste de dictionnaires {id_set : int, nom_anglais : str, nom_français : str, id_gamme : str, nom_gamme : str, image_ref : str, annee : int, nb_pieces : int, tranche_age : str, lien_amazon : str}
    """
    list_params = ("id_set", "nom", "gamme", "annee")
    requete_init = """SELECT id_set FROM Sets"""
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()

    def __search_set() -> None :
        """
        execute la requête sql après prise en compte des paramètres fournis
        """
        requete_sql = requete_init
        i = 0
        for p in params :
            assert p in list_params
            if i == 0 :
                requete_sql += " WHERE "
            else :
                requete_sql += " AND "
            if p == "id_set" :
                requete_sql += f'id_set = {params[p]}'
            elif p == "nom" :
                nom = params[p].split(" ")
                requete_sql += f'(nom_anglais LIKE "%{nom[0]}%" OR nom_français LIKE "%{nom[0]}%")'
                if len(nom) > 1 :
                    for mot in nom[1:] :
                        requete_sql += f'AND (nom_anglais LIKE "%{mot}%" OR nom_français LIKE "%{mot}%")'
            elif p == "gamme" :
                requete_sql += f'gamme = "{params[p]}"'
            else :
                requete_sql += f'annee = {params[p]}'
        requete_sql += " ORDER BY annee DESC;"
        curseur.execute(requete_sql)
    
    def __get_results(curseur:sqlite3.Cursor) -> list :
        """
        curseur (sqlite.Cursor), le Cursor ayant exécuté la requête sql

        renvoie la liste des résultats sous la forme d'une liste de dictionnaires {id_set : int, nom_anglais : str, nom_français : str, id_gamme : str, nom_gamme : str, image_ref : str, annee : int, nb_pieces : int, tranche_age : str, lien_amazon : str}
        """
        r = []
        for e in curseur :
            r.append(get_set_data(e[0]))
        return r

    if MODE_SANS_ECHEC :
        try :
            __search_set()
        except :
            curseur.execute(requete_init + ";")
    else :
        __search_set()
    r = __get_results(curseur)
    connexion.close()
    return r

def search_minifig(params:dict) -> list :
    """
    params (dict), paramètres fournis

    renvoie la liste des résultats sous la forme d'une liste de dictionnaires {id_minifig : str, id_rebrickable : str, nom : str, id_gamme : str, nom_gamme : str, image_ref : str}
    """
    list_params = ("nom", "id_minifig", "gamme", "id_set")
    requete_init = """SELECT m.id_minifig FROM Minifigures as m"""
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()

    def __search_minifig() -> None :
        """
        execute la requête sql après prise en compte des paramètres fournis
        """
        requete_sql = requete_init
        i = 0
        if "id_set" in params :
            requete_sql += " JOIN minifig_dans_set as ms ON m.id_minifig = ms.id_minifig"
        for p in params :
            assert p in list_params
            if i == 0 :
                requete_sql += " WHERE "
            else :
                requete_sql += " AND "
            if p == "nom" :
                nom = params[p].split(" ")
                requete_sql += f'm.nom LIKE "%{nom[0]}%"'
                if len(nom) > 1 :
                    for mot in nom[1:] :
                        requete_sql += f' AND m.nom LIKE "%{mot}%"'
            elif p == "id_minifig" :
                requete_sql += f'm.id_minifig = "{params[p]}"'
            elif p == "gamme" :
                requete_sql += f'm.gamme = "{params[p]}"'
            elif p == "id_set" :
                requete_sql += f'ms.id_set = {int(params[p])}'
            i += 1
        requete_sql += ";"
        curseur.execute(requete_sql)

    def __get_results(curseur:sqlite3.Cursor) -> list :
        """
        curseur (sqlite.Cursor), le Cursor ayant exécuté la requête sql

        renvoie la liste des résultats sous la forme d'une liste de dictionnaires {id_minifig : str, id_rebrickable : str, nom : str, id_gamme : str, nom_gamme : str, image_ref : str}
        """
        r = []
        for e in curseur :
            r.append(get_minifig_data(e[0]))
        return r

    if MODE_SANS_ECHEC :
        try :
            __search_minifig()
        except :
            curseur.execute(requete_init + ";")
    else :
        __search_minifig()
    r = __get_results(curseur)
    connexion.close()
    r = [{k : (e[k] if e[k] != None else "∅") for k in e} for e in r]
    r.reverse()
    return r



if __name__ == "__main__" :
    print(search_piece({}))