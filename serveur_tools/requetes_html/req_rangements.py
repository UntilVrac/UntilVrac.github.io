from sys import path
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
path.append(BRICKSTOCK_PATH)

import serveur_tools.scripts_gestion_bdd.gestion_bdd as bdd



def get_rangements_for_id_request(id_rangement:int) :
    """
    id_rangement (int), id du rangement

    renvoie les paramètres de modifications pour le rendu de la page web (cas où l'id_rangement est donné en paramètre GET)
    """

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
    
    def __create_li_items(elements:list, n:int=1) -> str :
        """
        entrées :
            elements (list), liste des éléments (sous forme d'une liste de dictionnaire)
            n (int) (0 par défaut), niveau d'indentation

        renvoie les balises li à insérer dans une balide ul
        """
        contenu = ""
        for e in elements :
            contenu += f"""<li>
    <a href="/BrickStock/rangements?id_rangement={e["id_rangement"]}">{bdd.get_rangements_infos(e["id_rangement"])["nom_rangement"]}</a>
    <ul class="level{n}">
        {__create_li_items(e["contenu"], n + 1)}
    </ul>
</li>"""
        return contenu
    params = {"{content}" : __create_li_items(arbre_rangements["contenu"])}