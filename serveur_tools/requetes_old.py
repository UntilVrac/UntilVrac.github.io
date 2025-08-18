import os
import urllib.parse
from gestion_bdd import *
from decodage_text import decoder_text

def is_GET(requete:str) -> bool :
    return requete[0:3] == "GET"

def is_POST(requete:str) -> bool :
    return requete[0:4] == "POST"

def get_url(requete:str) -> list :
    u = requete[requete.index("/") + 1:requete.index(" HTTP")]
    if "?" in u :
        return u.split("?")[0] + "?" + u.split("?")[1]
    else :
        return u

def get_params(requete:str) -> dict :
    arguments = [arg.split("=") for arg in requete.split("\n")[-1].split("&")]
    params = {}
    for args in arguments :
        params[args[0]] = args[1]
    return params

def rep_post(url:str, params:dict) -> bytes :
    """z
    params : parametre envoyé par l'utilisateur a travers la fiche
    perm_data : donnée semi-permanente (ici pour connectedppl)
    addrese : address de l'utilisateur
    """
    if url == "BrickStock/ajouter_design" :
        #try :
        largeur, longueur, hauteur = params["dimensions"].lower().split("x")
        largeur, longueur, hauteur = float(largeur), float(longueur), float(hauteur)
        sous_categorie = params["sous_categorie"].replace("+", " ")
        if sous_categorie in ("None", "", " ", "none") :
            sous_categorie = None
        create_new_design(int(params["id_design"]), decoder_text(params["nom"]), params["categorie"], largeur, longueur, hauteur, sous_categorie, chemin_image="images/" + params["chemin_image"].replace("+", " "))
        try :
            pass
        except :
            return get_file("validation", redirection=("http://localhost:1520/BrickStock/ajouter_design", "Erreur : le design n'a pu être ajouté.", "Réessayer"), post=True)
        else :
            return get_file("validation", redirection=("http://localhost:1520/BrickStock", "Les informations ont bien été enregistrées.", "Ok"), post=True)
    elif url == "BrickStock/supprimer_design" :
        try :
            delete_design(params["id_design"])
        except :
            return get_file("validation", redirection=("http://localhost:1520/BrickStock/supprimer_design", "Erreur : le design n'a pu être supprimé.", "Réessayer"))
        else :
            return get_file("validation", redirection=("http://localhost:1520/BrickStock", "La suppression a bien été effectuée.", "Ok"))
    elif url == "BrickStock/ajouter_piece" :
        try :
            create_new_piece_type(int(params["id_piece"].replace("+", " ")), int(params["id_design"].replace("+", " ")), params["couleur"].replace("+", " "), "images/" + params["chemin_image"].replace("+", " "))
        except :
            return get_file("validation", redirection=("http://localhost:1520/BrickStock/ajouter_piece", "Erreur : la pièce n'a pu être ajoutée.", "Réessayer"), post=True)
        else :
            return get_file("validation", redirection=("http://localhost:1520/BrickStock", "Les informations ont bien été enregistrées.", "Ok"), post=True)
    elif url == "BrickStock/supprimer_piece" :
        try :
            delete_piece_type(params["id_piece"])
        except :
            return get_file("validation", redirection=("http://localhost:1520/BrickStock/supprimer_piece", "Erreur : la pièce n'a pu être supprimée.", "Réessayer"))
        else :
            return get_file("validation", redirection=("http://localhost:1520/BrickStock", "La suppression a bien été effectuée.", "Ok"))
    elif url.split("/")[-3:-1] == ["BrickStock", "piece_info"] :
        try :
            maj_data_piece(params["id_piece"], int(params["quantite"]), int(params["nb_disponible"]), int(params["nb_endommage"]))
        except :
            return get_file("validation", redirection=("http://localhost:1520/BrickStock/piece_info/" + params["id_piece"], "Erreur : les données n'ont pu être enregistrées.", "Réessayer"), post=True)
        else :
            return get_file("validation", redirection=("http://localhost:1520/BrickStock", "Les informations ont bien été enregistrées.", "Ok"), post=True)

