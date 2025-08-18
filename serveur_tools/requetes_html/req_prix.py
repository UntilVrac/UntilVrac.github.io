from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/workspaces/UntilVrac.github.io"
path.append(BRICKSTOCK_PATH)

import serveur_tools.scripts_gestion_bdd.gestion_bdd as bdd
from serveur_tools.pile import Pile
import serveur_tools.scrap_data as scrap



def get_prix_piece_request(params_get:dict, HISTORIQUE:Pile, script:str=None) -> dict :
    """
    entrées :
        params_get (dict) : les paramètres get, 
        HISTORIQUE (Pile) : l'historique de navigation sur le site
        script (str) : le script (None par défaut)

    renvoie les paramètres de modifications pour le rendu de la page web
    """
    id_piece = int(params_get["id_piece"])
    params = {}
    if script == None :
        params["{script}"] = ""
    else :
        params["{script}"] = f"""<script type="text/javascript">{script}</script>"""
    if HISTORIQUE.est_vide() :
        page_precedente = "BrickStock/pieces"
    else :
        temp = Pile()
        page_precedente = HISTORIQUE.depiler()
        temp.empiler(page_precedente)
        while not page_precedente.split("?")[0] in ("BrickStock", "BrickStock/pieces") and not HISTORIQUE.est_vide() :
            page_precedente = HISTORIQUE.depiler()
            temp.empiler(page_precedente)
        if not page_precedente.split("?")[0] in ("BrickStock", "BrickStock/pieces") :
            page_precedente = "BrickStock/pieces"
        while not temp.est_vide() :
            HISTORIQUE.empiler(temp.depiler())
        assert temp.est_vide()
    params["{page_precedente}"] = page_precedente
    params["{id_piece}"] = id_piece
    piece_data = bdd.get_piece_info(id_piece)
    params["{nom}"], params["{id_design}"], params["{couleur}"], params["{categorie}"], params["{dimensions}"], params["{masse}"], params["{image_ref}"] = piece_data["nom"], piece_data["id_design"], piece_data["nom_couleur"], piece_data["categorie_span"], piece_data["dimensions_stud"], piece_data["masse"], piece_data["image_ref"]
    params["{prix_site_lego}"] = str(piece_data["prix_site_lego"]) + " €"
    params["{prix_legostore}"] = str(piece_data["prix_mur_pick_a_brick"]) + " €"
    prix_bricklink = scrap.get_prix_piece(id_piece)
    params["{prix_bricklink}"] = f"prix le plus bas&nbsp;: {prix_bricklink[0]} €<br/>prix moyen&nbsp;: {prix_bricklink[1]} €<br/>prix le plus haut&nbsp;: {prix_bricklink[2]} €"
    list_prix = [piece_data["prix_site_lego"], piece_data["prix_mur_pick_a_brick"], prix_bricklink[1]]
    list_prix.sort()
    if piece_data["prix_site_lego"] == list_prix[0] :
        params["{picto_site_lego}"] = "picto_prix_vert"
    elif piece_data["prix_site_lego"] == list_prix[-1] :
        params["{picto_site_lego}"] = "picto_prix_rouge"
    else :
        params["{picto_site_lego}"] = "picto_prix_orange"
    if piece_data["prix_mur_pick_a_brick"] == list_prix[0] :
        params["{picto_legostore}"] = "picto_prix_vert"
    elif piece_data["prix_mur_pick_a_brick"] == list_prix[-1] :
        params["{picto_legostore}"] = "picto_prix_rouge"
    else :
        params["{picto_legostore}"] = "picto_prix_orange"
    if prix_bricklink[1] == list_prix[0] :
        params["{picto_bricklink}"] = "picto_prix_vert"
    elif prix_bricklink[1] == list_prix[-1] :
        params["{picto_bricklink}"] = "picto_prix_rouge"
    else :
        params["{picto_bricklink}"] = "picto_prix_orange"
    return params

