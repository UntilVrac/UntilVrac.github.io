from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
path.append(BRICKSTOCK_PATH)

import serveur_tools.scripts_gestion_bdd.gestion_bdd as bdd



def get_pieces_request(params_get:dict, script:str=None) -> dict :
    """
    entrées :
        params_get (dict) : les paramètres get
        script (str) : le script (None par défaut)

    renvoie les paramètres de modifications pour le rendu de la page web
    """
    params = {"{" + p + "}" : params_get[p] for p in params_get}
    if script == None :
        params["{script}"] = ""
    else :
        params["{script}"] = f"""<script type="text/javascript">{script}</script>"""
    search_result = bdd.search_piece({k : params_get[k] for k in params_get if params_get[k] not in ("", "0")})
    for p in ("nom", "id_design", "ton", "couleur", "dimensions", "categorie", "sous_categorie") :
        if "{" + p + "}" not in params :
            params["{" + p + "}"] = ""
    cases = ""
    i = 1
    for r in search_result :
        cases += f"""<div class="block_resultat" id="resultat{i}">
<img class="apercu" src="{r["image_ref"]}">
<h4>{r["nom"]}</h4>
<span>ID : {r["id_piece"]} / {r["id_design"]}</span><br/>
<span>couleur : {r["nom_couleur"]}</span>
</div>"""
        i += 1
    if search_result == [] :
        cases = "<span>aucun résultat</span>"
    params["{cases}"] = cases
    params["{resultats}"] = search_result
    liste_tons = ""
    for t in bdd.get_liste_tons() :
        if "ton" in params_get :
            if params_get["ton"] == str(t["id_ton"]) :
                liste_tons += f"""<option selected value="{t["id_ton"]}">{t["nom_ton"]}</option>"""
            else :
                liste_tons += f"""<option value="{t["id_ton"]}">{t["nom_ton"]}</option>"""
        else :
            liste_tons += f"""<option value="{t["id_ton"]}">{t["nom_ton"]}</option>"""
    params["{liste_tons}"] = liste_tons
    params["{liste_couleurs}"] = bdd.get_liste_couleurs()
    if "couleur" in params_get :
        params["{couleur_filter}"] = params_get["couleur"]
    else :
        params["{couleur_filter}"] = "0"
    if "opaque" not in params_get and "transparent" not in params_get :
        params["{opaque_checkbox}"] = " checked"
        params["{transparent_checkbox}"] = " checked"
    else :
        if "opaque" in params_get :
            params["{opaque_checkbox}"] = " checked"
        else :
            params["{opaque_checkbox}"] = ""
        if "transparent" in params_get :
            params["{transparent_checkbox}"] = " checked"
        else :
            params["{transparent_checkbox}"] = ""
    if "sous_categorie" in params_get :
        params["{categorie_filter}"] = params_get["sous_categorie"]
    else :
        params["{categorie_filter}"] = "0"
    liste_categories = ""
    liste_categorie_dict = [bdd.get_infos_categorie(id) for id in bdd.get_liste_categories_racines()]
    for c in liste_categorie_dict :
        if "categorie" in params_get :
            if params_get["categorie"] == str(c["id_categorie"]) :
                liste_categories += f"""<option selected value="{c['id_categorie']}">{c['nom_categorie']}</option>"""
            else :
                liste_categories += f"""<option value="{c['id_categorie']}">{c['nom_categorie']}</option>"""
        else :
            liste_categories += f"""<option value="{c['id_categorie']}">{c['nom_categorie']}</option>"""
    params["{liste_categories}"] = liste_categories
    params["{liste_sous_categories}"] = {c["id_categorie"] : [[sc, bdd.get_infos_categorie(sc)["nom_categorie"]] for sc in bdd.get_liste_sous_categories(c["id_categorie"], direct=False)] for c in liste_categorie_dict}
    liste_couleur_add = ""
    lc = []
    liste_couleurs = bdd.get_liste_couleurs()
    for t in liste_couleurs :
        for c in liste_couleurs[t] :
            lc.append(bdd.get_couleur_data(c))
    for c in lc :
        liste_couleur_add += f"""<option value="{c["id_couleur"]}">{c["nom"]}</option>"""
    params["{liste_couleur_add}"] = liste_couleur_add
    liste = [params["{liste_couleurs}"][k] for k in params["{liste_couleurs}"]]
    params["{liste_all_couleurs}"] = []
    for e in liste :
        params["{liste_all_couleurs}"] += e
    liste = [params["{liste_sous_categories}"][k] for k in params["{liste_sous_categories}"]]
    params["{liste_all_categories}"] = []
    for e in liste :
        params["{liste_all_categories}"] += e
    return params

def post_pieces_request(url:str, params_post:dict) -> tuple :
    """
    entrées :
        url (str), l'url courante
        params_post (dict), les paramètres de la requête POST

    renvoie le tuple (url de reponse, script) à utiliser pour la réponse à la requête POST après avoir fait les modifications de la base de données nécéssaires
    """
    if params_post["form_name"] == "add_piece" :
        piece_data = {}
        for p in ("id_piece", "id_design", "couleur") :
            assert p in params_post
            f = {"id_piece" : int, "id_design" : int, "couleur" : int}[p]
            piece_data[p] = f(params_post[p])
        try :
            assert "prix_site_lego" in params_post
            p = float(params_post["prix_site_lego"].replace(",", "."))
            assert p >= 0
            piece_data["prix_site_lego"] = p
        except :
            piece_data["prix_site_lego"] = None
        response = bdd.ajouter_piece(piece_data["id_piece"], piece_data["id_design"], piece_data["couleur"], piece_data["prix_site_lego"])
        if response :
            return (url, "alert('les informations ont bien été enregistrées');")
        else :
            return (url, """alert("erreur : les informations n'ont pas été enregistrées");""")
    elif params_post["form_name"] == "piece_quantity" :
        id_piece = int(params_post["id_piece"])
        quantite, disponible, endommagee = int(params_post["quantite"]), int(params_post["disponible"]), int(params_post["endommagee"])
        try :
            assert quantite >= 0
            assert disponible >= 0
            assert endommagee >= 0
            assert quantite >= disponible
            assert quantite >= endommagee
            assert bdd.piece_est_dans_moc(id_piece)
        except :
            return (url, """alert("erreur : les quantités doivent être supérieurs ou égales à 0 et le nombre total de pièces doit être supérieur ou égal aux nombres de pièces disponibles et endommagées");""")
        response = bdd.update_moc_piece_qt(id_piece, quantite, disponible, endommagee)
        if response :
            return (url, "alert('les informations ont bien été enregistrées');")
        else :
            return (url, """alert("erreur : les informations n'ont pas été enregistrées");""")
    assert False



if __name__ == "__main__" :
    pass
    # print(get_pieces_request({}))