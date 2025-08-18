from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/workspaces/UntilVrac.github.io"
path.append(BRICKSTOCK_PATH)

import serveur_tools.scripts_gestion_bdd.gestion_bdd as bdd



def get_minifigs_request(params_get:dict, script:str=None) -> dict :
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
    if "gamme" in params_get :
        params["{gamme}"] = params_get["gamme"]
    else :
        params["{gamme}"] = ""
    if "id_set" in params_get :
        params["{id_set}"] = params_get["id_set"]
    else :
        params["{id_set}"] = ""
    search_result = bdd.search_minifig({k : params_get[k] for k in params_get if params_get[k] not in ("", "0")})
    cases = ""
    i = 1
    for r in search_result :
        cases += f"""<div class="block_resultat" id="resultat{i}">
    <img class="apercu" src="{r["image_ref"]}">
    <h4>{r["nom"]}</h4>
    <span> ID : {r["id_minifig"]}</span><br/>
    <span>gamme : {r["nom_gamme"]}</span>
</div>"""
        i += 1
    if search_result == [] :
        cases = "<span>aucun résultat</span>"
    params["{cases}"] = cases
    params["{resultats}"] = search_result
    liste_gammes = ""
    for g in bdd.get_liste_gammes() :
        liste_gammes += f"""<option value="{g[0]}">{g[1]}</option>"""
    params["{liste_gammes}"] = liste_gammes
    return params

def post_minifigs_request(url:str, params_post:dict) -> tuple :
    """
    entrées :
        url (str), l'url courante
        params_post (dict), les paramètres de la requête POST

    renvoie le tuple (url de reponse, script) à utiliser pour la réponse à la requête POST après avoir fait les modifications de la base de données nécéssaires
    """
    if params_post["form_name"] == "add_minifig" :
        minifig_data = {}
        for p in ("id_minifigure", "nom", "gamme") :
            assert p in params_post
            f = {"id_minifigure" : str, "nom" : str, "gamme" : str}[p]  #, "image_ref" : str
            minifig_data[p] = f(params_post[p])
        response = bdd.ajouter_minifig(minifig_data["id_minifigure"], minifig_data["nom"], minifig_data["gamme"])
        if response :
            return (url, """window.location.href = window.location.href.split('#')[0];
alert('les informations ont bien été enregistré');""")
        else :
            return (url, """alert("erreur : les informations n'ont pas été enregistré");""")
    elif params_post["form_name"] == "minifig_quantity" :
        id_minifig = params_post["id_minifig"]
        quantite = int(params_post["quantite"])
        try :
            assert quantite >= 0
            assert bdd.minifig_est_dans_moc(id_minifig)
        except :
            return (url, """alert("erreur : la quantité doit être supérieure ou égale à 0");""")
        response = bdd.update_moc_minifig_qt(id_minifig, quantite)
        if response :
            return (url, f"""window.location.href = window.location.href.split('#')[0] + '{"#" + params_post["linkId"]}';
alert('les informations ont bien été enregistré');""")
        else :
            return (url, """alert("erreur : les informations n'ont pas été enregistré");""")