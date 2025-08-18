class Node :
    """
    implémentation d'un noeud html
    attributs :
        - __nodeType (str) : type du noeux (span, div, p, a, img, ...)
        - params (dict) : paramètre du noeud (class, style, ...)
        - __children (list) : liste des noeuds ou string enfant
    méthodes :
        - __init__(self, nodeType:str, params:dict) -> None : constructeur de la classe Node
        - appendChild(self, node:Node|str) -> None : ajoute un enfant (classe Node ou String) à la liste __children
        - getChildren(self) -> list : renvoie la liste __children
        - getChildByType(self, nodeType:str) -> list : renvoie la liste des enfants du noeud dont le nodeType est spécifié
        - __str__(self) -> str : renvoie la chaine de caractère correspondant au code html indenté
        - __repr__(self) -> str : renvoie self.__str__() pour l'affichage en console
    """

    def __init__(self, nodeType:str, params:dict) :
        """
        constructeur de la classe Node
        """
        assert type(nodeType) == str
        assert type(params) == dict
        self.__nodeType = nodeType
        self.params = params
        self.__children = []
    
    def appendChild(self, node) -> None :
        """
        mutateur de l'attribut __children
        entrée : node (Node ou str)
        ajoute un enfant (classe Node ou String) à la liste __children
        """
        assert type(node) in (Node, str)
        self.__children.append(node)
    
    def getChildren(self) -> list :
        """
        assesseur de l'attribut __children
        renvoie la liste __children
        """
        return self.__children
    
    def getChildByType(self, nodeType:str) -> list :
        """
        assesseur de l'attribut __children
        entrée : nodeType (str) (pour récupérer les objets de type str (textNode), nodeType doit avoir pour valeur "str" ou "textNode")
        renvoie la liste des enfants du noeud dont le nodeType est spécifié
        """
        if nodeType in ("textNode", "str") :
            return [e for e in self.__children if type(e) == str]
        else :
            return [e for e in [n for n in self.__children if type(n) == Node] if e.__nodeType == nodeType]
    
    def __str__(self) -> str :
        """
        renvoie la chaine de caractère correspondant au code html indenté
        """
        chaine = f"<{self.__nodeType}"
        for p in self.params :
            chaine += f' {p}="{self.params[p]}"'
        chaine += ">"
        if self.__nodeType not in ("img", "br", "br/", "input") :
            if (len(self.__children)) > 0 :
                chaine += "\n"
                for n in self.__children :
                    for e in str(n).split("\n") :
                        chaine += "    " + e + "\n"
            chaine += f"</{self.__nodeType}>"
        return chaine
    
    def __repr__(self) -> str :
        """
        renvoie self.__str__() pour l'affichage en console
        """
        return self.__str__()     
    


def console_log(a:any="", b:any="", c:any="", d:any="", __name=__name__) -> None :
    """
    entrées :
        a, b, c et d, les éléments à écrire en console (par défaut "")
        __name, l'attribut __name__ du module exécutant la fonction (par défaut du module dans lequel elle est définie)
    si le fichier est exécuté comme fichier principal (__name__ == "__main__"), écrit en console les éléments a, b, c et d au moyen d'un print(a, b, c, d)
    sinon l'écriture en console n'est pas effectuée
    """
    if __name == "__main__" :
        print(a, b, c, d)

def get_params(node_header:str) -> dict :
    """
    node_header (str) : la partie paramétrique de la balise html ouvrante
    renvoie ces paramètres sous la forme d'un dictionnaire
    """
    if node_header == "" :
        return {}
    params = {}
    node_header = node_header.split(" ")
    i = 0
    l = len(node_header)
    assert "=" in node_header[i]
    n = 0
    while i < l :
        j = i
        p_n, p_c = node_header[i].split("=")
        while j < l - 1 and "=" not in node_header[j + 1] :
            p_c += " " + node_header[j]
            j += 1
            n += 1
        params[p_n] = p_c[1:-1]
        i = j + 1
    return params

