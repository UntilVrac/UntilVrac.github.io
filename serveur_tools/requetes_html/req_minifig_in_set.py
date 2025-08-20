from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
path.append(BRICKSTOCK_PATH)

import serveur_tools.scripts_gestion_bdd.gestion_bdd as bdd
from serveur_tools.pile import Pile



def get_minifig_in_set_request(params_get:dict, HISTORIQUE:Pile, script:str=None, post:bool=False) -> dict :
    """
    entrées :
        params_get (dict) : les paramètres get
        HISTORIQUE (Pile) : l'historique de navigation sur le site
        script (str) : le script (None par défaut)
        post (bool) : True si la requête était de type POST et FALSE sinon

    renvoie les paramètres de modifications pour le rendu de la page web
    """
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
    params = {"{page_precedente}" : page_precedente}
    if "id_set" not in params_get :
        params["{script}"] = f"""<script type="text/javascript">
alert("erreur : l'url ne contient pas l'id du set");
window.location.href = "http://localhost:1520/{page_precedente}";
</script>"""
        return params
    if script == None :
        params["{script}"] = ""
    else :
        params["{script}"] = f"""<script type="text/javascript">{script}</script>"""
    params["{page_precedente}"] = f"/{page_precedente}"
    set_data = bdd.get_set_data(params_get["id_set"])
    params["{nom_set}"], params["{id_set}"], params["{annee_set}"], params["{gamme_set}"], params["{image_ref_set}"] = set_data["nom_français"], set_data["id_set"], set_data["annee"], set_data["gamme"], set_data["image_ref"]
    list_minifig_in_set = ""
    value_input = {}
    i = 1
    if "liste_minifigs" in params_get and post :
        if params_get["liste_minifigs"] == "{}" :
            value_input = {}
        else :
            value_input = {e.split(" : ")[0] : int(e.split(" : ")[1]) for e in params_get["liste_minifigs"][1:-1].split(", ")}
        for k in value_input :
            classes = "item_minifig"
            if i % 5 == 0 :
                classes += " last"
            m = bdd.get_minifig_data(k)
            m["quantite"] = value_input[m["id_minifig"]]
            list_minifig_in_set += f"""<div class="{classes}" id="item_minifig{i}">
    <img id="bouton_supprimer{i}" class="supprimer_item" src="http://localhost:1520/BrickStock/images/croix.svg">
    <img class="apercu" src="{m["image_ref"]}">
    <span>ID&nbsp;: {m["id_minifig"]}</span><br/>
    <span>{m["nom"]}</span>
    <div class="quantity_box" style="margin-top: 12px;">
        <button type="button" class="bouton_moins" style="width: 50px;" id="-{i}">
            <svg class="minus" width="14px" height="2px" viewBox="0 0 14 2" aria-hidden="true"><polygon fill="black" points="14 2 0 2 0 -6.03961325e-14 14 -6.03961325e-14"></polygon></svg>
        </button><input required type="number" class="valeur" style="width: 56px;" min="0" id="val{i}" name="quantite" value="{m["quantite"]}"><button type="button" class="bouton_plus" style="width: 50px;" id="+{i}">
            <svg class="add" xmlns="http://www.w3.org/2000/svg" width="14px" height="14px" viewBox="0 0 14 14" aria-hidden="true"><polygon fill="#FFFFFF" points="14 8 0 8 0 6 14 6"></polygon><rect fill="#FFFFFF" fill-rule="nonzero" x="6" y="0" width="2" height="14"></rect></svg>
        </button>
    </div>
    <span class="hide" id="id_minifig_in_set{i}">{m["id_minifig"]}</span>
</div>"""
            i += 1
    else :
        liste_minifigs = bdd.get_minifig_in_set(params["{id_set}"])
        for m in liste_minifigs :
            classes = "item_minifig"
            if i % 5 == 0 :
                classes += " last"
            list_minifig_in_set += f"""<div class="{classes}" id="item_minifig{i}">
    <img id="bouton_supprimer{i}" class="supprimer_item" src="http://localhost:1520/BrickStock/images/croix.svg">
    <img class="apercu" src="{m["image_ref"]}">
    <span>ID&nbsp;: {m["id_minifig"]}</span><br/>
    <span>{m["nom"]}</span>
    <div class="quantity_box" style="margin-top: 12px;">
        <button type="button" class="bouton_moins" style="width: 50px;" id="-{i}">
            <svg class="minus" width="14px" height="2px" viewBox="0 0 14 2" aria-hidden="true"><polygon fill="black" points="14 2 0 2 0 -6.03961325e-14 14 -6.03961325e-14"></polygon></svg>
        </button><input required type="number" class="valeur" style="width: 56px;" min="0" id="val{i}" name="quantite" value="{m["quantite"]}"><button type="button" class="bouton_plus" style="width: 50px;" id="+{i}">
            <svg class="add" xmlns="http://www.w3.org/2000/svg" width="14px" height="14px" viewBox="0 0 14 14" aria-hidden="true"><polygon fill="#FFFFFF" points="14 8 0 8 0 6 14 6"></polygon><rect fill="#FFFFFF" fill-rule="nonzero" x="6" y="0" width="2" height="14"></rect></svg>
        </button>
    </div>
    <span class="hide" id="id_minifig_in_set{i}">{m["id_minifig"]}</span>
</div>"""
            value_input[m["id_minifig"]] = m["quantite"]
            i += 1
    params["{list_minifig_in_set}"] = list_minifig_in_set
    params["{value_input}"] = value_input
    if "nom_search" in params_get :
        params["{nom_search}"] = params_get["nom_search"]
    else :
        params["{nom_search}"] = ""
    if "id_minifig_search" in params_get :
        params["{id_minifig_search}"] = params_get["id_minifig_search"]
    else :
        params["{id_minifig_search}"] = ""
    if "gamme_search" in params_get :
        params["{gamme_search}"] = params_get["gamme_search"]
    else :
        params["{gamme_search}"] = ""
    if "id_set_search" in params_get :
        params["{id_set_search}"] = params_get["id_set_search"]
    else :
        params["{id_set_search}"] = ""
    params_search = {k[:-7] : params_get[k] for k in params_get if params_get[k] not in ("", "0") and k.endswith("_search")}
    if "id_set_search" in params_get :
        if params_get["id_set_search"] != "" :
            params_search["id_set"] = params_get["id_set_search"]
    search_result = bdd.search_minifig(params_search)
    cases = ""
    i = 1
    for r in search_result :
        # if r["id_minifig"] not in value_input :
        classes = "block_resultat"
        if i % 3 == 0 :
            classes += " last"
        cases += f"""<div class="{classes}" id="resultat{i}">
<img class="apercu" src="{r["image_ref"]}">
<h4>{r["nom"]}</h4>
<span> ID : {r["id_minifig"]}</span><br/>
<span>gamme : {r["nom_gamme"]}</span>
<span class="hide" id="id_minifig{i}">{r["id_minifig"]}</span>
<input type="submit" value="AJOUTER" class="bouton_validation_infos enregistrer" style="border-radius: 4px; width: 112px; margin-top: 8px;" id="ajouter{i}">
</div>"""
        i += 1
    if search_result == [] :
        cases = "<span>aucun résultat</span>"
    params["{cases}"] = cases
    params["{resultats}"] = search_result
    # params["{resultats}"] = [e for e in search_result if e["id_minifig"] not in value_input]
    liste_gammes = ""
    for g in bdd.get_liste_gammes() :
        liste_gammes += f"""<option value="{g[0]}">{g[1]}</option>"""
    params["{liste_gammes}"] = liste_gammes
    return params

