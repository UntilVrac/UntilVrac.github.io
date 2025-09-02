from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
path.append(BRICKSTOCK_PATH)

import requests
from serveur_tools.scrap_data import en_tete
from serveur_tools.scripts_gestion_bdd.admin_bdd import MODE_SANS_ECHEC



URL_API = "https://rebrickable.com/api/v3/"

JETON = "dc2a2f4a231edbf3742b0ebf56fbc172"
TOKEN = "11498dd5885f8b802d2c7a63b20d7ec8ad99343d17e5f0cdcfab4d43fabc4d78"




def new_token() -> None :
    response = requests.post(f"https://rebrickable.com/api/v3/users/_token/?key={JETON}", data={"username" : "BrickStock_Fr", "password" : 'c92D=e;}J"fpP8:'})
    if response.status_code == 200 :
        print("token créé")
        t = response.json()["user_token"]
        print(t)
        TOKEN = t
    else :
        print(response)
        print(response.content)



def get_design_data_for_insert_in_bdd(id_to_search:tuple) -> dict :
    """
    id_to_search (tuple), la paire (nom de l'id, id) correspondant à l'id à utiliser pour la recherche
        -> le nom de l'id peut être "id_lego" ou "id_bricklink"
    
    renvoie le dictionnaire {id_rebrickable : str, "nom_rebrickable" : str, "id_bricklink" : str, "list_id_lego" : list} correspondant
    """
    assert id_to_search[0] in ("id_lego", "id_bricklink")
    name_id = {"id_lego" : "lego_id", "id_bricklink" : "bricklink_id"}[id_to_search[0]]
    url = f"https://rebrickable.com/api/v3/lego/parts/?key={JETON}&{name_id}={id_to_search[1]}"
    print(url)
    response = requests.get(url)
    if response.status_code == 200 :
        rep_json = response.json()["results"][0]
        return {"id_rebrickable" : rep_json["part_num"], "nom_rebrickable" : rep_json["name"], "id_bricklink" : rep_json["external_ids"]["BrickLink"][0], "list_id_lego" : rep_json["external_ids"]["LEGO"]}
    return None

def get_image_ref_set(id_set:int) -> str :
    """
    id_set (int), id du set
    
    renvoie l'url de l'image ref : l'url de l'image de la du design en blanc s'il existe dans cette couleur, du site lego si elle y est, sinon du site bricklink voir du site rebrickable si cette image n'existe pas non plus sur le site bricklink en cas d'échec total, renvoie None
    """
    url1 = f"https://www.lego.com/cdn/cs/set/assets/bltb2f5c7b4630484df/{id_set}_alt1.jpg?format=png&fit=bounds&dpr=3"
    rep1 = requests.get(url1)
    if rep1.status_code == 200 :
        return url1
    url2 = f"https://img.bricklink.com/ItemImage/ON/0/{id_set}-1.png"
    rep2 = requests.get(url2)
    if rep2.status_code == 200 :
        return url2
    url3 = f"https://rebrickable.com/api/v3/lego/sets/{id_set}-1/?key={JETON}"
    rep3 = requests.get(url3)
    if rep3.status_code == 200 :
        return rep3.json()["set_img_url"]
    return None



'''
def get_image_ref_design(id_bricklink:str, id_rebrickable:str) -> str :
    """
    entrées :
        id_bricklink (str) et id_rebrickable (str), les id du design
    renvoie l'url de l'image ref : l'url de l'image de la du design en blanc s'il existe dans cette couleur, du site lego si elle y est, sinon du site bricklink voir du site rebrickable si cette image n'existe pas non plus sur le site bricklink
    en cas d'échec total, renvoie None
    """

    def try_get_image_ref(c) :
        couleur_data = get_couleur_data(c)
        url1 = f"https://rebrickable.com/api/v3/lego/parts/{id_rebrickable}/colors/{couleur_data[2]}/?key={JETON}"
        print(url1)
        rep1 = requests.get(url1)
        if rep1.status_code == 200 :
            liste_elements = rep1.json()["elements"]
            for id_element in liste_elements :
                url2 = f"https://www.lego.com/cdn/product-assets/element.spin.photoreal/{id_element}/00001.png"
                print(url2)
                rep2 = requests.get(url2, headers=en_tete)
                if rep2.status_code == 200 :
                    return url2
                
        url3 = f"https://img.bricklink.com/ItemImage/PN/{couleur_data[1]}/{id_bricklink}.png"
        print(url3)
        rep3 = requests.get(url3, headers=en_tete)
        if rep3.status_code == 200 :
            return url3
        elif rep3.status_code == 200 :
            return rep3.json()["part_img_url"]
        return None
        
    dict_couleurs = get_liste_couleurs()
    tons_used = [10, 11, 12, 17, 30]
    liste_couleurs = dict_couleurs[10] + dict_couleurs[11] + dict_couleurs[12] + dict_couleurs[17] + dict_couleurs[21]
    for t in dict_couleurs :
        if t not in tons_used :
            liste_couleurs += dict_couleurs[t]
    # print(liste_couleurs)
    for c in liste_couleurs :
        img = try_get_image_ref(c[0])
        if img != None :
            return img
    return None
'''