def get_prix_set_request(params_get:dict, HISTORIQUE:Pile, script:str=None) -> dict :
    """
    entrées :
        params_get (dict) : les paramètres get, 
        HISTORIQUE (Pile) : l'historique de navigation sur le site
        script (str) : le script (None par défaut)

    renvoie les paramètres de modifications pour le rendu de la page web
    """
    id_set = int(params_get["id_set"])
    params = {}
    if script == None :
        params["{script}"] = ""
    else :
        params["{script}"] = f"""<script type="text/javascript">{script}</script>"""
    if HISTORIQUE.est_vide() :
        page_precedente = "BrickStock/sets"
    else :
        temp = Pile()
        page_precedente = HISTORIQUE.depiler()
        temp.empiler(page_precedente)
        while not page_precedente.split("?")[0].endswith("sets") and not HISTORIQUE.est_vide() :
            page_precedente = HISTORIQUE.depiler()
            temp.empiler(page_precedente)
        if not page_precedente.split("?")[0].endswith("sets") :
            page_precedente = "BrickStock/sets"
        while not temp.est_vide() :
            HISTORIQUE.empiler(temp.depiler())
        assert temp.est_vide()
    params["{page_precedente}"] = page_precedente
    params["{id_set}"] = id_set
    set_data = bdd.get_set_data(id_set)
    params["{nom}"], params["{annee}"], params["{gamme}"], params["{image_ref}"] = set_data["nom_français"], set_data["annee"], set_data["gamme"], set_data["image_ref"]
    prix_lego = scrap.scrap_prix_site_lego(id_set)
    if prix_lego == None :
        prix_lego_str = "-"
    else :
        prix_lego_str = str(prix_lego) + " €"
    params["{prix_lego}"] = f"""<a href="https://www.lego.com/fr-fr/product/{id_set}" target="_blank">{prix_lego_str}</a>"""
    if set_data["lien_amazon"] == None :
        prix_amazon = None
        params["{prix_amazon}"] = "-"
    else :
        prix_amazon = scrap.get_prix_amazon(set_data["lien_amazon"])
        params["{prix_amazon}"] = f"""<a href="{set_data["lien_amazon"]}" target="_blank">{str(prix_amazon) + " €"}</a>"""
    prix_bricklink = scrap.get_prix_set(id_set)
    params["{prix_bricklink}"] = f"prix le plus bas&nbsp;: {prix_bricklink[0]} €<br/>prix moyen&nbsp;: {prix_bricklink[1]} €<br/>prix le plus haut&nbsp;: {prix_bricklink[2]} €"
    if prix_lego == None :
        params["{picto_lego}"] = "picto_prix_rouge"
        if prix_amazon == None :
            params["{picto_amazon}"] = "picto_prix_rouge"
            params["{picto_bricklink}"] = "picto_prix_vert"
        else :
            params["{picto_amazon}"] = "picto_prix_vert"
            params["{picto_bricklink}"] = "picto_prix_orange"
    else :
        params["{picto_bricklink}"] = "picto_prix_orange"
        if prix_amazon == None :
            params["{picto_lego}"] = "picto_prix_vert"
            params["{picto_amazon}"] = "picto_prix_rouge"
        else :
            if prix_amazon < prix_lego :
                params["{picto_lego}"] = "picto_prix_orange"
                params["{picto_amazon}"] = "picto_prix_vert"
            elif prix_amazon > set_data["prix_lego"] :
                params["{picto_lego}"] = "picto_prix_vert"
                params["{picto_amazon}"] = "picto_prix_orange"
            else :
                params["{picto_lego}"] = "picto_prix_vert"
                params["{picto_amazon}"] = "picto_prix_vert"
    return params

def get_prix_minifig_request(params_get:dict, HISTORIQUE:Pile, script:str=None) -> dict :
    """
    entrées :
        params_get (dict) : les paramètres get, 
        HISTORIQUE (Pile) : l'historique de navigation sur le site
        script (str) : le script (None par défaut)

    renvoie les paramètres de modifications pour le rendu de la page web
    """
    id_minifig = params_get["id_minifig"]
    params = {}
    if script == None :
        params["{script}"] = ""
    else :
        params["{script}"] = f"""<script type="text/javascript">{script}</script>"""
    if HISTORIQUE.est_vide() :
        page_precedente = "BrickStock/minifigures"
    else :
        temp = Pile()
        page_precedente = HISTORIQUE.depiler()
        temp.empiler(page_precedente)
        while not page_precedente.split("?")[0].endswith("minifigures") and not HISTORIQUE.est_vide() :
            page_precedente = HISTORIQUE.depiler()
            temp.empiler(page_precedente)
        if not page_precedente.split("?")[0].endswith("minifigures") :
            page_precedente = "BrickStock/minifigures"
        while not temp.est_vide() :
            HISTORIQUE.empiler(temp.depiler())
        assert temp.est_vide()
    params["{page_precedente}"] = page_precedente
    params["{id_minifig}"] = id_minifig
    minifig_data = bdd.get_minifig_data(id_minifig)
    params["{nom}"], params["{id_minifig}"], params["{gamme}"], params["{image_ref}"] = minifig_data["nom"], id_minifig, minifig_data["nom_gamme"], minifig_data["image_ref"]
    prix_bricklink = scrap.get_prix_minifig(id_minifig)
    if prix_bricklink[0] == prix_bricklink[1] == prix_bricklink[2] == None :
        params["{prix_bricklink}"] = "-"
    else :
        params["{prix_bricklink}"] = f"prix le plus bas&nbsp;: {str(prix_bricklink[0]) + " €" if prix_bricklink[0] != None else "-"}<br/>prix moyen&nbsp;: {str(prix_bricklink[1]) + " €" if prix_bricklink[1] != None else "-"}<br/>prix le plus haut&nbsp;: {str(prix_bricklink[2]) + " €" if prix_bricklink[2 ] != None else "-"}"
    return params