def post_minifig_in_set_search_request(url:str, HISTORIQUE:Pile, params_post:dict) -> dict :
    """
    entrées :
        url (str), l'url courante
        HISTORIQUE (Pile) : l'historique de navigation sur le site
        params_post (dict), les paramètres de la requête POST
        get_file (fonction), la fonction get_file

    renvoie les paramètres de modifications pour le rendu de la page web
    """
    params_get = {e.split("=")[0] : e.split("=")[1] for e in url.split("?")[1].split("&")}
    params_get = {"id_set" : params_get["id_set"], "nom_search" : params_post["nom"], "id_minifig_search" : params_post["id_minifig"], "gamme_search" : params_post["gamme"], "id_set_search" : params_post["id_set"], "liste_minifigs" : params_post["liste_minifigs"]}
    params = get_minifig_in_set_request(params_get, HISTORIQUE, post=True)
    post_to_get = ""
    for p in params_post :
        post_to_get += f'{p}={params_post[p]}&'
    # params_minifig = get_file("minifigures?" + post_to_get[:-1])[1]
    # id_set = params["{id_set}"]
    return params

def post_minifig_in_set_save_request(url:str, params_post:dict) -> tuple :
    """
    entrées :
        url (str), l'url courante
        params_post (dict), les paramètres de la requête POST
        get_file (fonction), la fonction get_file

    renvoie le tuple (url de reponse, script) à utiliser pour la réponse à la requête POST après avoir fait les modifications de la base de données nécéssaires
    """
    if params_post["liste_minifigs"] in ("{}", "{  }") :
        liste_minifigs = {}
    else :
        liste_minifigs = {e.split(" : ")[0] : e.split(" : ")[1] for e in params_post["liste_minifigs"][1:-1].split(", ")}
    try :
        liste_minifigs = {k : int(liste_minifigs[k]) for k in liste_minifigs if int(liste_minifigs[k]) != 0}
        for k in liste_minifigs :
            assert bdd.minifig_in_database(k)
            assert liste_minifigs[k] > 0
    except :
        return (url, """alert("erreur : les minifigs sélectionnées ne sont pas répertoriées ou les quantités saisies ne sont pas valides (quantités négatives ou n'étant pas des nombres)");""")
    response = bdd.update_minifig_in_set(params_post["id_set"], liste_minifigs)
    if response :
        return (url, "alert('les informations ont bien été enregistré');")
    else :
        return (url, """alert("erreur : les informations n'ont pas été enregistré");""")