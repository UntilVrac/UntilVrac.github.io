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



def split_str_command(command_str:str) -> dict :
    """
    command_str (str), la commande à traiter

    renvoie le dictionnaire {paramètre : valeur} correspondant
    """
    if len(command_str.split(" ")) == 1 :
        return {}
    params_init = {}
    k = 1
    command_params = command_str.split(" ")[1:]
    # print(command_params)
    i = 0
    while i < len(command_params) :
        if command_params[i].startswith("-") :
            if i + 1 >= len(command_params) :
                key, val = command_params[i], ""
            else :
                key, val = command_params[i], command_params[i + 1]
            i += 1
        else :
            key, val = k, command_params[i]
            k += 1
        if val[0] in ("'", '"') and val[-1] != val[0] :
            i += 1
            continuer = True
            while continuer :
                val += " " + command_params[i]
                if command_params[i][-1] == val[0] :
                    continuer = False
                i += 1
            # print(val)
            val = val[1:-1]
        else :
            i += 1
        params_init[key] = val
    # params = {}
    # print(params_init)
    return params_init
    # for k in params_init :
    #     val = params_init[k]
    #     assert type(val) == str
    #     if val.lower() == "true" :
    #         val = True
    #     elif val.lower() == "false" :
    #         val = False
    #     else :
    #         try :
    #             val2 = val.replace(",", ".")
    #             if "." in val :
    #                 val2 = float(val)
    #             else :
    #                 val2 = int(val)
    #         except :
    #             assert val[0] in ("'", '"')
    #             assert val[-1] == val[0]
    #             val = val[1:-1]
    #         else :
    #             val = val2
    #     params[k] = val
    # return params



# commandes :
def command_add_script(command_str:str) -> list :
    """
    command_str (str), la commande add à exécuter

    exécute la commande
    renvoie le résultat de la commande sous forme d'une liste de ligne à afficher en console
    """
    if bdd.rangement_est_compartimente(rangement_courant) :
        return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : the current storage is compartimentalized</span>"""]
    # print(command_str)
    cmd = split_str_command(command_str)
    cmd = [cmd[k] for k in cmd]
    if len(cmd) == 0 :
        return [f"""<span style="color: {COULEURS["cyan"]["hexa"]};">0 element added</span>"""]
    liste_ids = cmd
    # print(liste_ids)
    n = 0
    response = []
    for id in liste_ids :
        try :
            id == int(id)
            assert bdd.piece_in_database(id) or bdd.design_in_database(id)
            rep = bdd.ajouter_element_au_rangement(rangement_courant, int(id))
        except :
            response.append(f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : '{id}' is an invalid id""")
        else :
            if rep :
                n += 1
            else :
                response.append(f"""<span style="color: {COULEURS["jaune"]["hexa"]};">id '{id}' prior in a storage</span>""")
    response.append(f"""<span style="color: {COULEURS["cyan"]["hexa"]};">{n}/{len(liste_ids)} element{"" if n <= 1 else "s"} added</span>""")
    return response
    
