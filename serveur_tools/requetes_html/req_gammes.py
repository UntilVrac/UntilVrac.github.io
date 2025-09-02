from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
path.append(BRICKSTOCK_PATH)

import serveur_tools.scripts_gestion_bdd.gestion_bdd as bdd
from serveur_tools.pile import Pile
import serveur_tools.scrap_data as scrap



def get_gammes_request(origine:str, HISTORIQUE:Pile, script:str=None) -> dict :
    """
    entrées :
        origine (str), la page d'origine ("sets" ou "minifigures")
        HISTORIQUE (Pile), l'historique de navigation sur le site
        script (str), le script (None par défaut)

    renvoie les paramètres de modifications pour le rendu de la page web
    """
    assert origine in ("sets", "minifigures")
    origine = f"BrickStock/{origine}"
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
        while not page_precedente.split("?")[0] != origine and not HISTORIQUE.est_vide() :
            page_precedente = HISTORIQUE.depiler()
            temp.empiler(page_precedente)
        if not page_precedente.split("?")[0] == origine :
            page_precedente = "BrickStock/sets"
        while not temp.est_vide() :
            HISTORIQUE.empiler(temp.depiler())
        assert temp.est_vide()
    params["{page_precedente}"] = page_precedente
    classes_values = {"sets" : (' class="main"', ""), "minifigures" : ("", ' class="main"')}
    params["{classSets}"], params["{classMinifigs}"] = classes_values[page_precedente.split("?")[0].split("/")[-1]]

    def __render_ul(liste_gammes:dict, n:int=0) -> str :
        """
        entrées :
            gamme (dict), le dictionnaire correspondant à la gamme
            n (le niveau de la liste)
        """
        content_li = ""
        for g in liste_gammes :
            content_li += f"""<li>{g["id_gamme"]}&nbsp;: <b>{g["nom_gamme"]}</b>
    <ul>
        {__render_ul(g["sous_gammes"])}
    </ul>
</li>"""
        return content_li

    # content_ul = ""
    # for g in bdd.get_liste_gammes() :
    #     content_ul += f"""<li>{g[0]} : <b>{g[1]}</b></li>"""
    params["{content_ul}"] = __render_ul(bdd.get_liste_gammes_dict())
    liste_gammes_options = ""
    for e in bdd.get_liste_gammes_list() :
        liste_gammes_options += f"""<option value="{e[0]}">{e[1]}</option>"""
    params["{liste_gammes_options}"] = liste_gammes_options
    return params

def post_gammes_request(url:str, params_post:dict) -> tuple :
    """
    entrées :
        url (str), l'url courante
        params_post (dict), les paramètres de la requête POST

    renvoie le tuple (url de reponse, script) à utiliser pour la réponse à la requête POST après avoir fait les modifications de la base de données nécéssaires
    """
    assert params_post["form_name"] == "add_gamme"
    response = bdd.ajouter_gamme(params_post["id_gamme"], params_post["nom_gamme"], params_post["id_gamme_parente"] if params_post["id_gamme_parente"] != "" else None)
    if response :
        return (url, "alert('les informations ont bien été enregistrées');")
    else :
        return (url, """alert("erreur : les informations n'ont pas été enregistrées");""")