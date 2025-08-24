from os import listdir
import sqlite3
from serveur_tools.qr_code import create_qr_code
from time import sleep
from tqdm import tqdm

BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
BRICKSTOCK_SITE_HREF = "http://localhost:1520"
# BRICKSTOCK_PATH = "/workspaces/UntilVrac.github.io"
# BRICKSTOCK_SITE_HREF = "https://untilvrac.github.io"

def set_brickstock_path(current_path:str, n:int=0) -> tuple :
    # for f in listdir(current_path) :
    #     if f != "SET_BRICKSTOCK_PATH.py" :
    #         path = current_path + "/" + f
    #         if f.split(".")[-1] == "py" :
    #             file = open(path, "r")
    #             content = file.read()
    #             file.close()
    #             save = False
    #             if "BRICKSTOCK_PATH = " in content :
    #                 content = content.split("\n")
    #                 content_bis = []
    #                 for e in content :
    #                     if e.startswith("BRICKSTOCK_PATH = ") :
    #                         e = f'BRICKSTOCK_PATH = "{BRICKSTOCK_PATH}"'
    #                     content_bis.append(e)
    #                 content = content_bis
    #                 save = True
    #             if "BRICKSTOCK_SITE_HREF = " in content :
    #                 content = content.split("\n")
    #                 content_bis = []
    #                 for e in content :
    #                     if e.startswith("BRICKSTOCK_SITE_HREF = ") :
    #                         e = f'BRICKSTOCK_SITE_HREF = "{BRICKSTOCK_SITE_HREF}"'
    #                     content_bis.append(e)
    #                 content = content_bis
    #                 save = True
    #             if save :
    #                 file = open(path, "w")
    #                 file.write("\n".join(content))
    #                 file.close()
    #                 n += 1
    #         elif "." not in f :
    #             set_brickstock_path(path, n, a, b)
    # print("creation qr-codes")
    connexion = sqlite3.connect(BRICKSTOCK_PATH + "/databases/My Own Collection.db")
    curseur = connexion.cursor()
    curseur.execute('''SELECT id_rangement FROM Rangements_physiques;''')
    r = []
    for e in curseur :
        r.append(e[0])
    connexion.close()
    a, b, l = 0, 0, []
    for id in tqdm(r) :
        resp = create_qr_code(id)
        if resp :
            a += 1
        else :
            l.append(id)
        b += 1
        sleep(2)
    return (n, a, b, l)

if __name__ == "__main__" :
    n, a, b, l = set_brickstock_path(BRICKSTOCK_PATH)
    print(f"end :    {n} files affected ; {a} / {b} QR-Code created :")
    for id in l :
        print(f"    QR-Code {id}")