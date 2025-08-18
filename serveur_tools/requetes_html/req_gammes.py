from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/workspaces/UntilVrac.github.io"
path.append(BRICKSTOCK_PATH)

import serveur_tools.scripts_gestion_bdd.gestion_bdd as bdd
from serveur_tools.pile import Pile
import serveur_tools.scrap_data as scrap



def get_gammes_request(params_get:dict, HISTORIQUE:Pile, script:str=None) -> dict :
    """
    entrées :
        params_get (dict) : les paramètres get
        HISTORIQUE (Pile) : historique de navigation sur le site
        script (str) : le script (None par défaut)

    renvoie les paramètres de modifications pour le rendu de la page web
    """
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
    content_ul = ""
    for g in bdd.get_liste_gammes() :
        content_ul += f"""<li>{g[0]} : <b>{g[1]}</b></li>"""
    params["{content_ul}"] = content_ul
    return params

def post_gammes_request(url:str, params_post:dict) -> tuple :
    """
    entrées :
        url (str), l'url courante
        params_post (dict), les paramètres de la requête POST

    renvoie le tuple (url de reponse, script) à utiliser pour la réponse à la requête POST après avoir fait les modifications de la base de données nécéssaires
    """
    assert params_post["form_name"] == "add_gamme"
    response = bdd.ajouter_gamme(params_post["id_gamme"], params_post["nom_gamme"])
    if response :
        return (url, "alert('les informations ont bien été enregistrées');")
    else :
        return (url, """alert("erreur : les informations n'ont pas été enregistrées");""")