from sys import path
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
path.append(BRICKSTOCK_PATH)

import serveur_tools.scripts_gestion_bdd.gestion_bdd as bdd



def get_couleurs_request(params_get:dict, script:str=None) -> dict :
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
    liste_couleurs = bdd.get_liste_couleurs()
    liste_tons = bdd.get_liste_tons()
    # content = ""
    boutons = ""
    hexa = {"0" : 0, "1" : 1, "2" : 2, "3" : 3, "4" : 4, "5" : 5, "6" : 6, "7" : 7, "8" : 8, "9" : 9, "A" : 10, "B" : 11, "C" : 12, "D" : 13, "E" : 14, "F" : 15}
    i = 1
    for ton in liste_tons :
        c, t = ton["rgb_ref"].upper(), ton["id_ton"]
        if c[0] == "#" :
            c = c[1:]
            couleur = (hexa[c[0]] * 16 + hexa[c[1]], hexa[c[2]] * 16 + hexa[c[3]], hexa[c[4]] * 16 + hexa[c[5]])
            couleur1, couleur2 = tuple([c + 33 if c + 33 <= 255 else 255 for c in couleur]), tuple([c - 33 if c >= 33 else 0 for c in couleur])
            degrade = f"rgb{str(couleur1).replace("'", "")}, rgb{str(couleur).replace("'", "")}, rgb{str(couleur2).replace("'", "")}"
        else :
            couleurs = c.split("-")
            degrade = ""
            for col in couleurs :
                degrade += f'rgb{col.replace(";", ",")}, '
            degrade = degrade[:-2]
        boutons += f'''<a class="bouton_ton" href="#h{i}" style="background: linear-gradient(to top left, {degrade});"></a>'''
        i += 1
    params["{boutons}"] = boutons
    params["{listeTons}"] = liste_tons
    params["{listeCouleurs}"] = {t : [bdd.get_couleur_data(c) for c in liste_couleurs[t]] for t in liste_couleurs}
    return params

def post_couleurs_request(url:str, params_post:dict) -> tuple :
    """
    entrées :
        url (str), l'url courante
        params_post (dict), les paramètres de la requête POST

    renvoie le tuple (url de reponse, script) à utiliser pour la réponse à la requête POST après avoir fait les modifications de la base de données nécéssaires
    """
    if params_post["form_name"] == "add_ton" :
        ton_data = {}
        for p in ("id_ton", "nom", "rgb_ref") :
            assert p in params_post
            f = {"id_ton" : int, "nom" : str, "rgb_ref" : str}[p]
            ton_data[p] = f(params_post[p])
        response = bdd.ajouter_ton(ton_data["id_ton"], ton_data["nom"], ton_data["rgb_ref"])
        if response :
            return (url, "alert('les informations ont bien été enregistré');")
        else :
            return (url, """alert("erreur : les informations n'ont pas été enregistré");""")
    elif params_post["form_name"] == "add_couleur" :
        couleur_data = {}
        for p in ("id_couleur", "id_bricklink", "id_rebrickable", "nom", "nom_lego", "nom_bricklink", "nom_rebrickable", "id_ton", "est_transparent", "image_ref") :
            assert p in params_post
            f = {"id_couleur" : int, "id_bricklink" : int, "id_rebrickable" : int, "nom" : str, "nom_lego" : str, "nom_bricklink" : str, "nom_rebrickable" : str, "id_ton" : int, "est_transparent" : (lambda e : {"true" : True, "false" : False}[e.lower()]), "image_ref" : str}[p]
            couleur_data[p] = f(params_post[p])
        response = bdd.ajouter_couleur(couleur_data["id_couleur"], couleur_data["id_bricklink"], couleur_data["id_rebrickable"], couleur_data["nom"], couleur_data["nom_lego"], couleur_data["nom_bricklink"], couleur_data["nom_rebrickable"], couleur_data["id_ton"], couleur_data["est_transparent"], couleur_data["image_ref"])
        if response :
            return (url, "alert('les informations ont bien été enregistré');")
        else :
            return (url, """alert("erreur : les informations n'ont pas été enregistré");""")
    assert False