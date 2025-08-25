import requests
from urllib.parse import quote
from sys import path
import fpdf
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
BRICKSTOCK_SITE_HREF = "http://localhost:1520"
path.append(BRICKSTOCK_PATH)

import scripts_gestion_bdd.gestion_bdd as bdd

FORMATS_STANDARDS = {
    "3,5 x 5" : (89, 127), 
    "3,5 x 5 sans bordure" : (89, 127), 
    "4 x 6" : (102, 152), 
    "4 x 6 sans bordure" : (102, 152), 
    "5 x 7" : (127, 178), 
    "5 x 7 sans bordure" : (127, 178), 
    "8 x 10" : (203, 254), 
    "8 x 10 sans bordure" : (203, 254), 
    "A1" : (594, 840), 
    "A1 sans bordure" : (594, 840), 
    "A2" : (420, 594), 
    "A2 sans bordure" : (420, 594), 
    "A3" : (297, 420), 
    "A3 sans bordure" : (297, 420), 
    "A4" : (210, 297), 
    "A4 sans bordure" : (210, 297), 
    "A5" : (148.5, 210), 
    "Carte postale" : (100, 148), 
    "Carte postale sans bordure" : (100, 148), 
    "Enveloppe DL" : (110, 220), 
    "Enveloppe n°10" : (105, 241), 
    "JIS B5" : (182, 257), 
    "Lettre US" : (216, 279), 
    "Lettre US sans bordure" : (216, 279), 
    "Légal US" : (216, 356)
}

MARGES = {
    "3,5 x 5" : (2, 2), 
    "3,5 x 5 sans bordure" : (0, 0), 
    "4 x 6" : (3, 3), 
    "4 x 6 sans bordure" : (0, 0), 
    "5 x 7" : (5, 5), 
    "5 x 7 sans bordure" : (0, 0), 
    "8 x 10" : (10, 10), 
    "8 x 10 sans bordure" : (0, 0), 
    "A1" : (3, 2), 
    "A1 sans bordure" : (0, 0), 
    "A2" : (5, 3), 
    "A2 sans bordure" : (0, 0), 
    "A3" : (10, 5), 
    "A3 sans bordure" : (0, 0), 
    "A4" : (20, 10), 
    "A4 sans bordure" : (0, 0), 
    "A5" : (40, 20), 
    "Carte postale" : (5, 5), 
    "Carte postale sans bordure" : (0, 0), 
    "Enveloppe DL" : (5, 5), 
    "Enveloppe n°10" : (5, 5), 
    "JIS B5" : (15, 8), 
    "Lettre US" : (20, 10), 
    "Lettre US sans bordure" : (0, 0), 
    "Légal US" : (20, 10)
}



def create_qr_code(id_rangement:int, barcode_type:str="QRCode") -> bool :
    """
    entrées :
        id_rangement (int), le contenu (id de rangement physique) du QR-Code
        barcode_type (str), le type de code-barre (par défaut QR-Code ("QRCode"))
    
    crée le QR-Code correspondant à l'id fourni (contenu : "{adresse site brickstock}/BrickStock/rangements?id_rangement={id_rangement}")
    return True si le QR-Code à bien été créé et False sinon
    """
    content = f"{BRICKSTOCK_SITE_HREF}/BrickStock/rangements?id_rangement={id_rangement}"
    url = f"https://barcode.tec-it.com/barcode.ashx?data={quote(content)}&code={barcode_type}&dpi=96&imagetype=Png"
    print(url)
    response = requests.get(url)
    if response.status_code == 200 :
        file = open(f"images/QR-Codes_rangements/{id_rangement}.png", "w+b")
        file.write(response.content)
        file.close()
        return True
    else :
        print(f"erreur {response.status_code} : le QR-Code n'a pu être créé")
        return False
    
def generate_qr_codes_sheet(page_size:tuple, marges:tuple, nb_qrcode_par_ligne:int, qrcode_size:float) -> str :
    """
    entrées :
        page_size (tuple), les dimensions de la page en millimètre sous la forme (largeur (int ou float), hauteur, (int ou float))
        marges (tuple), les marges de la page en millimètre sous la forme (marges en haut (int ou float) / bas, marges latérales (int ou float))
        nb_qrcode_par_ligne (int ou None), le nombre de qr-code par ligne (si None : valeur automatique)
        qrcode_size (int, float ou None), la largeur que doit avoir un qr-code sur la feuille (en millimètre) (susceptible d'être adaptée à la largeur de la feuille et au nombre de qr-code par ligne) (si None : valeur automatique)

    génère la ou les page(s) de qr-codes à imprimer
    renvoie le chemin d'accès du fichier pdf correspondant
    """
    assert type(page_size) == tuple
    assert len(page_size) == 2
    assert type(page_size[0]) in (int, float)
    assert type(page_size[1]) in (int, float)
    assert page_size[0] > 0
    assert page_size[1] > 0
    assert type(marges) == tuple
    assert len(marges) == 2
    assert type(marges[0]) in (int, float)
    assert type(marges[1]) in (int, float)
    assert marges[0] >= 0
    assert marges[1] >= 0
    assert marges[0] * 2 < page_size[0]
    assert marges[1] * 2 < page_size[1]
    assert type(nb_qrcode_par_ligne) == int or nb_qrcode_par_ligne == None
    assert type(qrcode_size) in (int, float) or qrcode_size == None
    w, h = page_size[0] - 2 * marges[0], page_size[1] - 2 * marges[1]
    if qrcode_size != None and nb_qrcode_par_ligne != None :
        if w < nb_qrcode_par_ligne * qrcode_size * 1.4 :
            qrcode_size = w / (nb_qrcode_par_ligne * 1.4)
    m = qrcode_size / 5
    case_w, case_h = qrcode_size + 2 * m, qrcode_size + 3 * m
    nb_lignes_par_page = h // case_h
    nb_qrcode_par_page = nb_qrcode_par_ligne * nb_lignes_par_page
    liste_qrcodes_ids = bdd.get_liste_id_rangements_for_qr_code_print()
    # nb_pages = len(liste_qrcodes_ids) / nb_qrcode_par_page
    # nb_pages = int(nb_pages) + {True : 0, False : 1}[int(nb_pages) == nb_pages]
    pdf = fpdf.FPDF(format=page_size)
    x, y = 0, 0
    i = 0
    for id in liste_qrcodes_ids :
        if i % nb_qrcode_par_ligne == 0 :
            x = 0
            y += 1
        if i % nb_qrcode_par_page == 0 :
            pdf.add_page()
            x, y = 0, 0
        pdf.image(f"{BRICKSTOCK_PATH}/images/QR-Codes_rangements/{id}.png", x * case_w + marges[1] + m, y * case_h + marges[0] + m, qrcode_size, qrcode_size)
        pdf.x, pdf.y = x * case_w + marges[1] + m, y * case_h + marges[1] + m + qrcode_size
        pdf.cell(qrcode_size, m, str(id), align="center")
        x += 1
        i += 1
    path = f"{BRICKSTOCK_PATH}/data_save/qr-codes_to_print.pdf"
    pdf.output(path)
    return path