def command_clear_script(command_str:str) -> list :
    """
    command_str (str), la commande clear à exécuter

    exécute la commande
    renvoie le résultat de la commande sous forme d'une liste de ligne à afficher en console
    """
    if bdd.rangement_est_compartimente(rangement_courant) :
        return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : current storage is compartimentalized</span>"""]
    if command_str == "clear" :
        return [f"""<span style="color: {COULEURS["bleu"]["hexa"]};">Do you want really clear the current storage's content ? Y/N</span>"""]
    elif command_str == "Y" :
        rep = bdd.update_rangement_content(rangement_courant, [])
        if rep :
            return [f"""<span style="color: {COULEURS["vert"]["hexa"]};">The current storage's content has been deleted.</span>"""]
        else :
            return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : the deletion cannot be completed</span>"""]
    elif command_str == "N" :
        return [f"""<span style="color: {COULEURS["rose"]["hexa"]};">The deletion has been canceled.</span>"""]
    assert False

def command_cs_script(command_str:str) -> list :
    """
    command_str (str), la commande cs à exécuter

    exécute la commande
    renvoie le résultat de la commande sous forme d'une liste de ligne à afficher en console
    """
    global rangement_courant
    # cmd = command_str.split(" ")
    cmd = split_str_command(command_str)
    # cmd = [cmd[k] for k in cmd]
    if len(cmd) != 1 :
        return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : invalid syntax ; cs command takes one argument : path</span>"""]
    path = cmd[1].split("/")
    if path[-1] == "" :
        path = path[:-1]
    # print(path)
    try :
        if path[0] == "" :
            position = None
            i = 1
        else :
            position = rangement_courant
            i = 0
            continuer = True
            while continuer :
            # while path[i] == ".." :
                if i < len(path) :
                    if path[i] == ".." :
                        position = bdd.get_rangement_parent(position)
                        assert position != None
                        i += 1
                    else :
                        continuer = False
                else :
                    continuer = False
        for e in path[i:] :
            id = int(e)
            assert id in (i["id_rangement"] for i in bdd.get_arbre_rangements(position)["contenu"])
            position = id
    except :
        return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : no such storage</span>"""]
    else :
        rangement_courant = position
        return []

def command_del_script(command_str:str) -> list :
    """
    command_str (str), la commande del à exécuter

    exécute la commande
    renvoie le résultat de la commande sous forme d'une liste de ligne à afficher en console
    """
    if bdd.rangement_est_compartimente(rangement_courant) :
        return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : the current storage is compartimentalized<span>"""]
    # cmd = command_str.split(" ")
    cmd = split_str_command(command_str)
    cmd = [cmd[k] for k in cmd]
    if len(cmd) == 0 :
        return [f"""<span style="color: {COULEURS["cyan"]["hexa"]};">0 element removed</span>"""]
    liste_ids = cmd
    n = 0
    response = []
    for id in liste_ids :
        try :
            id = int(id)
            assert bdd.piece_in_database(id) or bdd.design_in_database(id)
            if not bdd.element_in_rangement(rangement_courant, id) :
                response.append(f"""<span style="color: {COULEURS["jaune"]["hexa"]};">the '{id}' element is not in storage</span>""")
            else :
                bdd.supprimer_element_du_rangement(rangement_courant, id)
            n += 1
        except :
            response.append(f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : '{id}' is an invalid id<span>""")
    response.append(f"""<span style="color: {COULEURS["cyan"]["hexa"]};">{n}/{len(liste_ids)} element{"" if n <= 1 else "s"} removed</span>""")
    return response

def command_find_script(command_str:str) -> list :
    """
    command_str (str), la commande find à exécuter

    exécute la commande
    renvoie le résultat de la commande sous forme d'une liste de ligne à afficher en console
    """
    # cmd = command_str.split(" ")
    cmd = split_str_command(command_str)
    cmd = [cmd[k] for k in cmd]
    if len(cmd) != 1 :
        return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : invalid syntax ; find command takes one argument : id_element</span>"""]
    try :
        id_rangement = bdd.get_rangement_for_element(int(cmd[0]))
    except :
        return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : invalide element_id</span>"""]
    else :
        if id_rangement == None :
            return [f"""<span style="color: {COULEURS["cyan"]["hexa"]};">no storage for this element</span>"""]
        else :
            global rangement_courant
            position = rangement_courant
            rangement_courant = id_rangement
            r = execute_command("pws")
            rangement_courant = position
            return r
            # return [f"""<span style="color: {COULEURS["cyan"]["hexa"]};">{id_rangement}</span>"""]
        
def command_ls_script(command_str:str) -> list :
    """
    command_str (str), la commande ls à exécuter

    exécute la commande
    renvoie le résultat de la commande sous forme d'une liste de ligne à afficher en console
    """
    if bdd.rangement_est_compartimente(rangement_courant) :
        # print(True)
        t_content = ""
        content = bdd.get_arbre_rangements(rangement_courant)["contenu"]
        if len(content) == 0 :
            return [f"""<span style="color: {COULEURS["cyan"]["hexa"]};">storage is empty</span>"""]
        for e in content :
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
        # print(False)
        t_content = ""
        content = bdd.get_rangement_content(rangement_courant)
        if len(content) == 0 :
            return [f"""<span style="color: {COULEURS["cyan"]["hexa"]};">storage is empty</span>"""]
        for e in content :
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

def command_mkran_script(command_str:str) -> list :
    """
    command_str (str), la commande mkran à exécuter

    exécute la commande
    renvoie le résultat de la commande sous forme d'une liste de ligne à afficher en console
    """
    if not bdd.rangement_est_compartimente(rangement_courant) :
        return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : the current storage is not compartmentalized"""]
    elif bdd.count_compartiments_in_rangement(rangement_courant) == bdd.get_rangements_infos(rangement_courant)["nb_compartiments"] :
        return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : there are no compartment available in the current storage</span>"""]
    # cmd = command_str.split(" ")
    cmd = split_str_command(command_str)
    if not(1 in cmd and 2 in cmd) :
        return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : mkran command takes at least two arguments : storage_name and storage_type</span>"""]
    print(cmd)
    for k in cmd :
        if k not in (1, 2, "-n", "-c") :
            return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : mkran command takes at most four arguments : storage_name and storage_type (required) and compartments_number (preceded by '-n') and compartmentalization (preceded by '-c')</span>"""]
    nb_compartiments, compartimentation = 1, "1 x 1"
    response = []
    if "-n" in cmd :
        try :
            nb_compartiments = int(cmd["-n"])
            assert nb_compartiments >= 1
        except :
            return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : invalid value for '-n' argument</span>"""]
        if not "-c" in cmd :
            compartimentation = f"1 x {nb_compartiments}"
    if "-c" in cmd :
        try :
            c = cmd["-c"].lower()
            c = c.split(" x ")
            c = [int(e) for e in c]
            n = 1
            for e in c :
                assert e > 0
                n *= e
        except :
            return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : invalid value for '-c' argument</span>"""]
        else :
            if "-n" in cmd :
                if n != nb_compartiments :
                    compartimentation = f"1 x {nb_compartiments}"
                    response.append(f"""<span style="color: {COULEURS["jaune"]["hexa"]};">'-c' argument's value has been replaced by '{compartimentation}' to correspond with the '-n' argument value</span>""")
                else :
                    compartimentation = cmd["-c"]
            else :
                compartimentation = cmd["-c"]
                nb_compartiments = n
    bdd.ajouter_rangement(cmd[1], cmd[2], nb_compartiments, compartimentation, rangement_courant)
    response.append(f"""<span style="color: {COULEURS["cyan"]["hexa"]};">storage created</span>""")
    return response

