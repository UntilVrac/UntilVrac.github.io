import requests
from urllib.parse import quote
from sys import path
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
BRICKSTOCK_SITE_HREF = "http://localhost:1520"
path.append(BRICKSTOCK_PATH)

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