def construct_html_arb(html_brut:str, rec_n:int=0) -> list :
    """
    entrées :
        html_brut (str), le code html brut
        rec_n (int), le numéro d'appel récursif (permettant au développeur de suivre les appels récursifs en console)
    renvoie une liste d'éléments de type Node ou String correspondant à l'implémentation du code html brut par la classe Node
    """
    liste_content = []
    continuer = True
    n = 0
    while continuer and len(html_brut) > 0 and n < 100 :
        console_log(rec_n, 1, "\n", html_brut)
        if html_brut[0] == "<" :
            i = html_brut.index(">") + 1
            balise_brut = html_brut[0:i]
            balise_type = balise_brut[1:-1].split(" ")[0]
            if balise_type[0] == "/" :
                console_log(rec_n, 2.1)
                continuer = False
                console_log(rec_n, 2.2, balise_brut)
            else :
                balise_params = get_params(balise_brut[len(balise_type) + 2:-1])
                if balise_type in ("img", "br", "br/", "input") :
                    console_log(rec_n, 3.1)
                    balise = Node(balise_type, balise_params)
                    console_log(rec_n, 3.2, balise)
                    liste_content.append(balise)
                else :
                    console_log(rec_n, 3.3)
                    balise = Node(balise_type, balise_params)
                    console_log(rec_n, 3.4, balise)
                    rec = construct_html_arb(html_brut[len(balise_brut):], rec_n=rec_n + 1)
                    if type(rec) == tuple :
                        rec, html_brut = rec
                    else :
                        html_brut = ""
                    console_log(rec_n, 3.5, html_brut)
                    i = 0
                    for node in rec :
                        balise.appendChild(node)
                    console_log(rec_n, 3.6, balise)
                    liste_content.append(balise)
        else :
            console_log(rec_n, 4.1)
            i = html_brut.index("<")
            console_log(rec_n, 4.2, html_brut[0:i])
            liste_content.append(html_brut[0:i])
        console_log(rec_n, 5, "i =", i)
        html_brut = html_brut[i:]
        n += 1
        console_log(rec_n, 6, continuer)
    if len(html_brut) == 0 :
        console_log(rec_n, 7)
        return liste_content
    else :
        console_log(rec_n, 8)
        return (liste_content, html_brut)
    


if __name__ == "__main__" :
    html_brut = """<div class="page"><div class="menu"><ul><li><a href="/BrickStock/pieces">Pièces</a></li><li><a href="/BrickStock/designs">Designs</a></li><li><a href="/BrickStock/categories">Categories</a></li><li><a href="/BrickStock/couleurs">Couleurs</a></li><li class="main"><a href="/BrickStock/sets">Sets</a></li><li><a href="/BrickStock/minifigures">Minifigures</a></li></ul></div><div class="layout"><a class="page_precedente" href="{page_precedente}">&lt; <span>Retour</span></a><div style="text-align: center;"><h3 style="text-align: center;">{nom_set}</h3><a style="display: inline-block; position: relative; vertical-align: top;" href="{image_ref_set}" target="_blank"><img class="item_img" style="margin-left: 12px; width: 200px;" src="{image_ref_set}"></a><div class="infos_set"><span id="item_id_set">id du set&nbsp;: {id_set}</span><br/><span>gamme&nbsp;: {gamme_set}</span><br/><span id="item_annee">année&nbsp;: {annee_set}</span></div></div><div style="text-align: left; padding: 24px;" id="list_minifig_in_set">{list_minifig_in_set}</div><form method="POST" style="margin: 0 24px 24px; text-align: center; width: calc(100% - 48px);"><input type="hidden" name="form_name" value="save_data"><input type="hidden" name="id_set" value="{id_set}"><input type="hidden" name="liste_minifigs" id="liste_minifigs_input"><input type="submit" value="ENREGISTRER" class="bouton_validation_infos enregistrer" style="border-radius: 4px; width: 140px;"></form><div style="text-align: left; margin: 0 24px; padding: 24px 0; border-top: 1px solid #404040;" id="search_zone"><div class="filter_zone"><a class="bouton_refresh" href="" id="boutonRefresh"></a><h3>Filtres&nbsp;:</h3><form method="POST" id="form_search" action="http://localhost:1520/BrickStock/{current_url}#search_zone"><input type="hidden" name="form_name" value="search_minifig"><input type="hidden" name="liste_minifigs" id="liste_minifigs_input_search"><span>Nom&nbsp;:</span><br/><input type="text" name="nom" value="{nom_search}" placeholder="saisissez un nom" id="filter1"><img src="http://localhost:1520/BrickStock/images/del_filter.svg" class="del_filter hide" id="del1"><separator></separator><span>id de la minifig&nbsp;:</span><br/><input type="text" name="id_minifig" value="{id_minifig_search}" placeholder="saisissez un nom" id="filter4"><img src="http://localhost:1520/BrickStock/images/del_filter.svg" class="del_filter hide" id="del4"><separator></separator><span>Gamme&nbsp;:</span><br/><select name="gamme" value="{gamme_search}" id="filter2"><option value="0">--sélectionner une gamme--</option>{liste_gammes}</select><img src="http://localhost:1520/BrickStock/images/del_filter.svg" class="del_filter hide" id="del2"><separator></separator><span>Set&nbsp;:</span><br/><input type="text" name="id_set" value="{id_set_search}" placeholder="saisissez un id de set" id="filter3"><img src="http://localhost:1520/BrickStock/images/del_filter.svg" class="del_filter hide" id="del3"><separator></separator><input type="submit" value="Rechercher" class="rechercher"></form></div><div class="table_zone">{cases}</div></div></div></div>"""
    html_node = construct_html_arb(html_brut)[0]
    print()
    print()
    print()
    print(html_node)