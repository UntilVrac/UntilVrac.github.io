from sys import path
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
path.append(BRICKSTOCK_PATH)

import serveur_tools.scripts_gestion_bdd.gestion_bdd as bdd

COULEURS = {
    "blanc" : {"hexa" : "#CBCBCB", "rgb" : (203, 203, 203)}, 
    "noir" : {"hexa" : "#1F1F1F", "rgb" : (31, 31, 31)}, 
    "gris" : {"hexa" : "#7F7F7F", "rgb" : (127, 127, 127)}, 
    "cyan" : {"hexa" : "#9CDCFF", "rgb" : (156, 220, 255)}, 
    "bleu" : {"hexa" : "#4D87B7", "rgb" : (77, 135, 183)}, 
    "turquoise" : {"hexa" : "#4DC6AD", "rgb" : (77, 198, 173)}, 
    "vert" : {"hexa" : "#628B50", "rgb" : (98, 139, 80)}, 
    "jaune" : {"hexa" : "#ECC807", "rgb" : (236, 200, 7)}, 
    "rouge" : {"hexa" : "#CA8D75", "rgb" : (202, 141, 117)}, 
    "rose" : {"hexa" : "#B179AC", "rgb" : (177, 121, 172)}
}

rangement_courant = None



# commandes :
def command_add_script(command_str:str) -> list :
    """
    command_str (str), la commande add à exécuter

    exécute la commande
    renvoie le résultat de la commande sous forme d'une liste de ligne à afficher en console
    """
    cmd = command_str.split(" ")
    if len(cmd) == 1 :
        return [f"""<span style="color: {COULEURS["cyan"]["hexa"]};">0 elements added</span>"""]
    liste_ids = cmd[1:]
    n = 0
    response = []
    for id in liste_ids :
        try :
            rep = bdd.ajouter_element_au_rangement(rangement_courant, int(id))
        except :
            response.append(f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : '{id}' is an invalid id""")
        else :
            if rep :
                n += 1
            else :
                response.append(f"""<span style="color: {COULEURS["jaune"]["hexa"]};">id '{id}' prior in a storage</span>""")
    response.append(f"""<span style="color: {COULEURS["cyan"]["hexa"]};">{n}/{len(liste_ids)} elements added</span>""")
    return response

def command_cr_script(command_str:str) -> list :
    """
    command_str (str), la commande cr à exécuter

    exécute la commande
    renvoie le résultat de la commande sous forme d'une liste de ligne à afficher en console
    """
    cmd = command_str.split(" ")
    if len(cmd) != 1 :
        return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : invalid syntax ; cr command take one argument : path</span>"""]
    path = cmd[1].split("/")
    try :
        if path[0] == "" :
            position = None
            i = 1
        else :
            position = rangement_courant
            i = 0
            while path[i] == ".." :
                position = bdd.get_rangement_parent(position)
                assert position != None
                i += 1
        for e in path[i:] :
            id = int(e)
            assert id in (i["id_rangement"] for i in bdd.get_arbre_rangements(position)["contenu"])
            position = id
    except :
        return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : no such storage</span>"""]
    else :
        rangement_courant = position
        return []
    
def command_clear_script(command_str:str) -> list :
    """
    command_str (str), la commande clear à exécuter

    exécute la commande
    renvoie le résultat de la commande sous forme d'une liste de ligne à afficher en console
    """
    if command_str == "clear" :
        return [f"""<span style="color: {COULEURS["bleu"]["hexa"]};">Do you want really clear the current storage's content ? Y/N</span>"""]
    elif command_str == "y" :
        bdd.update_rangement_content(rangement_courant, [])
        return [f"""<span style="color: {COULEURS["vert"]["hexa"]};">The current storage's content has been deleted.</span>"""]
    else :
        return [f"""<span style="color: {COULEURS["rose"]["hexa"]};">The deletion has been canceled.</span>"""]

def command_del_script(command_str:str) -> list :
    """
    command_str (str), la commande del à exécuter

    exécute la commande
    renvoie le résultat de la commande sous forme d'une liste de ligne à afficher en console
    """
    cmd = command_str.split(" ")
    if len(cmd) == 1 :
        return [f"""<span style="color: {COULEURS["cyan"]["hexa"]};">0 elements removed</span>"""]
    liste_ids = cmd[1:]
    n = 0
    response = []
    for id in liste_ids :
        try :
            bdd.supprimer_element_du_rangement(rangement_courant, int(id))
        except :
            response.append(f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : '{id}' is an invalid id""")
    response.append(f"""<span style="color: {COULEURS["cyan"]["hexa"]};">{n}/{len(liste_ids)} elements removed</span>""")
    return response

def command_find_script(command_str:str) -> list :
    """
    command_str (str), la commande find à exécuter

    exécute la commande
    renvoie le résultat de la commande sous forme d'une liste de ligne à afficher en console
    """
    cmd = command_str.split(" ")
    if len(cmd) != 1 :
        return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : invalid syntax ; find command take one argument : id_element</span>"""]
    try :
        id_rangement = bdd.get_rangement_for_element(int(cmd[1]))
    except :
        return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : invalide element_id</span>"""]
    else :
        if id_rangement == None :
            return [f"""<span style="color: {COULEURS["cyan"]["hexa"]};">null</span>"""]
        else :
            return [f"""<span style="color: {COULEURS["cyan"]["hexa"]};">{id_rangement}</span>"""]
        
def command_ls_script(command_str:str) -> list :
    """
    command_str (str), la commande ls à exécuter

    exécute la commande
    renvoie le résultat de la commande sous forme d'une liste de ligne à afficher en console
    """
    if bdd.rangement_est_compartimente(rangement_courant) :
        t_content = ""
        for e in bdd.get_arbre_rangements(rangement_courant) :
            t_content += f"""<tr>
    <td>{e["id_rangement"]}</td>
    <td>{e["nom_rangement"]}</td>
</tr>"""
        return [f"""<table class="response_ls">
    <tbody>
        <tr>
            <td>ID RANGEMENT :</td>
            <td>NOM :</td>
        </tr>
        <tr>
            <td></td>
            <td></td>
        </tr>
        {t_content}
    </tbody>
</table>"""]
    else :
        t_content = ""
        for e in bdd.get_rangement_content(rangement_courant) :
            t_content += f"""<tr>
    <td>{e[0]}</td>
    <td>{e[1]}</td>
</tr>"""
        return [f"""<table class="response_ls">
    <tbody>
        <tr>
            <td>ID ELEMENT :</td>
            <td>TYPE :</td>
        </tr>
        <tr>
            <td></td>
            <td></td>
        </tr>
        {t_content}
    </tbody>
</table>"""]