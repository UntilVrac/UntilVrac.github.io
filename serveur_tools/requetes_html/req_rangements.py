from sys import path
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
path.append(BRICKSTOCK_PATH)

import serveur_tools.scripts_gestion_bdd.gestion_bdd as bdd
from serveur_tools.qr_code import FORMATS_STANDARDS



def get_rangements_for_id_request(id_rangement:int) -> dict :
    """
    id_rangement (int), id du rangement

    renvoie les paramètres de modifications pour le rendu de la page web (cas où l'id_rangement est donné en paramètre GET)
    """
    arbre_rangements = bdd.get_arbre_rangements(id_rangement)
    infos = bdd.get_rangements_infos(id_rangement)
    path = bdd.get_rangement_path(id_rangement)
    path.append(infos)
    li_content = ""
    for e in arbre_rangements["contenu"] :
        li_content += f"""<li>
    <a href="/BrickStock/rangements?id_rangement={e["id_rangement"]}">{bdd.get_rangements_infos(e["id_rangement"])["nom_rangement"]}</a>
</li>"""
    contenu = f"""<span>{" > ".join([f'''<a href="/BrickStock/rangements?id_rangement={e["id_rangement"]}">{e["nom_rangement"]}</a>''' for e in path])}</span><br/>
<ul class="level level{len(bdd.get_rangement_path(id_rangement)) + 1}">
    {li_content}
</ul>"""
    params = {"{content}" : contenu, "{script}" : ""}
    return params