def command_mv_script(command_str:str) -> list :
    """
    command_str (str), la commande mv à exécuter

    exécute la commande
    renvoie le résultat de la commande sous forme d'une liste de ligne à afficher en console
    """
    cmd = split_str_command(command_str)
    global rangement_courant
    current = rangement_courant
    for e in cmd :
        if e not in (1, 2, "-c") :
            return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : mv command doesn't take '{e}' argument</span>"""]
    if 1 not in cmd :
        return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : mv command takes at least one argument : new_path</span>"""]
    if 2 in cmd :
        path1, path2 = cmd[1], cmd[2]
    else :
        path1, path2 = "/".join([""] + [e["id_rangement"] for e in bdd.get_rangement_path(current)]), cmd[1]
    rep1 = command_cs_script(f"cr {path1}")
    if rep1 != [] :
        return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : invalid origin path</span>"""]
    rangement_courant = current
    rep2 = command_cs_script(f"cr {path2}")
    rangement_courant = current
    id1, id2 = int(path1.split("/")[-1]), int(path2.split("/")[-1])
    if rep2 != [] :
        return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : invalid destination path</span>"""]
    if "-c" in cmd :
        if bdd.rangement_est_compartimente(id2) :
            return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : destination path corresponds to a compartmentalized storage</span>"""]
        for id in bdd.get_rangement_content(id1) :
            pass
        rep1 = bdd.update_rangement_content(id2, [e[0] for e in bdd.get_rangement_content(id1)])
        if not rep1 :
            return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : move couldn't be performed</span>"""]
        bdd.update_rangement_content(id1, [])
        return [f"""<span style="color: {COULEURS["cyan"]["hexa"]};">storage content moved</span>"""]
    else :
        if not bdd.rangement_est_compartimente(id2) :
            return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : destination path doesn't correspond to a compartmentalized storage</span>"""]
        bdd.change_parent_rangement(id1, id2)
        return [f"""<span style="color: {COULEURS["cyan"]["hexa"]};">storage moved</span>"""]
    
def command_pws_script(command_str:str) -> list :
    """
    command_str (str), la commande pws à exécuter

    exécute la commande
    renvoie le résultat de la commande sous forme d'une liste de ligne à afficher en console
    """
    if rangement_courant in (0, None) :
        return [f"""<span style="color: {COULEURS["cyan"]["hexa"]};">/</span>"""]
    else :
        path = "/".join([str(e["id_rangement"]) for e in bdd.get_rangement_path(rangement_courant)])
        return [f"""<span style="color: {COULEURS["cyan"]["hexa"]};">{path}</span>"""]

def command_rmran_script(command_str:str) -> list :
    """
    command_str (str), la commande rmran à exécuter

    exécute la commande
    renvoie le résultat de la commande sous forme d'une liste de ligne à afficher en console
    """

    def nb_enfants(id_rangement:int) -> int :
        """
        id_rangement (int), l'id du rangement

        renvoie le nombre total de sous-rangements qu'il contient
        """
        arbre = bdd.get_arbre_rangements(id_rangement)
        n = 0
        for e in arbre["contenu"] :
            n += 1
            n += nb_enfants(e["id_rangement"])
        return n

    if command_str.startswith("rmran ") :
        cmd = split_str_command(command_str)
        if 1 not in cmd :
            return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : rmran command take one argument : storage_path</span>"""]
        else :
            current = rangement_courant
            try :
                rep = command_cr_script(f"cr {cmd[1]}")
                rangement_courant = current
                if rep == [] :
                    nb = nb_enfants(int(cmd[1].split("/")[-1]))
                    return [f"""<span style="color: {COULEURS["bleu"]["hexa"]};">Do you want really remove the storage whose id is '{cmd[1]}' ? This operation will result the deletion of {str(nb) + " other storage" if nb <= 1 else str(nb) + " other storages"}. Y/N</span>"""]
                else :
                    return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : invalid path</span>"""]
            except :
                rangement_courant = current
                return [f"""<span style="color: {COULEURS["rouge"]["hexa"]};">ERROR : invalid argument value</span>"""]
    elif command_str.startswith("Y ") :
        cmd = split_str_command(command_str)
        bdd.supprimer_rangement(int(cmd[1]))
        return [f"""<span style="color: {COULEURS["vert"]["hexa"]};">The storage has been deleted.</span>"""]
    else :
        return [f"""<span style="color: {COULEURS["rose"]["hexa"]};">The deletion has been canceled.</span>"""]
    
