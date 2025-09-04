from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
path.append(BRICKSTOCK_PATH)

from datetime import datetime
from os import remove
import serveur_tools.scripts_gestion_bdd.gestion_bdd as bdd
import serveur_tools.json_tools as json



INDEX_SAVE = 1



def get_sets_request(params_get:dict, script:str=None) -> dict :
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
    list_params = {"id_set" : "", "nom" : "", "gamme" : 0, "annee" : 0}
    for p in list_params :
        if p in params_get :
            params["{" + p + "}"] = params_get[p]
        else :
            params["{" + p + "}"] = list_params[p]
    search_result = bdd.search_set({k : params_get[k] for k in params_get if params_get[k] not in ("", "0")})
    cases = ""
    i = 1
    for r in search_result :
        r["nb_minifig"], r["nb_exemplaires"] = bdd.count_minifigs_in_set(r["id_set"]), bdd.count_exemplaires_in_moc(r["id_set"])
        class_list = "block_resultat"
        if i % 3 == 0 :
            class_list += " last"
        cases += f"""<div class="{class_list}" id="resultat{i}">
<img class="apercu" src="{r["image_ref"]}">
<h4>{r["nom_français"]}</h4>
<span>ID : {r["id_set"]}</span><br/>
<span>{r["gamme"]}</span><br/>
<span>année : {r["annee"]}</span>
</div>"""
        i += 1
    if search_result == [] :
        cases = "<span>aucun résultat</span>"
    params["{cases}"] = cases
    params["{resultats}"] = search_result
    liste_gammes = ""
    liste_gammes_bis = ""
    for g in bdd.get_liste_gammes_list() :
        if "gamme" in params_get :
            if params_get["gamme"] == g[0] :
                liste_gammes += f"""<option selected value="{g[0]}">{g[1]}</option>"""
            else :
                liste_gammes += f"""<option value="{g[0]}">{g[1]}</option>"""
        else :
            liste_gammes += f"""<option value="{g[0]}">{g[1]}</option>"""
        liste_gammes_bis += f"""<option value="{g[0]}">{g[1]}</option>"""
    params["{liste_gammes}"] = liste_gammes
    params["{liste_gammes_bis}"] = liste_gammes_bis
    liste_annees = ""
    for a in bdd.get_liste_annees_for_set() :
        if "annee" in params_get :
            if params_get["annee"] == a :
                liste_annees += f"""<option selected value="{a}">{a}</option>"""
            else :
                liste_annees += f"""<option value="{a}">{a}</option>"""
        else :
            liste_annees += f"""<option value="{a}">{a}</option>"""
    params["{liste_annees}"] = liste_annees
    params["{current_annee}"] = datetime.now().year
    return params

def post_sets_request(url:str, params_post:dict) -> tuple :
    """
    entrées :
        url (str), l'url courante
        params_post (dict), les paramètres de la requête POST

    renvoie le tuple (url de reponse, script) à utiliser pour la réponse à la requête POST après avoir fait les modifications de la base de données nécéssaires
    """
    filename = "data_save/sets_queue.json"
    if params_post["form_name"] in ("add_set", "add_to_queue") :
        set_data = {}
        for p in ("id_set", "nom_anglais", "nom_français", "gamme", "annee", "nb_pieces", "tranche_age", "lien_amazon") :
            assert p in params_post
            f = {"id_set" : int, "nom_anglais" : str, "nom_français" : str, "gamme" : str, "annee" : int, "nb_pieces" : int, "tranche_age" : str, "lien_amazon" : str}[p]
            set_data[p] = f(params_post[p])
        if params_post["form_name"] == "add_set" :
            response = bdd.ajouter_set(set_data["id_set"], set_data["nom_anglais"], set_data["nom_français"], set_data["gamme"], set_data["annee"], set_data["nb_pieces"], set_data["tranche_age"], set_data["lien_amazon"])
            if response :
                return (url, """alert("les informations ont bien été enregistré");""")
            else :
                return (url, """alert("erreur : les informations n'ont pas été enregistré");""")
        else :
            queue = json.upload_json(filename)
            queue.append(set_data)
            json.save_json(queue, filename)
    else :
        maintenant = datetime.now()
        global INDEX_SAVE
        filename2 = f"data_save/sets_queue_save-{INDEX_SAVE}-{maintenant.day}/{maintenant.month}/{maintenant.year} à {maintenant.hour}:{maintenant.minute}:{maintenant.second}.json"
        INDEX_SAVE += 1
        assert params_post["form_name"] == "render_queue"
        f1 = open(filename, "r")
        f2 = open(filename2, "w")
        f2.write(f1.read())
        f1.close()
        f2.close()
        liste = json.upload_json(filename)
        i, l = 0, len(liste)
        for set_data in liste :
            print(f"{i}/{l} done")
            print(f"""doing set {set_data["id_set"]}...""")
            response = bdd.ajouter_set(set_data["id_set"], set_data["nom_anglais"], set_data["nom_français"], set_data["gamme"], set_data["annee"], set_data["nb_pieces"], set_data["tranche_age"], set_data["lien_amazon"])
            if not response :
                json.save_json(liste[i:])
                assert response
            i += 1
        print(f"{i}/{l} done")
        if i != l :
            print(i, l)
        assert i == l
        json.save_json([], filename)
        remove(filename2)