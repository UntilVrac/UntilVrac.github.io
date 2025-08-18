from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/workspaces/UntilVrac.github.io"
path.append(BRICKSTOCK_PATH)

import serveur_tools.scripts_gestion_bdd.gestion_bdd as bdd



def get_designs_request(params_get:dict, script:str=None) -> dict :
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
    if "nom" in params_get :
        params["{nom}"] = params_get["nom"]
    else :
        params["{nom}"] = ""
    if "dimensions" in params_get :
        params["{dimensions}"] = params_get["dimensions"]
    else :
        params["{dimensions}"] = ""
    if "categorie" in params_get :
        params["{categorie}"] = params_get["categorie"]
    else :
        params["{categorie}"] = "0"
    if "sous_categorie" in params_get :
        params["{sous_categorie}"] = params_get["sous_categorie"]
    else :
        params["{sous_categorie}"] = "0"
    search_result = bdd.search_design({k : params_get[k] for k in params_get if params_get[k] not in ("", "0")})
    cases = ""
    i = 1
    for r in search_result :
        cases += f"""<div class="block_resultat" id="resultat{i}">
<img class="apercu" src="{r["image_ref"]}">
<h4>{r["nom"]}</h4>
<span>ID : {r["id_design"]}</span><br/>
<span>catégorie : {r["nom_categorie"]}</span>
</div>"""
        i += 1
    if search_result == [] :
        cases = "<span>aucun résultat</span>"
    params["{cases}"] = cases
    params["{resultats}"] = search_result
    if "sous_categorie" in params_get :
        params["{categorie_filter}"] = params_get["sous_categorie"]
    else :
        params["{categorie_filter}"] = "0"
    liste_categories = ""
    liste_categories_bis = ""
    liste_categorie_dict = [bdd.get_infos_categorie(id) for id in bdd.get_liste_categories_racines()]
    for c in liste_categorie_dict :
        if "categorie" in params_get :
            if params_get["categorie"] == str(c["id_categorie"]) :
                liste_categories += f"""<option selected value="{c['id_categorie']}">{c['nom_categorie']}</option>"""
            else :
                liste_categories += f"""<option value="{c['id_categorie']}">{c['nom_categorie']}</option>"""
        else :
            liste_categories += f"""<option value="{c['id_categorie']}">{c['nom_categorie']}</option>"""
        liste_categories_bis += f"""<option value="{c['id_categorie']}">{c['nom_categorie']}</option>"""
    params["{liste_categories}"] = liste_categories
    params["{liste_categories_bis}"] = liste_categories_bis
    params["{liste_sous_categories}"] = {c["id_categorie"] : [[sc, bdd.get_infos_categorie(sc)["nom_categorie"]] for sc in bdd.get_liste_sous_categories(c["id_categorie"], direct=False)] for c in liste_categorie_dict}
    liste = [params["{liste_sous_categories}"][k] for k in params["{liste_sous_categories}"]]
    params["{liste_all_categories}"] = []
    for e in liste :
        params["{liste_all_categories}"] += e
    return params

def post_designs_request(url:str, params_post:dict) -> tuple :
    """
    entrées :
        url (str), l'url courante
        params_post (dict), les paramètres de la requête POST

    renvoie le tuple (url de reponse, script) à utiliser pour la réponse à la requête POST après avoir fait les modifications de la base de données nécéssaires
    """
    assert params_post["form_name"] == "add_design"
    design_data = {}
    for p in ("id_design", "id_lego", "id_bricklink", "nom", "nom_lego", "nom_bricklink", "categorie", "sous_categorie", "dimensions", "transparent") :
        assert p in params_post
        f = {"id_design" : int, "id_lego" : int, "id_bricklink" : str, "nom" : str, "nom_lego" : str, "nom_bricklink" : str, "categorie" : int, "sous_categorie" : int, "dimensions" : str, "transparent" : (lambda e : True if e.lower() == "true" else False)}[p]
        design_data[p] = f(params_post[p])
    cat = design_data["categorie"]
    if design_data["sous_categorie"] not in (None, "Null", "null", "None", "", " ", "0", 0) :
        cat = design_data["sous_categorie"]
    response = bdd.ajouter_design(design_data["id_design"], design_data["id_lego"], design_data["id_bricklink"], design_data["nom"], design_data["nom_lego"], design_data["nom_bricklink"], design_data["dimensions"], cat, design_data["transparent"])
    if response :
        return (url, "alert('les informations ont bien été enregistrées');")
    else :
        return (url, """alert("erreur : les informations n'ont pas été enregistrées");""")



if __name__ == "__main__" :
    print(get_designs_request({}))