def get_rangement_content_request(id_rangement:int, params_get:dict=None) -> dict :
    """
    entrées :
        id_rangement (int), id du rangement
        params_get (dict) ({} par défaut), les paramètres GET

    renvoie les paramètres de modifications pour le rendu de la page web (cas un id_piece est donné en paramètre GET)
    """
    if params_get == None :
        params_get = {}
    infos_rangement = bdd.get_rangements_infos(id_rangement)
    path = bdd.get_rangement_path(id_rangement)
    # path.append(infos_rangement)
    params = {"{path_rangement}" : f"""<span>{" > ".join([f'''<a href="/BrickStock/rangements?id_rangement={e["id_rangement"]}">{e["nom_rangement"]}</a>''' for e in path])}</span>""", "{id_rangement}" : id_rangement, "{type_rangement}" : infos_rangement["type_rangement"], "{qr_code_href}" : f"""/BrickStock/rangements/QR-Codes?id_rangement={id_rangement}""", "{id_qr-code}" : id_rangement, "{script}" : ""}
    try :
        liste_content = [(int(e.split(" : ")[0]), e.split(" : ")[1]) for e in params_get["liste_pieces"].split(", ")]
        params["{value_input}"] = params_get["liste_pieces"]
    except :
        liste_content = bdd.get_rangement_content(id_rangement)
        params["{value_input}"] = {e[0] : e[1] for e in liste_content}
    content = ""
    i = 1
    for e in liste_content :
        if e[1] == "pièce" :
            piece_infos = bdd.get_piece_info(e[0])
            content += f"""<div class="item_minifig" id="element{i}">
    <input type="hidden" id="type_element{i}" value="piece">
    <input type="hidden" id="id_element{i}" value="{piece_infos["id_piece"]}">
    <img id="bouton_supprimer{i}" class="supprimer_item" src="/BrickStock/images/croix.svg">
    <img class="type_element" src="{bdd.get_couleur_data(piece_infos["id_couleur"])["image_ref"]}">
    <img class="apercu" src="{piece_infos["image_ref"]}">
    <span>id pièce&nbsp;: {piece_infos["id_piece"]}</span>
    <span>id design&nbsp;: {piece_infos["id_design"]}</span><br/>
    <span style="font-weight: bold;">{piece_infos["nom"]}</span>
</div>"""
        else :
            design_infos = bdd.get_design_info(e[0])
            content += f"""<div class="item_minifig" id="element{i}">
    <input type="hidden" id="type_element{i}" value="design">
    <input type="hidden" id="id_element{i}" value="{design_infos["id_design"]}">
    <img id="bouton_supprimer{i}" class="supprimer_item" src="/BrickStock/images/croix.svg">
    <img class="type_element" src="/BrickStock/images/palette.png">
    <img class="apercu" src="{design_infos["image_ref"]}">
    <span>id design&nbsp;: {design_infos["id_design"]}</span><br/>
    <span style="font-weight: bold;">{design_infos["nom"]}</span>
</div>"""
        i += 1
    params["{content}"] = content
    params_search = {}
    infos_search = ("nom", "id_design", "dimensions", "categorie", "sous_categorie")
    for p in infos_search :
        if p + "_search" in params_get :
            if p in ("categorie", "sous_categorie") :
                try :
                    if params_get[p + "_search"] != "0" :
                        params_search[p] = int(params_get[p + "_search"])
                except :
                    pass
            elif params_get[p + "_search"] != "" :
                params_search[p] = params_get[p + "_search"]
    resultats_search = bdd.search_piece(params_search)
    cases = ""
    i = 1
    # liste_pieces = [e[0] for e in liste_content if e[1] == "pièce"]
    for r in resultats_search :
        # if r["id_piece"] not in liste_pieces :
        cases += f"""<div class="block_resultat" id="resultat{i}">
    <input type="hidden" value="{r["id_piece"]}" id="id_piece{i}">
    <input type="hidden" value="{r["id_design"]}" id="id_design{i}">
    <img class="apercu" src="{r["image_ref"]}">
    <h4>{r["nom"]}</h4>
    <span>id pièce&nbsp;: {r["id_piece"]}</span><br/>
    <span>id design&nbsp;: {r["id_design"]}</span>
    <input type="submit" value="AJOUTER LA PIÈCE" class="bouton_validation_infos enregistrer" style="border-radius: 4px; width: 162px; margin-top: 8px;" id="ajouter_piece_{i}">
    <input type="submit" value="AJOUTER LE DESIGN" class="bouton_validation_infos enregistrer" style="border-radius: 4px; width: 174px; margin-top: 8px;" id="ajouter_design{i}">
</div>"""
        i += 1
    params["{cases}"] = cases
    for e in resultats_search :
        e["design_data"] = bdd.get_design_info(e["id_design"])
        e["couleur_data"] = bdd.get_couleur_data(e["id_couleur"])
    params["{resultats}"] = resultats_search
    # params["{resultats}"] = resultats_search
    for p in infos_search[:3] :
        p = p + "_search"
        if p in params_get :
            params["{" + p + "}"] = params_get[p]
        else :
            params["{" + p + "}"] = ""
    cat, sous_cat = 0, 0
    if "categorie" in params_search :
        cat = params_search["categorie"]
    if "sous_categorie" in params_search :
        sous_cat = params_search["sous_categorie"]
    liste_cat = ""
    for c in bdd.get_liste_categories_racines() :
        if c == cat :
            select = " selected"
        else :
            select = ""
        liste_cat += f"""<option{select} value="{c}">{bdd.get_infos_categorie(c)["nom_categorie"]}</option>"""
    liste_sous_cat = ""
    if cat != 0 :
        for c in bdd.get_liste_sous_categories(cat) :
            if c == sous_cat :
                select = " selected"
            else :
                select = ""
            liste_sous_cat += f"""<option{select} value="{c}">{bdd.get_infos_categorie(c)["nom_categorie"]}</option>"""
    params["{liste_cat}"] = liste_cat
    liste_categorie_dict = [bdd.get_infos_categorie(id) for id in bdd.get_liste_categories_racines()]
    params["{liste_sous_categories}"] = {c["id_categorie"] : [[sc, bdd.get_infos_categorie(sc)["nom_categorie"]] for sc in bdd.get_liste_sous_categories(c["id_categorie"], direct=False)] for c in liste_categorie_dict}
    liste = [params["{liste_sous_categories}"][k] for k in params["{liste_sous_categories}"]]
    params["{liste_all_categories}"] = []
    for e in liste :
        params["{liste_all_categories}"] += e
    if "sous_categorie_search" in params_get :
        params["{categorie_filter}"] = params_get["sous_categorie_search"]
    else :
        params["{categorie_filter}"] = "0"
    return params

