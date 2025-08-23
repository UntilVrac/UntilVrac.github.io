from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
path.append(BRICKSTOCK_PATH)

import serveur_tools.scripts_gestion_bdd.gestion_bdd as bdd
from serveur_tools.decodage_text import decoder_text
from serveur_tools.pile import Pile
from serveur_tools.requetes_html.req_pieces import *
from serveur_tools.requetes_html.req_designs import *
from serveur_tools.requetes_html.req_categories import *
from serveur_tools.requetes_html.req_couleurs import *
from serveur_tools.requetes_html.req_sets import *
from serveur_tools.requetes_html.req_minifigures import *
from serveur_tools.requetes_html.req_exemplaires import *
from serveur_tools.requetes_html.req_minifig_in_set import *
from serveur_tools.requetes_html.req_prix import *
from serveur_tools.requetes_html.req_gammes import *
from serveur_tools.requetes_html.req_piece_in_set import *
from serveur_tools.requetes_html.req_rangements import *


HISTORIQUE = Pile()

def render_template(file_path:str, entete, params:dict=None) -> bin :
    """
    entrées :
        file_path (str), le chemin du fichier html à ouvrir
        entete (str), l'en-tête de la réponse
        params (dict), les paramètres à appliquer pour le rendu de la page

    renvoie la page web encodée en utf-8 après remplacement dans son contenu des clées du dictionnaires params par leurs valeurs
    """
    with open("html/" + file_path, "r") as file :
        content = file.read()
    if params != None :
        for p in params :
            content = content.replace(p, str(params[p]))
    return (entete + content).encode()

def is_GET(requete:str) -> bool :
    """
    requete (str), la requête à traiter

    renvoie True si la requête est de type GET et False sinon
    """
    return requete[0:3] == "GET"

def is_POST(requete:str) -> bool :
    """
    requete (str), la requête à traiter

    renvoie True si la requête est de type POST et False sinon
    """
    return requete[0:4] == "POST"

def get_url(requete:str) -> list :
    """
    requete (str), la requête à traiter

    renvoie l'url de la requête
    """
    u = requete[requete.index("/") + 1:requete.index(" HTTP")]
    if "?" in u :
        return u.split("?")[0] + "?" + u.split("?")[1]
    else :
        return u

def get_params(requete:str) -> dict :
    """
    requete (str), la requête POST

    renvoie les paramètres POST sous forme de dictionnaire
    """
    arguments = [arg.split("=") for arg in requete.split("\n")[-1].split("&")]
    params = {}
    for args in arguments :
        params[args[0]] = args[1]
    return params

def page_exist(url:str) -> bool :
    liste_pages = ["BrickStock", "*404", "BrickStock/pieces", "BrickStock/pieces/prix", "BrickStock/designs", "BrickStock/categories", "BrickStock/couleurs", "BrickStock/sets", "BrickStock/sets/exemplaires_du_set", "BrickStock/sets/prix", "BrickStock/minifigures", "BrickStock/minifigures/prix", "BrickStock/sets/minifigs_du_set", "BrickStock/sets/pieces_du_set", "BrickStock/sets/gammes", "BrickStock/minifigures/gammes", "BrickStock/rangements", "BrickStock/rangements/QR-Codes", "*Fin"]
    if len(url) == 0 :
        url = "/"
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

def rep_post(url:str, params_post:dict) -> bytes :
    entete = "HTTP/1.1 200 OK\r\nhost: le site local\r\nContent-Type: text/html\r\n\r\n"
    url = decoder_text(url)
    if not page_exist(url.split("?")[0]) :
        return get_file("404")
    else :
        filename = url.split("?")[0].split("/")
        params_post = {decoder_text(k) : decoder_text(params_post[k]) for k in params_post}
    if filename[-1] in ("BrickStock", "pieces") :
        rep = post_pieces_request(url, params_post)
        return get_file(rep[0], script=rep[1], post=True)
    elif filename[-1] == "designs" :
        rep = post_designs_request(url, params_post)
        return get_file(rep[0], script=rep[1], post=True)
    elif filename[-1] == "categories" :
        rep = post_categories_request(url, params_post)
        return get_file(rep[0], script=rep[1], post=True)
    elif filename[-1] == "couleurs" :
        rep = post_couleurs_request(url, params_post)
        return get_file(rep[0], script=rep[1], post=True)
    elif filename[-1] == "sets" :
        rep = post_sets_request(url, params_post)
        return get_file(rep[0], script=rep[1], post=True)
    elif filename[-1] == "exemplaires_du_set" :
        rep = post_exemplaires_request(url, params_post)
        return get_file(rep[0], script=rep[1], post=True)
    elif filename[-1] == "minifigures" :
        rep = post_minifigs_request(url, params_post)
        return get_file(rep[0], script=rep[1], post=True)
    elif filename[-1] == "minifigs_du_set" :
        if params_post["form_name"] == "search_minifig" :
            params = post_minifig_in_set_search_request(url, HISTORIQUE, params_post)
            # print(params)
            return render_template("minifigs_du_set.html", entete, params=params)
        elif params_post["form_name"] == "save_data" :
            rep = post_minifig_in_set_save_request(params_post)
            return get_file(url, script=rep[1])
    elif filename[-1] == "gammes" :
        rep = post_gammes_request(url, params_post)
        return get_file(rep[0], script=rep[1], post=True)
    elif filename[-1] == "rangements" :
        if params_post["form_name"] == "search_piece" :
            params = post_rangement_content_request(url, params_post)
            return render_template("rangement_content.html", entete, params=params)
        elif params_post["form_name"] == "save_data" :
            rep = post_rangement_save_request(params_post)
        return get_file(url, script=rep)
    assert False

