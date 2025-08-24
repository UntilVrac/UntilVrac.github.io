import requests
from urllib.parse import quote
from sys import path
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
BRICKSTOCK_SITE_HREF = "http://localhost:1520"
path.append(BRICKSTOCK_PATH)



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