from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/"
path.append(BRICKSTOCK_PATH)

import serveur_tools.scripts_gestion_bdd.gestion_bdd as bdd
from serveur_tools.pile import Pile



def get_exemplaires_request(params_get:dict, HISTORIQUE:Pile, script:str=None) -> dict :
    """
    entrées :
        params_get (dict) : les paramètres get
        HISTORIQUE (Pile) : l'historique de navigation sur le site
        script (str) : le script (None par défaut)

    renvoie les paramètres de modifications pour le rendu de la page web
    """
    params = {}
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
    if script == None :
        params["{script}"] = ""
    else :
        params["{script}"] = f"""<script type="text/javascript">{script}</script>"""
    id_set = params_get["id_set"]
    set_data = bdd.get_set_data(id_set)
    params["{nom_set}"], params["{id_set}"], params["{annee_set}"], params["{gamme_set}"], params["{image_ref_set}"] = set_data["nom_français"], set_data["id_set"], set_data["annee"], set_data["gamme"], set_data["image_ref"]
    list_exemplaires = ""
    input_val = {}
    for e in bdd.get_set_data_from_moc(id_set) :
        statut = ""
        assert e["statut"] in ("construit", "détruit")
        if e["statut"] == "détruit" :
            statut = f"""<select class="statut" id="{e["id_exemplaire"]}">
                <option value="construit">construit</option>
                <option selected value="détruit">détruit</option>
            </select>"""
        else :
            statut = f"""<select class="statut" id="{e["id_exemplaire"]}">
                <option selected value="construit">construit</option>
                <option value="détruit">détruit</option>
            </select>"""
        list_exemplaires += f"""
<tr>
<td>{e["id_exemplaire"]}</td>
<td>{e["id_set"]}</td>
<td>{set_data["nom_français"]}</td>
<td>{e["date_achat"]}</td>
<td>
    {statut}
</td>
</tr>"""
        input_val[e["id_exemplaire"]] = e["statut"]
    params["{list_exemplaires}"] = list_exemplaires
    params["{input_value}"] = str(input_val)
    return params

def post_exemplaires_request(url:str, params_post:dict) -> tuple :
    """
    entrées :
        url (str), l'url courante
        params_post (dict), les paramètres de la requête POST

    renvoie le tuple (url de reponse, script) à utiliser pour la réponse à la requête POST après avoir fait les modifications de la base de données nécéssaires
    """
    if params_post["form_name"] == "ajouter_exemplaire" :
        exemplaires_data = {}
        for p in ("id_set", "date_achat", "statut") :
            assert p in params_post
            f = {"id_set" : int, "date_achat" : str, "statut" : str}[p]
            exemplaires_data[p] = f(params_post[p])
        response = bdd.ajouter_exemplaire(exemplaires_data["id_set"], exemplaires_data["date_achat"], exemplaires_data["statut"])
    elif params_post["form_name"] == "save_data" :
        input_val = params_post["list_exemplaires"]
        list_exemplaires = {int(e.split(" : ")[0]) : e.split(" : ")[1] for e in input_val[1:-1].split(", ")}
        response = bdd.update_statut_exemplaires(list_exemplaires)
    if response :
        return (url, """alert("les informations ont bien été enregistré");""")
    else :
        return (url, """alert("erreur : les informations n'ont pas été enregistré");""")