def get_image_ref_design(id_bricklink:str, id_rebrickable:str, dict_couleurs:dict, data_couleurs:dict) -> str :
    """
    entrées :
        id_bricklink (str) et id_rebrickable (str), les id du design
        dict_couleurs (dict), dictionnaire {id_ton : [liste des id_couleur]}
        data_couleurs (dict), les données des couleurs
    renvoie l'url de l'image ref : l'url de l'image de la du design en blanc s'il existe dans cette couleur, du site lego si elle y est, sinon du site bricklink voir du site rebrickable si cette image n'existe pas non plus sur le site bricklink
    en cas d'échec total, renvoie None
    """

    def try_get_image_ref(c:int) -> str :
        """
        c (int), l'id de la couleur à tester

        renvoie l'url de l'image si elle est trouvé et None sinon
        """
        couleur_data = data_couleurs[c]
        url1 = f"https://rebrickable.com/api/v3/lego/parts/{id_rebrickable}/colors/{couleur_data["id_rebrickable"]}/?key={JETON}"
        # print(url1)
        rep1 = requests.get(url1)
        if rep1.status_code == 200 :
            liste_elements = rep1.json()["elements"]
            for id_element in liste_elements :
                url2 = f"https://www.lego.com/cdn/product-assets/element.spin.photoreal/{id_element}/00001.png"
                print(url2)
                rep2 = requests.get(url2, headers=en_tete)
                if rep2.status_code == 200 :
                    return url2
                
        url3 = f"https://img.bricklink.com/ItemImage/PN/{couleur_data["id_bricklink"]}/{id_bricklink}.png"
        # print(url3)
        rep3 = requests.get(url3, headers=en_tete)
        if rep3.status_code == 200 :
            return url3
        elif rep3.status_code == 200 :
            return rep3.json()["part_img_url"]
        return None
        
    tons_used = [10, 11, 12, 17, 30]
    liste_couleurs = dict_couleurs[10] + dict_couleurs[11] + dict_couleurs[12] + dict_couleurs[17] + dict_couleurs[21]
    for t in dict_couleurs :
        if t not in tons_used :
            liste_couleurs += dict_couleurs[t]
    # print(liste_couleurs)
    for c in liste_couleurs :
        img = try_get_image_ref(c)
        if img != None :
            return img
    return None

def get_image_ref_piece(id_piece:int, id_design:int, id_couleur:int, design_infos:dict, couleur_data:dict) -> str :
    """
    entrées :
        id_piece (int), id de la pièce
        id_design (int), id du design de la pièce
        id_couleur (int), id de la couleur de la pièce
        design_infos (dict), les infos du design
        couleur_data (dict), les infos de la couleur
    renvoie l'url de l'image ref : l'url de l'image de la boite du set du site lego si elle y est, sinon du site bricklink voir du site rebrickable
    en cas d'échec total, renvoie None
    """
    url1 = f"https://www.lego.com/cdn/product-assets/element.spin.photoreal/{id_piece}/00001.png"
    print(url1)
    rep1 = requests.get(url1, headers=en_tete)
    if rep1.status_code == 200 :
        return url1
    url2 = f"https://img.bricklink.com/ItemImage/PN/{couleur_data[1]}/{design_infos["id_bricklink"]}.png"
    print(url2)
    rep2 = requests.get(url2, headers=en_tete)
    if rep2.status_code == 200 :
        return url2
    url3 = f"https://rebrickable.com/api/v3/lego/parts/{design_infos["id_rebrickable"]}/colors/{couleur_data[2]}/?key={JETON}"
    print(url3)
    rep3 = requests.get(url3)
    if rep3.status_code == 200 :
        return rep3.json()["part_img_url"]
    return None

def get_image_ref_couleur(color_id:int) -> str :
    """
    color_id (int), color_id rebrickable

    renvoie l'url d'une image ref, renvoie None
    """
    url = f"https://rebrickable.com/api/v3/lego/parts/3005/colors/{color_id}/?key={JETON}"
    # print(url)
    response = requests.get(url)
    if response.status_code == 200 :
        return response.json()["part_img_url"]
    return None

def get_image_ref_minifig(id_minifig:str, id_rebrickable:str) -> str :
    """
    entrées :
        id_minifig (str) et id_rebrickable (str), les id de la minifigure
    renvoie l'url de l'image ref : l'url de l'image de la minifig du site bricklink si elle y est, sinon du site rebrickable
    en cas d'échec total, renvoie None
    """
    url1 = f"https://img.bricklink.com/ItemImage/MN/0/{id_minifig}.png"
    # print(url1)
    rep1 = requests.get(url1, headers=en_tete)
    # print(rep1.status_code)
    if rep1.status_code == 200 :
        return url1
    url2 = f"https://rebrickable.com/api/v3/lego/minifigs/{id_rebrickable}/?key={JETON}"
    # print(url2)
    rep2 = requests.get(url2)
    print(rep2.status_code)
    if rep2.status_code == 200 :
        return rep2.json()["set_img_url"]
    return None