def page_exist(url:str) -> bool :
    liste_pages = ["BrickStock", "BrickStock/piece_info/*", "BrickStock/ajouter_design", "BrickStock/supprimer_design", "BrickStock/ajouter_piece", "BrickStock/supprimer_piece", "*Fin", "404", "*validation", "*redirection"]
    if url[-1] == "/" :
        url = url[:-1]
    L = len(url)
    for page in liste_pages :
        if "*" in page :
            page = page.split("*")
            i, nb_match = 0, 0
            for part in page :
                l = len(part)
                if i + l <= L :
                    if i == 0 :
                        if url[:l] == part :
                            nb_match += 1
                            i += l
                    elif i + l == L :
                        if url[i:] == part :
                            nb_match += 1
                            i += l
                    else :
                        while i + l <= L :
                            if url[i:i + l] == part :
                                nb_match += 1
                                i += l
                                break
                            else :
                                i += 1
            if nb_match == len(page) :
                return True
        else :
            if page == url :
                return True
    return False

def get_file(filename:str, post:bool=False, redirection:any=None) -> bytes :
    """
    filename : fichier a renvoyé apres modification pour envoi
    perm_data : donnée semi-permanente (ici pour connectedppl)
    post : indique si la requête était de type POST
    url_redirection : indique l'url à suivre une fois la connexion effectuée (utile uniquement pour l'affichage de la page de connexion)
    """
    content_types = {
        ".jpg" : "image/jpeg", 
        ".JPG" : "image/jpeg", 
        ".jpeg" : "image/jpeg", 
        ".JPEG" : "image/jpeg", 
        ".ico" : "image/ico", 
        ".svg" : "image/svg+xml", 
        ".css" : "text/css",
        ".png" : "image/png",
        ".PNG" : "image/png", 
        ".js" : "text/javascipt"
    }
    for ext, content_type in content_types.items() :
        if filename[-len(ext):] == ext :
            entete = f"HTTP/1.1 200 OK\r\nHost: le site local\r\nContent-Type: {content_type}\r\n\r\n"
            try :
                with open(filename, "rb") as file :
                    encoded_content = entete.encode() + file.read()
                return encoded_content
            except :
                return entete.encode()
    href = filename.replace("%2F", "/")
    url, params_get = [], ""
    if "?" in href :
        url, params_get = href.split("?")
        params_get = {e.split("=")[0] : e.split("=")[1] for e in params_get.split("&")}
    else :
        url = href
        params_get = {}
    filename = url.split("/")
    while len(filename) < 2 :
        filename = [None] + filename
    entete = "HTTP/1.1 200 OK\r\nhost: le site local\r\nContent-Type: text/html\r\n\r\n"
    if not page_exist(url) :
        filename.append("404")
        entete = "HTTP/1.1 404 Not Found\r\nhost: le site local\r\nContent-Type: text/html\r\n\r\n"
    elif filename[-2] == "piece_info" :
        try :
            id_piece = int(filename[-1])
            assert piece_in_database(id_piece)
            filename.append("piece_info")
        except :
            filename[-1] = "piece_info-unknowed"
        else :
            pass
    with open(f"html/{filename[-1]}.html") as file :
        content = entete + file.read()
        if filename[-1] == "BrickStock" :
            if "panel" not in params_get :
                params_get["panel"] = "pieces"
            content = content.replace("{panel_pieces?}", {"pieces" : "", "designs" : " hide"}[params_get["panel"]])
            content = content.replace("{panel_designs?}", {"pieces" : " hide", "designs" : ""}[params_get["panel"]])
            listes_resultats_pieces = []
            listes_resultats_designs = []
            if "id_design" in params_get :
                try :
                    listes_resultats_pieces.append(get_pieces_by_design(int(params_get["id_design"])))
                except :
                    return get_file("404")
            if "ton" in params_get :
                try :
                    listes_resultats_pieces.append(get_pieces_by_ton(params_get["ton"]))
                except :
                    return get_file("404")
            if "couleur" in params_get :
                try :
                    listes_resultats_pieces.append(get_pieces_by_color(params_get["couleur"]))
                except :
                    return get_file("404")
            if "dimensions" in params_get :
                try :
                    value = params_get["dimensions"].lower().split["x"]
                    assert 0 < len(value) <= 3
                    values = []
                    for e in value :
                        e = e.replace(",", ".")
                        value.append(float(e))
                    if len(values) == 1 :
                        r = distinct(get_pieces_by_dimensions(largeur=values[0]) + get_pieces_by_dimensions(longueur=values[1]) + get_pieces_by_dimensions(hauteur=values[1]))
                        listes_resultats_pieces.append(r)
                        listes_resultats_designs.append(r)
                    elif len(values) == 2 :
                        r = distinct(get_pieces_by_dimensions(largeur=values[0], longueur=values[1]) + get_pieces_by_dimensions(largeur=values[0], hauteur=values[1]) + get_pieces_by_dimensions(largeur=values[1], longueur=values[0]) + get_pieces_by_dimensions(longueur=values[0], hauteur=values[1]) + get_pieces_by_dimensions(largeur=values[1], hauteur=values[0]) + get_pieces_by_dimensions(longueur=values[1], hauteur=values[0]))
                        listes_resultats_pieces.append(r)
                        listes_resultats_designs.append(r)
                    elif len(values) == 3 :
                        r = distinct(get_pieces_by_dimensions(largeur=values[0], longueur=values[1], hauteur=values[2]) + get_pieces_by_dimensions(largeur=values[0], longueur=values[2], hauteur=values[1]) + get_pieces_by_dimensions(largeur=values[1], longueur=values[0], hauteur=values[2]) + get_pieces_by_dimensions(largeur=values[1], longueur=values[2], hauteur=values[0]) + get_pieces_by_dimensions(largeur=values[2], longueur=values[0], hauteur=values[1]) + get_pieces_by_dimensions(largeur=values[2], longueur=values[1], hauteur=values[0]))
                        listes_resultats_pieces.append(r)
                        listes_resultats_designs.append(r)
                except :
                    return get_file("404")
            if "categorie" in params_get :
                try :
                    r = get_pieces_by_categorie(params_get["categorie"].replace("_", " "))
                    listes_resultats_pieces.append(r)
                    listes_resultats_designs.append(r)
                except :
                    return get_file("404")
            if "sous-categorie" in params_get :
                try :
                    r = get_pieces_by_sub_categorie(params_get["categorie"].replace("_", " "))
                    listes_resultats_pieces.append(r)
                    listes_resultats_designs.append(r)
                except :
                    return get_file("404")
            resultats_pieces = []
            if listes_resultats_pieces == [] :
                resultats_pieces = get_all_pieces()
            else :
                resultats_pieces = intersection_lists(tuple(listes_resultats_pieces))
            tableau_pieces = ""
            i = 0
            couleur_lignes = {0 : 'white', 1 : 'gray'}
            for p in resultats_pieces :
                d = get_piece_info(p[0])
                tableau_pieces += f"""
<tr class="{couleur_lignes[i % 2]}">
    <td style="width: 230px">
        <a href="/{d.chemin_image}" target="_blank">
            <img src="/{d.chemin_image}">
        </a>
    </td>
    <td style="width: 135px">
        <a href="/BrickStock/piece_info/{d.id_piece}" target="_blank">{d.id_piece}</a>
    </td>
    <td style="width: 135px">
        <a href="/BrickStock?panel=pieces&id_design={d.id_design}" target="_blank">{d.id_design}</a>
    </td>
    <td style="width: 165px">
        <a href="/BrickStock?panel=pieces&couleur={d.couleur.replace(" ", "_")}" target="_blank">{d.couleur}</a>
    </td>
    <td style="width: 135px">{d.quantite}</td>
    <td style="width: 90px">{d.nb_disponible}</td>
    <td style="width: 110px">{d.nb_endommage}</td>
</tr>
"""
                i += 1
            content = content.replace("{tableau_pieces}", tableau_pieces)
            if len(resultats_pieces) == 0 :
                content = content.replace("{nb_results_pieces}", "aucun résultat")
            elif len(resultats_pieces) == 1 :
                content = content.replace("{nb_results_pieces}", "1 résultat")
            else :
                content = content.replace("{nb_results_pieces}", str(len(resultats_pieces)) + " résultats")
            resultats_designs = []
            if listes_resultats_designs == [] :
                resultats_designs = get_all_designs()
            else :
                resultats_designs = intersection_lists(tuple(listes_resultats_designs))
                resultats_designs = [get_design_info(p[1]) for p in resultats_designs]
            tableau_designs = ""
            i = 0
            for d in resultats_designs :
                if int(d["largeur"]) == d["largeur"] :
                    d["largeur"] = int(d["largeur"])
                if int(d["longueur"]) == d["longueur"] :
                    d["longueur"] = int(d["longueur"])
                if int(d["hauteur"]) == d["hauteur"] :
                    d["hauteur"] = int(d["hauteur"])
                dimensions = str(d["largeur"]) + "x" + str(d["longueur"]) + "x" + str(d["hauteur"])
                categorie = ""
                if d["sous_categorie"] in ("", "None", None, " ", "NULL") :
                    categorie = f"""<a href="/BrickStock?panel=designs&categorie={d['categorie'].replace(" ", "_")}">{d['categorie']}</a>"""
                else :
                    categorie = f"""<a href="/BrickStock?panel=designs&categorie={d['categorie'].replace(" ", "_")}" target="_blank">{d['categorie']}</a> > <a href="/BrickStock?panel=designs&categorie={d['categorie'].replace(" ", "_")}&sous_categorie={d['sous_categorie'].replace(" ", "_")}" target="_blank">{d['sous_categorie']}</a>"""
                tableau_designs += f"""
<tr class="{couleur_lignes[i % 2]}">
    <td style="width: 228px;">
        <a href="/{d['chemin_image']}" target="_blank">
            <img src="http://localhost:1520/{d['chemin_image']}">
        </a>
    </td>
    <td style="width: 90px;">
        <a href="/BrickStock?panel=pieces&id_design={d['id_design']}" target="_blank">{d["id_design"]}</a>
    </td>
    <td style="width: 150px;">
        <a href="/BrickStock?panel=pieces&id_design={d['id_design']}" target="_blank">{d["nom"]}</a>
    </td>
    <td style="width: 92px;">{dimensions}</td>
    <td style="width: 150px;">
        {categorie}
    </td>
    <td style="width: 90px;">{d["quantite"]}</td>
    <td style="width: 90px;">{d["nb_disponible"]}</td>
    <td style="width: 110px;">{d["nb_endommage"]}</td>
</tr>
"""
                i += 1
            content = content.replace("{tableau_designs}", tableau_designs)
            if len(resultats_designs) == 0 :
                content = content.replace("{nb_results_designs}", "aucun résultat")
            elif len(resultats_designs) == 1 :
                content = content.replace("{nb_results_designs}", "1 résultat")
            else :
                content = content.replace("{nb_results_designs}", str(len(resultats_designs)) + " résultats")
            content = content.replace("{dictCouleurs}", str(get_couleurs_by_tons()))
            content = content.replace("{couleurs}", str(get_liste_couleurs()))
            content = content.replace("{categories}", str(get_liste_categories()))
            content = content.replace("{dictCategories}", str(get_sous_categories_by_categories()))
        elif filename[-1] == "ajouter_piece" :
            content = content.replace("{liste_couleurs}", str(get_liste_couleurs()))
        elif filename[-1] == "piece_info" :
            id_piece = int(filename[-2])
            piece_info = get_piece_info(id_piece)
            content = content.replace("{nom}", piece_info.nom)
            content = content.replace("{src_image}", "http://localhost:1520/" + piece_info.chemin_image)
            content = content.replace("{id_piece}", str(piece_info.id_piece))
            content = content.replace("{id_design}", str(piece_info.id_design))
            content = content.replace("{color}", piece_info.couleur)
            content = content.replace("{dimensions}", piece_info.dimensions)
            categorie = ""
            if piece_info.sous_categorie in ("", "None", None, " ", "NULL") :
                categorie = f"""<a href="/BrickStock?panel=designs&categorie={piece_info.categorie}">{piece_info.categorie}</a>"""
            else :
                categorie = f"""<a href="/BrickStock?panel=designs&categorie={piece_info.categorie}">{piece_info.categorie}</a> > <a href="/BrickStock?panel=designs&categorie={piece_info.categorie}&sous_categorie={piece_info.sous_categorie}>{piece_info.sous_categorie}</a>"""
            content = content.replace("{categorie}", categorie)
            content = content.replace("{quantite}", str(piece_info.quantite))
            content = content.replace("{nb_disponible}", str(piece_info.nb_disponible))
            content = content.replace("{nb_endommage}", str(piece_info.nb_endommage))
        elif filename[-1] == "validation" :
            content = content.replace("{redirection}", redirection[0])
            content = content.replace("{message}", redirection[1])
            content = content.replace("{button}", redirection[2])
        elif filename[-1] == "redirection" :
            if redirection[0:15] == "localhost:1520/" :
                redirection = "http://" + redirection
            elif redirection[0:22] != "http://localhost:1520/" :
                if redirection[0] == "/" :
                    redirection = "http://localhost:1520" + redirection
                else :
                    redirection = "http://localhost:1520/" + redirection
            content = content.replace("{redirection}", redirection)
        elif filename[-1] == "Fin" :
            pass
    return content.encode()