def get_rangements_for_piece_request(id_piece:int) -> dict :
    """
    id_piece (int), id de la pièce dont on doit récupérer le rangement

    renvoie les paramètres de modifications pour le rendu de la page web (cas un id_piece est donné en paramètre GET)
    """

def get_rangements_list_request() -> dict :
    """
    renvoie les paramètres de modifications pour le rendu de la page web (cas où aucune information n'est donnée en paramètre GET -> renvoie de la liste des rangements)
    """
    arbre_rangements = bdd.get_arbre_rangements()
    contenu = ""
    for e in arbre_rangements["contenu"] :
        contenu += f"""<li>
        <a href="/BrickStock/rangements?id_rangement={e["id_rangement"]}">{bdd.get_rangements_infos(e["id_rangement"])["nom_rangement"]}</a>
    </li>"""
    params = {"{content}" : f"""<ul class="level level0">{contenu}</ul>""", "{script}" : "", "{id_rangement}" : 0}
    return params

def get_print_qrcodes_request() -> dict :
    """
    renvoie les paramètres de modifications pour le rendu de la page web (cas où aucune information n'est donnée en paramètre GET -> renvoie de la liste des rangements)
    """
    return {"{FORMATS_STANDARDS}" : {k : [int(FORMATS_STANDARDS[k][0]), int(FORMATS_STANDARDS[k][1])] for k in FORMATS_STANDARDS}, "{script}" : ""}

def post_add_rangement(params_post:dict) -> str :
    """
    params_post (dict), les paramètres de la requête POST

    renvoie le script à utiliser pour la réponse à la requête POST après avoir fait les modifications de la base de données nécéssaires
    """
    response = bdd.ajouter_rangement(params_post["nom"], params_post["type_rangement"], int(params_post["nb_compartiments"]), params_post["compartimentation"], int(params_post["id_rangement_parent"]))
    if response :
        return """alert("les informations ont bien été enregistré");"""
    else :
        return """alert("erreur : les informations n'ont pas été enregistré");"""

def post_rangement_content_request(url:str, params_post:dict) -> dict :
    """
    entrées :
        url (str), l'url courante
        params_post (dict), les paramètres de la requête POST

    renvoie les paramètres de modifications pour le rendu de la page web
    """
    params_get = {e.split("=")[0] : e.split("=")[1] for e in url.split("?")[1].split("&")}
    params_get = {"id_rangement" : params_get["id_rangement"], "nom_search" : params_post["nom"], "id_design_search" : params_post["id_design"], "dimensions_search" : params_post["dimensions"], "categorie_search" : params_post["categorie"], "sous_categorie_search" : params_post["sous_categorie"], "liste_pieces" : params_post["liste_pieces"]}
    params = get_rangement_content_request(int(params_get["id_rangement"]), params_get=params_get)
    return params

def post_rangement_save_request(params_post:dict) -> str :
    """
    params_post (dict), les paramètres de la requête POST

    renvoie le script à utiliser pour la réponse à la requête POST après avoir fait les modifications de la base de données nécéssaires
    """
    if params_post["liste_pieces"] in ("{}", "{  }") :
        liste_elements = []
    else :
        try :
            liste_elements = []
            for e in params_post["liste_pieces"][1:-1].split(", ") :
                k, v = e.split(" : ")
                k = int(k)
                assert v in ("pièce", "design")
                if v == "pièce" :
                    assert bdd.piece_in_database(k)
                else :
                    assert bdd.design_in_database(k)
                liste_elements.append(k)
        except :
            return """alert('erreur : les éléments sélectionnés ne sont pas répertoriés ou le type d'élément est invalide (le type d'élément doit être "pièce" ou "design")');"""
    try :
        id_rangement = int(params_post["id_rangement"])
    except :
        return """alert("erreur : id de rangement invalide");"""
    response = bdd.update_rangement_content(id_rangement, liste_elements)
    if response :
        return """alert("les informations ont bien été enregistré");"""
    else :
        return """alert("erreur : les informations n'ont pas été enregistré");"""