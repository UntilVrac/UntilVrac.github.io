from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
path.append(BRICKSTOCK_PATH)

import serveur_tools.scripts_gestion_bdd.gestion_bdd as bdd
from serveur_tools.pile import Pile
from serveur_tools.json_tools import upload_json
import serveur_tools.requetes_api as api



def get_piece_in_set_request(params_get:dict, HISTORIQUE:Pile, script:str=None, post:bool=False) -> dict :
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
    if script == None :
        params["{script}"] = ""
    else :
        params["{script}"] = script
    id_set = params_get["id_set"]
    data_set = bdd.get_set_data(id_set)
    params["{image_ref_set}"], params["{id_set}"], params["{gamme_set}"], params["{annee_set}"], params["{nb_pieces_set}"] = data_set["image_ref"], id_set, data_set["{nom_gamme}"], data_set["annee"], data_set["nb_pieces"]
    liste_pieces_known = bdd.get_piece_in_set(id_set)
    liste_pieces_connues = ""
    for p in liste_pieces_known :
        piece_infos = bdd.get_piece_info(p[0])
        liste_pieces_connues += f"""<div class="item_minifig">
    <img class="apercu" src="{piece_infos["image_ref"]}">
    <span>Id de la pièce&nbsp;: <a href="/BrickStock/pieces?nom={piece_infos["nom"]}">{piece_infos["id_piece"]}</a></span><br/>
    <span>Id du design&nbsp;: <a href="/BrickStock/pieces?id_design={piece_infos["id_design"]}>{piece_infos["id_design"]}</a></span><br/>
    <span>{piece_infos["nom"]}</span>
    <div class="quantity_box" style="margin-top: 12px;">
        <input required type="number" readonly class="valeur" style="width: 56px;" min="0" name="quantite" value="{p[1]}">
    </div>
</div>"""
    params["{listePiecesConnues}"] = liste_pieces_connues
    liste_pieces_inconnues = {}
    n = 0
    liste_pieces_unknown = upload_json("/data_save/piece_in_set_data/{id_set}.json")
    transparence = {True : "oui", False : "non"}
    resultats = []
    if liste_pieces_unknown != None :
        for p in liste_pieces_unknown :
            n += 1
            if p["design"]["statut"] == "find" :
                design_data = bdd.get_design_info(p["design"]["id_design"],)
                design_infos = f"""<span style="font-weight: bold;">Design connu&nbsp;:</span>
<img class="apercu" src="{design_data["image_ref"]}">
<span>id du design&nbsp;: <a href="/BrickStock/pieces?id_design={design_data["id_design"]}">{design_data["id_design"]}</span>
<span>{design_data["nom"]}</span>
<span>catégorie&nbsp;: {design_data["categorie_span"]}</span>
<span>dimensions&nbsp;: {design_data["dimensions_stud"]}</span>"""
            else :
                img_ref = api.get_image_ref_design(design_data["id_bricklink"], design_data["id_rebrickable"])
                if img_ref == None :
                    img_ref = "/BrickStock/images/no_image.png"
                design_infos = f"""<span style="font-weight: bold;">Design inconnu&nbsp;→ informations issues du site Rebrickable&nbsp;:</span>
<img class="apercu" src="{img_ref}">
<span>id Lego<sup>®</sup> connus&nbsp;: {", ".join(design_data["id_lego"])}</span>
<span>id Bricklink&nbsp;: {design_data["id_bricklink"]}</span>
<span>id Rebrickable&nbsp;: {design_data["id_rebrickable"]}</span>
<span>nom (Rebrickable)&nbsp;: {design_data["nom_rebrickable"]}"""
            if p["couleur"]["statut"] == "find" :
                color_data = bdd.get_couleur_data(p["couleur"]["id_couleur"])
                color_id = color_data["id_couleur_rebrickable"]
                color_infos = f"""<span style="font-weight: bold;">Couleur connue&nbsp;:</span>
<img class="apercu couleur" src="{color_data["image_ref"]}">
<span>id couleur&nbsp;: {color_data["id_couleur"]}</span>
<span>nom&nbsp;: {color_data["nom_couleur"]}</span>
<span>transparence&nbsp;: <a>{transparence[color_data["est_transparent"]]}</span>"""
            else :
                color_id = p["couleur"]["id_rebrickable"]
                color_data = api.get_color_infos(color_id)
                img_ref = api.get_image_ref_couleur(p["couleur"]["id_rebrickable"])
                if img_ref == None :
                    img_ref = "/BrickStock/images/no_image.png"
                color_infos = f"""<span style="font-weight: bold;">Couleur inconnue&nbsp;→ informations issues du site Rebrickable&nbsp;:</span>
<img class="apercu" src="{img_ref}">
<span>nom Lego<sup>®</sup> connus&nbsp;: {", ".join(color_data["nom_lego"])}</span>
<span>id Bricklink&nbsp;: {color_data["id_bricklink"]}</span>
<span>nom Bricklink&nbsp;: {color_data["nom_bricklink"]}</span>
<span>id Rebrickable&nbsp;: {color_data["id_rebrickable"]}</span>
<span>nom Rebrickabel&nbsp;: {color_data["nom_rebrickable"]}</span>
<span>transparence&nbsp;: {transparence[color_data["est_transparent"]]}</span>"""
            resultats.append(f"""<div id="item{n}" class="item_minifig" style="cursor: pointer;"><img class="apercu" src="{api.get_rebrickable_image_ref_piece(design_data["id_rebrickable"], color_id)}"></div>""")
            liste_pieces_inconnues[n] = f"""<div class="fenetre" style="text-align: left;">
    <h3>Information de la pièce&nbsp;:</h3>
    <h5>Informations du design</h5>
    {design_infos}
    <h5 style="display: inline-block; weight: calc(100% - 16px); margin: 0 8px; border-top: 2px solid #000000">Informations de la couleur</h5>
    {color_infos}
</div>
"""
    params["{nPiecesInconnues}"] = n
    params["{listePiecesInconnues}"] = liste_pieces_inconnues
    params["{resultats}"] = resultats
    return params