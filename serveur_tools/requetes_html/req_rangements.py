from sys import path
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
path.append(BRICKSTOCK_PATH)

import serveur_tools.scripts_gestion_bdd.gestion_bdd as bdd



def get_rangements_for_id_request(id_rangement:int) :
    """
    id_rangement (int), id du rangement

    renvoie les paramètres de modifications pour le rendu de la page web (cas où l'id_rangement est donné en paramètre GET)
    """
    arbre_rangements = bdd.get_arbre_rangements()
    infos = bdd.get_rangements_infos(id_rangement)
    path = bdd.get_rangement_path(id_rangement)
    path.append(infos)
    li_content = ""
    for e in arbre_rangements["contenu"] :
        li_content += f"""<li>
    <a href="/BrickStock/rangements?id_rangement={e["id_rangement"]}">{bdd.get_rangements_infos(e["id_rangement"])["nom_rangement"]}</a>
</li>"""
    contenu = f"""<span>{" > ".join([f'''<a href="/BrickStock/rangements?id_rangement={e["id_rangement"]}">{e["nom_rangement"]}</a>''' for e in path])}</span><ul class="level level{len(bdd.get_rangement_path(id_rangement)) + 1}">
    {li_content}
</ul>"""
    params = {"{content}" : contenu, "{script}" : ""}
    return params

def get_rangements_for_piece_request(id_piece:int) :
    """
    id_piece (int), id de la pièce dont on doit récupérer le rangement

    renvoie les paramètres de modifications pour le rendu de la page web (cas un id_piece est donné en paramètre GET)
    """

def get_rangements_list_request() :
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