def command_tree_script(command_str:str) -> list :
    """
    command_str (str), la commande tree à exécuter

    exécute la commande
    renvoie le résultat de la commande sous forme d'une liste de ligne à afficher en console
    """

    def parcours(id_rangement:int) -> list :
        """
        id_rangement (int), l'id du rangement racine du parcours

        renvoie le résultat du parcours sous forme d'une liste de ligne à afficher en console
        """
        response = []
        arbre = bdd.get_arbre_rangements(id_rangement)
        # print(arbre)
        response.append(f"""{arbre["id_rangement"]} - {arbre["nom_rangement"]}""")
        for id in arbre["contenu"] :
            for e in parcours(id["id_rangement"]) :
                response.append("    " + e)
        return response
    
    return [f"""<span style="color: {COULEURS["cyan"]["hexa"]};">{e}</span>""" for e in parcours(rangement_courant)]



COMMANDS_FUNCTIONS = {
    "add" : command_add_script, # validé 1/2
    "clear" : command_clear_script, # validé
    "cs" : command_cs_script, # validé
    "del" : command_del_script, # validé
    "find" : command_find_script, # validé
    "ls" : command_ls_script, # validé
    "mkran" : command_mkran_script, # validé
    "mv" : command_mv_script, 
    "pws" : command_pws_script, # validé
    "rmran" : command_rmran_script, 
    "tree" : command_tree_script
}
COMMANDS_WITH_CONFIRMATION = ["clear", "rmran"]

HISTORIQUE_COMMANDES = []

def execute_command(command_str:str) -> list :
    """
    command_str (str), la commande clear à exécuter

    exécute la commande
    renvoie le résultat de la commande sous forme d'une liste de ligne à afficher en console
    """
    if command_str.replace(" ", "") == "" :
        return [f"""<span style="color: {COULEURS["blanc"]["hexa"]};">>>> {command_str}</span>"""]
    print(command_str)
    if command_str.upper() in ("Y", "N") :
        command_str = command_str.upper()
        print(True)
        last_command = HISTORIQUE_COMMANDES[-1]
        cmd_name = last_command.split(" ")[0]
        if cmd_name in COMMANDS_WITH_CONFIRMATION :
            print(None)
            if len(last_command.split(" ")) > 1 :
                cmd = command_str + " " + " ".join(last_command.split(" ")[1:])
            else :
                cmd = command_str
            # print(cmd)
            return [f"""<span style="color: {COULEURS["blanc"]["hexa"]};">>>> {command_str}</span>"""] + COMMANDS_FUNCTIONS[cmd_name](cmd)
        else :
            return [f"""<span style="color: {COULEURS["blanc"]["hexa"]};">>>> {command_str}</span>""", f"""<span style="color: {COULEURS["rouge"]["hexa"]};">{cmd_name} : command not found</span>"""]
    else :
        HISTORIQUE_COMMANDES.append(command_str)
    cmd_name = command_str.split(" ")[0]
    if cmd_name in COMMANDS_FUNCTIONS :
        return [f"""<span style="color: {COULEURS["blanc"]["hexa"]};">>>> {command_str}</span>"""] + COMMANDS_FUNCTIONS[cmd_name](command_str)
    else :
        return [f"""<span style="color: {COULEURS["blanc"]["hexa"]};">>>> {command_str}</span>""", f"""<span style="color: {COULEURS["rouge"]["hexa"]};">{cmd_name} : command not found</span>"""]



if __name__ == "__main__" :
    pass
    # print(split_str_command("mkran 'Boite 1' 'petite boite' -n 2 -c '1 x 2'"))
    # print(command_rmran_script(""))
    # a = command_tree_script("")
    # for e in a :
    #     print(e)

    rangement_courant = 73

    cmd = """
mc ../../74
mv ../../72 -c
"""

    """
add 3005 300501
"""

    def write(rep:list) -> None :
        for e in rep :
            print(e)

    for e in cmd.split("\n") :
        if e != "" :
            write(execute_command(e))