def get_liste_parts_in_set(id_set:int) -> list :
    """
    id_set (int), id du set

    renvoie la liste des elements du set sous forme d'une liste de tuple (part_num rebrickable (str), color_id rebrickable (int), quantité (int))
    renvoie None en cas d'échec de la requête vers l'api rebrickable
    """
    url = f"https://rebrickable.com/api/v3/lego/sets/{id_set}-1/parts/?key={JETON}"
    # print(url)
    response = requests.get(url)
    if response.status_code == 200 :
        count = response.json()["count"]
        # print(count)
        url2 = f"https://rebrickable.com/api/v3/lego/sets/{id_set}-1/parts/?key={JETON}&page_size={count}"
        # print(url2)
        response2 = requests.get(url2)
        if response2.status_code == 200 :
            rep_json = response2.json()["results"]
            r = []
            for p in rep_json :
                r.append((p["part"]["part_num"], p["color"]["id"], p["quantity"]))
            return r
    return None

def get_image_for_unknown_part(part_num:str, color_id:int) -> str :
    """
    entrées :
        part_num (str), l'id rebrickable du design
        color_id (int), id rebrickable de la couleur

    renvoie l'url de l'image de référence rebrickable correspondante
    renvoie None en cas d'échec
    """
    url = f"https://rebrickable.com/api/v3/lego/part/{part_num}/colors/{color_id}/?key={JETON}"
    # print(url)
    response = requests.get(url)
    if response.status_code == 200 :
        return response.json()["part_img_url"]
    return None

def get_rebrickable_image_ref_piece(part_num:str, color_id:int) -> str :
    """
    entrées :
        part_num (str), l'id rebrickable du design
        color_id (str), l'id rebrickable de la couleur
    
    renvoie l'url de l'image ref rebrickable
    renvoie None en cas d'échec
    """
    url = f"https://rebrickable.com/api/v3/lego/parts/{part_num}/colors/{color_id}/?key={JETON}"
    # print(url)
    response = requests.get(url)
    if response.status_code == 200 :
        return response.json()["part_img_url"]
    return None

def get_part_infos(part_num:str) -> dict :
    """
    part_num (str), l'id rebrickable du design

    renvoie les informations de rebrickable correspondantes sous la forme du dictionnaire {id_lego : list[int], id_bricklink : str, id_rebrickable : str, nom_rebrickable : str}
    renvoie None en cas d'échec
    """
    url = f"https://rebrickable.com/api/v3/lego/parts/{part_num}/?key={JETON}"
    # print(url)
    response = requests.get(url)
    if response.status_code == 200 :
        rep_json = response.json()
        infos = {}
        if "LEGO" in rep_json["external_ids"] :
            infos["id_lego"] = [int(e) for e in rep_json["external_ids"]["LEGO"]]
        else :
            infos["id_lego"] = []
        if "BrickLink" in rep_json["external_ids"] :
            infos["id_bricklink"] = rep_json["external_ids"]["BrickLink"][0]
        else :
            infos["id_bricklink"] = None
        infos["id_rebrickable"], infos["nom_rebrickable"] = part_num, rep_json["name"]
        return infos
    print(response.status_code)
    if MODE_SANS_ECHEC :
        return None
    else :
        print(part_num)
        assert False

def get_color_infos(color_id:int) -> dict :
    """
    color_id (int), id rebrickable de la couleur

    renvoie les informations de rebrickable correspondantes sous la forme du dictionnaire {nom_lego : list, id_bricklink : int, nom_bricklink : str, id_rebrickable : int, nom_rebrickable : str} avec pour valeur None lorsque l'information correspondant à la clée n'a pas été trouvée
    renvoie None en cas d'échec
    """
    url = f"https://rebrickable.com/api/v3/lego/colors/{color_id}/?key={JETON}&page_size=500"
    # print(url)
    response = requests.get(url)
    if response.status_code == 200 :
        c = response.json()
        infos = {}
        if "LEGO" in c["external_ids"] :
            infos["nom_lego"] = c["external_ids"]["LEGO"]["ext_descrs"]
        else :
            infos["nom_lego"] = None
        if "BrickLink" in c["external_ids"] :
            infos["id_bricklink"] = c["external_ids"]["BrickLink"]["ext_ids"][0]
            infos["nom_bricklink"] = c["external_ids"]["BrickLink"]["ext_descrs"][0]
        else :
            infos["id_bricklink"], infos["nom_bricklink"] = None, None
        infos["id_rebrickable"], infos["nom_rebrickable"], infos["est_transparent"] = color_id, c["name"], [c["is_trans"]]
        return infos
    return None



if __name__ == "__main__" :
    pass
    # print(get_image_ref_design(3005, "30005", "3005"))
    # print()
    # print(get_image_ref_design(94925, "94925", "94925"))
    # print(get_image_ref_piece(300501, 3005, 1000))
    # print(get_image_ref_design("3005", "3005"))
    # print(get_image_ref_design("3005", "3005", True))
    # print(get_liste_parts_in_set(75345))
    print(get_image_ref_minifig("sw1431", "fig-016594"))