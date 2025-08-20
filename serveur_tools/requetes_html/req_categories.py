from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
path.append(BRICKSTOCK_PATH)

import serveur_tools.scripts_gestion_bdd.gestion_bdd as bdd



def get_categories_request(params_get:dict, script:str) -> dict :
    """
    entrées :
        params_get (dict) : les paramètres get
        script (str) : le script (None par défaut)

    renvoie les paramètres de modifications pour le rendu de la page web
    """
    params = {}
    if script == None :
        params["{script}"] = ""
    else :
        params["{script}"] = f"""<script type="text/javascript">{script}</script>"""
    params["{dictCategories}"] = {c : bdd.get_infos_categorie(c) for c in bdd.get_liste_id_categories()}
    params["{categoriesRacines}"] = bdd.get_liste_categories_racines()
    return params

def post_categories_request(url:str, params_post:dict) -> tuple :
    """
    entrées :
        url (str), l'url courante
        params_post (dict), les paramètres de la requête POST

    renvoie le tuple (url de reponse, script) à utiliser pour la réponse à la requête POST après avoir fait les modifications de la base de données nécéssaires
    """
    # if params_post["form_name"] == "add_categorie" :
    assert params_post["form_name"] == "add_categorie"
    cat_data = {}
    for p in ("id_categorie", "nom_categorie", "image_ref", "categorie_sup") :
        print(p)
        assert p in params_post
        f = {"id_categorie" : int, "nom_categorie" : str, "image_ref" : str, "categorie_sup" : (lambda e : int(e) if e not in ("", "0", 0) else None)}[p]
        cat_data[p] = f(params_post[p])
    response = bdd.ajouter_categorie(cat_data["id_categorie"], cat_data["nom_categorie"], cat_data["image_ref"], cat_data["categorie_sup"])
    if response :
        return (url, "alert('les informations ont bien été enregistré');")
    else :
        return (url, """alert("erreur : les informations n'ont pas été enregistré");""")
    # elif params_post["form_name"] == "add_sous_categorie" :
    #     sc_data = {}
    #     for p in ("id_sous_categorie", "nom_sous_categorie", "id_categorie") :
    #         assert p in params_post
    #         f = {"id_sous_categorie" : int, "nom_sous_categorie" : str, "id_categorie" : int}[p]
    #         sc_data[p] = f(params_post[p])
    #     response = bdd.ajouter_sous_categorie(sc_data["id_sous_categorie"], sc_data["nom_sous_categorie"], sc_data["id_categorie"])
    #     if response :
    #         return get_file(url, script="alert('les informations ont bien été enregistré');")
    #     else :
    #         return get_file(url, script="""alert("erreur : les informations n'ont pas été enregistré");""")