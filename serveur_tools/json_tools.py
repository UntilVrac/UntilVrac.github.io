from os.path import exists

# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"

def convert_json_to_str(data:any) -> str :
    """
    data (type de base (int, float, str, tuple, list, dict ou bool) ou None), donnée à convertir
    
    renvoie les données converties en string
    """
    if data == None :
        return "null"
    assert type(data) in (int, float, str, tuple, list, dict, bool)
    if type(data) == tuple :
        data = list(data)
    if type(data) == str :
        return f'"{data}"'
    elif type(data) in (int, float) :
        return str(data)
    elif type(data) == list :
        if len(data) == 0 :
            return "[\n]"
        str_content = "["
        for e in data :
            e = convert_json_to_str(e).split("\n")
            for l in e :
                str_content += f"\n    {l}"
            str_content += ","
        return str_content[:-1] + "\n]"
    elif type(data) == dict :
        str_content = "{"
        for e in data :
            assert type(e) in (int, float, str)
            str_content += f"\n    {convert_json_to_str(e)} : "
            e_val = convert_json_to_str(data[e]).split("\n")
            i = 0
            for l in e_val :
                if i != 0 :
                    str_content += "\n    "
                str_content += l
                i += 1
            str_content += ","
        return str_content[:-1] + "\n}"
    elif type(data) == bool :
        return {True : "true", False : "false"}[data]
    
def convert_str_to_json(data:str) -> any :
    """
    data (str), données json en str

    renvoie les données json sous la forme d'objets des types de base sauf tuple (int, float, str, list, dict ou bool) ou None
    """

    def __align_left(data:str) -> str :
        """
        data (str), données à désindenter

        renvoie les données en str après suppression des indentations inutiles
        """
        n = 0
        data_bis = data.split("\n")
        temoin = data_bis[0]
        while temoin.startswith("    ") :
            temoin = temoin[4:]
            n += 1
        if n != 0 :
            data = temoin
            for l in data_bis[1:] :
                data += "\n" + l[4 * n:]
        return data
    
    data = __align_left(data)
    if data[0] == "[" :
        assert data[-1] == "]"
        list_lines = __align_left(data[2:-2]).split("\n")
        obj = []
        list_ensembles = []
        new = True
        for l in list_lines :
            if l.startswith("    ") :
                list_ensembles[-1].append(l)
                new = False
            else :
                if new :
                    list_ensembles.append([])
                else :
                    new = True
                list_ensembles[-1].append(l)
        for e in list_ensembles :
            e = "\n".join(e)
            if e[-1] == "\n" :
                e = e[:-1]
            if e[-1] == "," :
                e = e[:-1]
            obj.append(convert_str_to_json(e))
        return obj
    elif data[0] == "{" :
        assert data[-1] == "}"
        list_lines = __align_left(data[2:-2]).split("\n")
        obj = {}
        list_ensembles = []
        new = True
        for l in list_lines :
            if l.startswith("    ") :
                list_ensembles[-1].append(l)
                new = False
            else :
                if new :
                    list_ensembles.append([])
                else :
                    new = True
                list_ensembles[-1].append(l)
        for e in list_ensembles :
            e = "\n".join(e)
            if e[-1] == "\n" :
                e = e[:-1]
            if e[-1] == "," :
                e = e[:-1]
            i = e.index(":")
            key, val = e[:i - 1], e[i + 2:]
            obj[convert_str_to_json(key)] = convert_str_to_json(val)
        return obj
    else :
        if data[0] == '"' :
            assert data[-1] == '"'
            return data[1:-1]
        elif data in ("true", "false", "null") :
            return {"true" : True, "false" : False, "null" : None}[data]
        elif "." in data :
            return float(data)
        else :
            return int(data)

def save_json(json_data:any, filename:str) -> None :
    """
    entrées :
        json_data (dict), les données json à enregistrer
        filename (str), le chemin d'accès du fichier dans lequel les données seront enregistrées
    en l'absence d'extension dans le nom du fichier, l'extension utilisée sera automatiquement .json

    enregistre les données json dans le fichier spécifié (les données présentes dans ce fichier seront écrasées)
    """
    if filename[0] != "/" :
        filename = "/" + filename
    filename = BRICKSTOCK_PATH + filename
    nom = filename.split("/")[-1]
    if not ("." in nom and nom[-1] != ".") :
        filename += ".json"
    file = open(filename, "w")
    file.write(convert_json_to_str(json_data))
    file.close()

def upload_json(filename:str) -> any :
    """
    filename (str), le chemin d'accès du fichier source
    en l'absence d'extension dans le nom du fichier, l'extension utilisée sera automatiquement .json

    renvoie les données json contenu dans ce fichier
    renvoie None si le fichier n'existe pas
    """
    if filename[0] != "/" :
        filename = "/" + filename
    filename = BRICKSTOCK_PATH + filename
    nom = filename.split("/")[-1]
    if not ("." in nom and nom[-1] != ".") :
        filename += ".json"
    if exists(filename) :
        file = open(filename, "r")
        content = file.read()
        file.close()
        return convert_str_to_json(content)
    else :
        return None



if __name__ == "__main__" :
    pass
    # a = {"count" : 273, "results" : [{"id" : 0, "is_trans" : False}, {"id" : 0.1, "is_trans" : True}]}
    # b = convert_json_to_str(a)
    # print(b)
    # print()
    # c = convert_str_to_json(b)
    # print(a == c)
    # print()
    # print(c)
    print(convert_json_to_str({"1" : [], "2" : ["lknln", 55], "R" : 4}))