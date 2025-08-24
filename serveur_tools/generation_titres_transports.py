import fpdf
import requests
# from bs4 import BeautifulSoup
# from decomposition_html import construct_html_arb
from urllib.parse import quote
from gestion_bdd import creer_nouveau_titre_transport
from sqlite3 import Connection

DIMENSIONS_CARTE = (85, 54)
POSITION_CODE_BARRE = {"billet_uni_lfsgp" : (5.5, 23.4), "billet_uni_lfsgp+" : (5.5, 23.4), "billet_10" : (5.5, 23.4), "pass_10" : (5.5, 19.5), "pass_uni" : (5.5, 19.5)}

KEY = "baccacbacbaaacccabababbcbaabbcbc"
# a, b, c = 0, 0, 0
# for car in KEY :
#     if car == "a" :
#         a += 1
#     elif car == "b" :
#         b += 1
#     else :
#         c += 1
# print(a, b, c, a + b + c)

# KEY = "abaccacbacbaaacccabaababbcbaabbacbcbabbcabcaabaaabccabacabcbbcccccaaabbbcbccaccbcaacbaabbbbcccacabcabcabcbcbcbbbacaccacaabaacbcb"

# key = ""
# from random import randint
# for i in range(8) :
#     part = ""
#     for i in range(16) :
#         part += "abc"[randint(0, 2)]
#     key += part
# print(key, key.count("a"), key.count("b"), key.count("c"))

def deci_to_hexa(deci_num:int) -> str :
    if deci_num < 16 :
        return str(deci_num) if deci_num < 10 else {10 : "A", 11 : "B", 12 : "C", 13 : "D", 14 : "E", 15 : "F"}[deci_num]
    else :
        return deci_to_hexa(deci_num // 16) + deci_to_hexa(deci_num % 16)
    
def hexa_to_deci(hexa_num:str) -> int :
    n = len(hexa_num) - 1
    deci_num = 0
    for car in hexa_num :
        deci_num += 16**n * (int(car) if car in "0123456789" else {"A" : 10, "B" : 11, "C" : 12, "D" : 13, "E" : 14, "F" : 15}[car])
        n -= 1
    return deci_num

def encrypt_barcode_id(id_source:int) -> str :
    id_str = str(id_source)
    while len(id_str) < 12 :
        id_str = "0" + id_str
    fx = lambda e : "0" * (8 - len(e)) + e
    id_hexa = {"a" : fx(deci_to_hexa(int(id_str[:4]))), "b" : fx(deci_to_hexa(int(id_str[4:8]))), "c" : fx(deci_to_hexa(int(id_str[8:])))}
    id_output = ""
    for car in KEY :
        id_output += id_hexa[car]
    return id_output

def decrypt_barcode_id(id_source:str) -> int :
    assert len(id_source) == 128 * 8
    a, b, c = None, None, None
    # for i in range(128) :
    for i in range(32) :
        if KEY[i] == "a" :
            if a == None :
                a = id_source[i * 8:(i + 1) * 8]
            else :
                assert id_source[i * 8:(i + 1) * 8] == a
        elif KEY[i] == "b" :
            if b == None :
                b = id_source[i * 8:(i + 1) * 8]
            else :
                assert id_source[i * 8:(i + 1) * 8] == b
        elif KEY[i] == "c" :
            if c == None :
                c = id_source[i * 8:(i + 1) * 8]
            else :
                assert id_source[i * 8:(i + 1) * 8] == c
    fx = lambda e : "0" * (4 - len(e)) + e
    a, b, c = fx(str(hexa_to_deci(a))), fx(str(hexa_to_deci(b))), fx(str(hexa_to_deci(c)))
    return int(a + b + c)

def create_code_barre(barcode_type:str, id_content:int) :
    content = "/www.acg-transport.fr/titres_transport?id=" + encrypt_barcode_id(id_content)
    url = f"https://barcode.tec-it.com/barcode.ashx?data={quote(content)}&code={barcode_type}&dpi=96&imagetype=Png"
    # print(url)
    response = requests.get(url)
    if response.status_code == 200 :
        # print(response.content)
        path = f"images/titres de transport/code-barres/{id_content}.png"
        # path = content + ".png"
        file = open(path, "w+b")
        file.write(response.content)
        file.close()
        return path
        # return response.content
    print(response.status_code, response.content)
    assert False
    return ""

def create_titre_transport_pdf(titre_id:str) -> str :
    connexion, id_titre = creer_nouveau_titre_transport(titre_id)
    assert type(connexion) == Connection
    try :
        # code_barre = create_code_barre("DataMatrix", id_titre)
        code_barre = create_code_barre("Aztec", id_titre)
    except :
        return None
    pdf = fpdf.FPDF(format=DIMENSIONS_CARTE)
    # pdf.set_font("arial rounded MT bold", size=10)
    pdf.add_page()
    pdf.image(f"images/titres de transport/{titre_id}-1.png", 0, 0, DIMENSIONS_CARTE[0], DIMENSIONS_CARTE[1])
    pdf.add_page()
    pdf.image(f"images/titres de transport/{titre_id}-2.png", 0, 0, DIMENSIONS_CARTE[0], DIMENSIONS_CARTE[1])
    pdf.image(code_barre, POSITION_CODE_BARRE[titre_id][0], POSITION_CODE_BARRE[titre_id][1], 15, 15)
    path = f"images/titres de transport/cartes/{titre_id}-{id_titre}.pdf"
    pdf.output(path)
    connexion.commit()
    connexion.close()
    return path



if __name__ == "__main__" :
    create_titre_transport_pdf("pass_10")
    assert decrypt_barcode_id(encrypt_barcode_id(200000000000)) == 200000000000