def get_file(filename:str, script:any=None, post:bool=False) -> bytes :
    """
    filename : fichier a renvoyer apres modification pour envoi
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
        ".js" : "text/javascript"
    }
    for ext, content_type in content_types.items() :
        if filename[-len(ext):] == ext :
            entete = f"HTTP/1.1 200 OK\r\nHost: le site local\r\nContent-Type: {content_type}\r\n\r\n"
            if filename[0] == "/" :
                filename = filename[1:]
            if filename.startswith("BrickStock/") :
                filename = filename[11:]
            try :
                print("file :", filename)
                with open(filename, "rb") as file :
                    encoded_content = entete.encode() + file.read()
                return encoded_content
            except :
                return entete.encode()
    href = filename.replace("%2F", "/")
    if not post :
        HISTORIQUE.empiler(href)
        print(HISTORIQUE, "\n\n\n")
    url, params_get = [], ""
    if "?" in href :
        url, params_get = href.split("?")
        params_get = {e.split("=")[0] : e.split("=")[1] for e in params_get.split("&")}
    else :
        url = href
        if len(url) == 0 :
            url = "/"
        params_get = {}
        if url[-1] == "/" :
            url = url[:-1]
    params_get = {decoder_text(k) : decoder_text(params_get[k]) for k in params_get}
    filename = url.split("/")
    while len(filename) < 2 :
        filename = [None] + filename
    entete = "HTTP/1.1 200 OK\r\nhost: le site local\r\nContent-Type: text/html\r\n\r\n"
    if not page_exist(url) :
        filename.append("404")
        entete = "HTTP/1.1 404 Not Found\r\nhost: le site local\r\nContent-Type: text/html\r\n\r\n"
    if filename[-1] == "404" :
        return render_template("404.html", entete)
    elif filename[-1] in ("BrickStock", "pieces") :
        params = get_pieces_request(params_get, script)
        return render_template("pieces.html", entete, params=params)
    elif filename[-1] == "designs" :
        params = get_designs_request(params_get, script)
        return render_template("designs.html", entete, params=params)
    elif filename[-1] == "categories" :
        params = get_categories_request(params_get, script)
        return render_template("categories.html", entete, params=params)
    elif filename[-1] == "couleurs" :
        params = get_couleurs_request(params_get, script)
        return render_template("couleurs.html", entete, params=params)
    elif filename[-1] == "sets" :
        params = get_sets_request(params_get, script)
        return render_template("sets.html", entete, params=params)
    elif filename[-1] == "exemplaires_du_set" :
        params = get_exemplaires_request(params_get, HISTORIQUE, script)
        return render_template("exemplaires_du_set.html", entete, params=params)
    elif filename[-1] == "minifigures" :
        params = get_minifigs_request(params_get, script)
        if not post :
            return render_template("minifigures.html", entete, params=params)
        else :
            return (entete, params)
    elif filename[-1] == "minifigs_du_set" :
        params = get_minifig_in_set_request(params_get, HISTORIQUE, script, post=False)
        return render_template("minifigs_du_set.html", entete, params=params)
    elif filename[-1] == "pieces_du_set" :
        params = get_piece_in_set_request(params_get, HISTORIQUE, script)
        return render_template("gammes.html", entete, params=params)
    elif filename[-1] == "rangements" :
        if "id_rangement" in params_get :
            try :
                id_rangement = int(params_get["id_rangement"])
            except :
                pass
            else :
                if bdd.rangement_est_compartimente(id_rangement) :
                    params = get_rangements_for_id_request(id_rangement)
                    return render_template("rangements.html", entete, params=params)
                else :
                    params = get_rangement_content_request(id_rangement)
                    return render_template("rangement_content.html", entete, params=params)
        elif "id_piece" in params_get :
            try :
                id_piece = int(params_get["id_piece"])
            except :
                pass
            else :
                params = get_rangements_for_piece_request(id_piece)
                return render_template("rangements.html", entete, params=params)
        params = get_rangements_list_request()
        return render_template("rangements.html", entete, params=params)
    elif filename[-1] == "QR-Codes" :
        try :
            id_rangement = int(params_get["id_rangement"])
        except :
            return get_file("/BrickStock/404")
        else :
            return get_file(f"""/BrickStock/images/QR-Codes_rangements/{bdd.get_id_qr_code_rangement(id_rangement)}.png""")
    elif filename[-1] == "Fin" :
        return render_template("Fin.html", entete)
    assert False