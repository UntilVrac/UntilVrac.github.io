import requests
import sqlite3

def get_input() :
    i = input("id rebrickable : ")
    if i == "save&end" :
        print()
        print("interruption volontaire")
        print("données enregistrées")
        print()
        assert False
    elif i == "" :
        i = None
    else :
        if not i.startswith("fig-") :
            i = "fig-" + i
    return i


def get_id_used() :
    ids = []
    file = open("table_minifigures2.csv", "r")
    content = file.read().split("\n")[1:]
    file.close()
    for l in content :
        ids.append(l.split(",")[1])
    return ids

id_used = get_id_used()


def get_url_minifigs(id_fig:str) :
    print()
    print(id_fig)
    connexion = sqlite3.connect("../BrickStock database.db")
    curseur = connexion.cursor()
    curseur.execute('''SELECT nom, image_ref FROM Minifigures WHERE id_minifig = ?;''', (id_fig,))
    r = []
    for e in curseur :
        r.append(e)
    r = r[0]
    print(r[0])
    print("image :", r[1])
    curseur.execute('''SELECT id_set FROM minifig_dans_set WHERE id_minifig = ?;''', (id_fig,))
    r = []
    for e in curseur :
        r.append(int(e[0]))
    connexion.close()
    if len(r) == 0 :
        print(None, 1)
        return get_input()
    print(True, 1)
    print(r)
    ids = {}
    for s in r :
        url = f"https://rebrickable.com/api/v3/lego/sets/{s}-1/minifigs/?key=dc2a2f4a231edbf3742b0ebf56fbc172"
        print(url)
        response = requests.get(url)
        if response.status_code == 200 :
            rep_json = response.json()
            for item in rep_json["results"] :
                id = item["set_num"]
                if id in ids :
                    ids[id] += 1
                else :
                    ids[id] = 1
        else :
            print(response.status_code)
            return get_input()
    r_bis = []
    for f in ids :
        if ids[f] == len(r) and f not in id_used :
            r_bis.append(f)
    if len(r_bis) == 0 :
        print(None, 2)
        return get_input()
    elif len(r_bis) == 1 :
        print(True, 2)
        print(r_bis[0])
        return r_bis[0]
    else :
        print(r_bis)
        return get_input()
            

file = open("table_minifigures.csv", "r")
content = file.read().split("\n")
file.close()

def write_content(lines:list) :
    file = open("table_minifigures.csv", "w")
    content = ""
    for l in lines :
        content += l + "\n"
    content = content[:-1]
    file.write(content)
    file.close()

new_content = ""
lines = list(content)
try :
    for l in content :
        line = l.split(",")
        fig_id = get_url_minifigs(line[0])
        if fig_id != None :
            id_used.append(fig_id)
        new_content += f"\n{line[0]},{fig_id}"
        for e in line[1:] :
            new_content += "," + e
        # print(l, lines[0])
        assert lines[0] == l
        lines.pop(0)
except :
    print()
    print("erreur")
    print()
write_content(lines)
file = open("table_minifigures2.csv", "a")
file.write(new_content)
file.close()