from sys import path
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
path.append(BRICKSTOCK_PATH)

import serveur_tools.scripts_gestion_bdd.gestion_bdd as bdd



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

def get_rangement_content_request(id_rangement:int) -> dict :
    """
    id_rangement (int), id du rangement

    renvoie les paramètres de modifications pour le rendu de la page web (cas un id_piece est donné en paramètre GET)
    """
    params = {}
    liste_content = bdd.get_rangement_content(id_rangement)
    content = ""
    for e in liste_content :
        if e[1] == "pièce" :
            content += f""""""
        else :
            pass
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
        contenu += f"""<ul class="level level0">
    <li>
        <a href="/BrickStock/rangements?id_rangement={e["id_rangement"]}">{bdd.get_rangements_infos(e["id_rangement"])["nom_rangement"]}</a>
    </li>
</ul>"""
    params = {"{content}" : contenu, "{script}" : ""}
    return params