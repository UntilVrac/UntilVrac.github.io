from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/"
path.append(BRICKSTOCK_PATH)

import requests
from bs4 import BeautifulSoup
from os.path import exists
import sqlite3
from serveur_tools.decomposition_html import *

DATABASE_NAME = "databases/BrickStock database.db"
for i in range(2) :
    if not exists(DATABASE_NAME) :
        DATABASE_NAME = "../" + DATABASE_NAME
    
TAUX = float(requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()["rates"]["EUR"])
# print(TAUX)

en_tete = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

def scrap_price_guide(element_url:str) -> tuple :
    """
    element_url (str) : l'url de la page bricklink correspondant au guide des prix à scrapper

    renvoie le tuple (prix le plus bas, prix moyen, prix le plus haut) correspondant
    """
    response = requests.get(element_url, headers=en_tete)
    if response.status_code == 200 :
        soup = BeautifulSoup(response.content, "html.parser")
        # print(soup)
        try :
            # Récupère le prix de la pièce, ici on prend le premier prix affiché
            table_content = soup.find("table", {"class" : "fv"})
            # print(table_content)
            table_entete = table_content.find("tr", {"bgcolor" : "#C0C0C0"})
            # print(table_entete)
            html = construct_html_arb(str(table_entete))[0]
            assert type(html) == Node
            section = html.getChildren()[2].getChildren()[0].getChildren()[0].getChildren()[0].getChildren()[0]
            # print(section)
            p_min, p_moy, p_max = float(section.getChildren()[2].getChildren()[1].getChildren()[0].getChildren()[0][4:]), float(section.getChildren()[3].getChildren()[1].getChildren()[0].getChildren()[0][4:]), float(section.getChildren()[5].getChildren()[1].getChildren()[0].getChildren()[0][4:])
            print("Prix trouvé")
            return (p_min, p_moy, p_max)
        except :
            print("Erreur : Prix non trouvé")
    else :
        print(f"Erreur lors du scraping de l'URL : {element_url}")
    return (None, None, None)

def scrap_prix_site_lego(id_set:int) -> float :
    """
    id_set (int), id du set

    renvoie le prix du set affiché sur le site Lego s'il existe et None sinon (ancien produit / page inexistante)
    """
    url = f"https://www.lego.com/fr-fr/product/{id_set}"
    response = requests.get(url, headers=en_tete)
    print(url)
    if response.status_code == 200 :
        soup = BeautifulSoup(response.content, features="html.parser")
        # print(soup))
        try :
            div1 = soup.find("div", {"class" : "ProductOverviewstyles__Container-sc-1wfukzv-3 ijtUWJ"})
            # print(div1)
            div2 = div1.find("div", {"class" : "ProductOverviewstyles__PriceAvailabilityWrapper-sc-1wfukzv-8 jFhflf"})
            # print(div2)
            html = construct_html_arb(str(div2))[0]
            prix = html.getChildren()[0].getChildren()[0].getChildren()[0]
            # print(prix)
            prix = float(prix[:5].replace(",", "."))
            print("Prix trouvé")
            return prix
        except :
            print("Erreur : Prix non trouvé")
    else :
        print(f"Erreur lors du scraping de l'URL : {url}")
    return None

# def get_prix_piece_site_lego(id_piece:int) -> float :
#     """
#     id_piece (int), l'id de la pièce

#     renvoie le prix de la pièce affiché sur le site Lego s'il existe et None sinon
#     """
#     if id_piece == None :
#         return None
#     url = "https://www.lego.com/fr-fr/pick-and-build/pick-a-brick?query={id_piece}"
#     print(url)
#     response = requests.get(url, headers=en_tete)
#     if response.status_code == 200 :
#         soup = BeautifulSoup(response.content, features="html.parser")
#         # print(soup)
#         ul = soup.find("ul", {"class" : "ElementsList_leaves__iT4F8 "}) #, "data-test" : "pab-search-results-list"
#         print(ul)
#         li = ul.find("li", {"class" : "ElementsList_leaf__3tVNf ElementsList_row-count-4__HKOE5"})
#         print(li)
#     return None

def get_prix_piece(id_piece:int) -> tuple :
    """
    id_piece (int), id de la pièce

    renvoie le tuple (prix le plus bas, prix moyen, prix le plus haut), pour bricklink
    """
    connexion = sqlite3.connect(DATABASE_NAME)
    curseur = connexion.cursor()
    curseur.execute('''SELECT d.id_bricklink, c.id_couleur_bricklink FROM Design as d JOIN Couleurs as c JOIN Piece as p ON d.id_design = p.id_design AND p.id_couleur = c.id_couleur WHERE p.id_piece = ?;''', (id_piece,))
    r = []
    for e in curseur :
        r.append(e)
    connexion.close()
    assert len(r) == 1
    id_design, id_couleur = r[0]
    # id_design, id_couleur = int(id_design), int(id_couleur)
    # url = f"https://www.bricklink.com/v2/catalog/catalogitem.page?P={id_design}&C={id_couleur}#T=C&C={id_couleur}"
    # url = f"https://www.bricklink.com/ajax/clone/catalogifs.ajax?itemid=299&color=1&ss=FR&cond=N&reg=-1&ca=2&iconly=0"
    url = f"https://www.bricklink.com/catalogPG.asp?itemType=P&itemNo={id_design}&colorID={id_couleur}&v=P&priceGroup=Y&prDec=2"
    prix = scrap_price_guide(url)
    p_min, p_moy, p_max = round(prix[0] * TAUX, 2), round(prix[1] * TAUX, 2), round(prix[2] * TAUX, 2)
    # print(p_min, p_moy, p_max)
    return (p_min, p_moy, p_max)

def get_prix_set(id_set:int) -> tuple :
    """
    id_set (int), id du set

    renvoie le tuple (prix le plus bas, prix moyen, prix le plus haut), pour bricklink
    """
    url = f"https://www.bricklink.com/catalogPG.asp?itemType=S&itemNo={id_set}&itemSeq=1&colorID=0&v=P&priceGroup=Y&prDec=2"
    prix = scrap_price_guide(url)
    # print(prix)
    p_min, p_moy, p_max = round(prix[0] * TAUX, 2), round(prix[1] * TAUX, 2), round(prix[2] * TAUX, 2)
    # print(p_min, p_moy, p_max)
    return (p_min, p_moy, p_max)

def get_prix_minifig(id_minifig:str) -> tuple :
    """
    id_minifig (int), id de la minifig

    renvoie le tuple (prix le plus bas, prix moyen, prix le plus haut), pour bricklink
    """
    url = f"https://www.bricklink.com/catalogPG.asp?itemType=M&itemNo={id_minifig}&itemSeq=1&colorID=0&v=P&priceGroup=Y&prDec=2"
    prix = scrap_price_guide(url)
    # print(prix)
    if prix[0] == None :
        p_min = None
    else :
        p_min = round(prix[0] * TAUX, 2)
    if prix[1] == None :
        p_moy = None
    else :
        p_moy = round(prix[1] * TAUX, 2)
    if prix[2] == None :
        p_max = None
    else :
        p_max = round(prix[2] * TAUX, 2)
    # print(p_min, p_moy, p_max)
    return (p_min, p_moy, p_max)

def get_prix_amazon(lien_set:str) -> float :
    """
    lien_set (str), l'url de la page amazon du set

    renvoie le prix affiché sur la page si il existe et None sinon
    """
    response = requests.get(lien_set, headers=en_tete)
    if response.status_code == 200 :
        soup = BeautifulSoup(response.content, "html.parser")
        # print(soup)
        div_apex_desktop = soup.find("div", {"id" : "apex_desktop", "class" : "celwidget"})
        try :
            # print(div_apex_desktop)
            div_corePriceDisplay_desktop_feature_div = div_apex_desktop.find("div", {"id" : "corePriceDisplay_desktop_feature_div", "class" : "celwidget"})
            div = div_corePriceDisplay_desktop_feature_div.find("div", {"class" : "a-section a-spacing-none aok-align-center aok-relative"})
            # print(div)
            span = div.find("span", {"class" : "a-price aok-align-center reinventPricePriceToPayMargin priceToPay"})
            # print(span)
            html = construct_html_arb(str(span))[0]
            # print(html)
            prix = html.getChildren()[1].getChildren()[0].getChildren()[0] + "." + html.getChildren()[1].getChildren()[1].getChildren()[0]
            print(prix)
            print("Prix trouvé")
            return float(prix)
        except :
            print("Erreur : Prix non trouvé")
    else :
        print(f"Erreur lors du scraping de l'URL : {lien_set}")
    return None

def get_part_infos(id_part:int) -> dict :
    """
    id_part (int), id_part bricklink

    renvoie le dictionnaire {masse : float, dimensions_stud : str, dimensions_cm : str} correspondant avec pour valeur None lorsque l'information correspondant à la clé n'a pas été trouvée
    """
    href = f"https://www.bricklink.com/v2/catalog/catalogitem.page?P={id_part}"
    response = requests.get(href, headers=en_tete)

    infos = {"masse" : None, "dimensions_stud" : None, "dimensions_cm" : None}

    if response.status_code == 200 :
        soup = BeautifulSoup(response.content, "html.parser")
        # print(soup)
        try :
            table = soup.find("table", {"style" : "width:510px; text-align: left;"})
            # print(table)
            td = table.find("td", {"width" : "38%", "valign" : "TOP", "height" : "115px"})
            # print(td)
            font = td.find("font", {"style" : "font-size:12px; line-height:18px;"})
            # print(font)
            html = construct_html_arb(str(font))[0]
            # print(html)
            # print("----------")
            i = 0
            # print(html.getChildren())
            for b in html.getChildren() :
                i += 1
                # print("----")
                # print(b)
                # print("----")
                if b == "Weight: " :
                    infos["masse"] = float(html.getChildren()[i].getChildren()[0][:-1])
                elif b == "Stud Dim.: " :
                    infos["dimensions_stud"] = html.getChildren()[i].getChildren()[0][:-9]
                elif b == "Pack. Dim.: " :
                    infos["dimensions_cm"] = html.getChildren()[i].getChildren()[0][:-4]
            # print(i)
            return infos
        except :
            pass
    return infos



if __name__ == "__main__" :
    pass
    # print(get_prix_piece(300501))
    # print(get_prix_set(75381))
    # print(get_prix_minifig("sw0606"))
    # print(scrap_amazon("https://www.amazon.fr/LEGO-Embarquement-Construction-Collectionner-75387/dp/B0CFW28JMN/ref=sr_1_9?__mk_fr_FR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=2U2FYVBEI8D6U&dib=eyJ2IjoiMSJ9._Z0Msd-e95OhAXuistAMWQNTjcIco6Pu23ukcGmy6O27SRUaxjCSQkS484H356TZlW9DZs5Hg1DcYfR2Qa8wr51dRpGlqNXREdlKZdZI0l5xCNJqoaoN2xEs084eGDPC8BA6NapOkNG_qIaFfuQXrIFdQtK5ffCrNuTNQ5mZuRlczjf3lSfdSIa27HDGjCV_CeAKpx0UiLzQh1GJjWHC7xFXXntztan07yWL0Nj74ldfpmQ-6tk_bW-Ssn2iw24XPbGaLGY_jR7rjECaOs8UxNhmH8y2JWfIC5d2sYbQuK0.Ju-es3QD3UmQnJeGWZCfeO_xlLp46Nw-kGmCTqqaDaw&dib_tag=se&keywords=lego+75376&qid=1744654938&sprefix=lego+75376%2Caps%2C92&sr=8-9"))
    # print(scrap_amazon("https://www.amazon.fr/LEGO-75345-Construction-Minifigurines-Anti-V%C3%A9hicule/dp/B0BBS2K3YK/ref=sr_1_1?__mk_fr_FR=%C3%85M%C3%85%C5%BD%C3%95%C3%91&crid=31G38BPCQHX2C&dib=eyJ2IjoiMSJ9.zhfxVcKYsjYy_3DLt34dHq8alVURI7_3lwnZxFD-AIkSukonk0eQgx2B28pGeJ7N633JC6_8o2DLLiltolV_45iNgYIMpCZzMWMerxbEuGXGwngfT-ecgFyN9JNgJ9807uZVJZ3FpuoVkSNK8dNL8jiyNgJLvxDr2_aOCl7NQHJvsIo9qMaYX0OBTBS5PA6O_jkA3zgqE9gWizLPutnsO0MoD8kHnY_MPyFDaO6w6D9GP453y6S3__2v3mn6mrLtSE1D9NoDbpg1mpUd7FzIGHKIjJCf0evEqNDhuqol4e3n6Hawn3GwfZyaBhEqEPc7Pifnm6X9Abdg9uUaZ50V1IonVyj3TU2tUIwy4rBB7VPjS07Z6FXqwg76AOyxF7K9QXUibxiwa0V75jy0CCCq5ma6WuBNxPG8SQ2Nc7ueKkYwAWCPYPW_dqgEgzbhZOer.nZlgAJWuWdvtjjaOEQ72VhMx-cM5fAbLyBgMgxriH30&dib_tag=se&keywords=lego%2B75345&qid=1740497241&sprefix=lego%2B75345%2Caps%2C71&sr=8-1&th=1"))
    # print(scrap_prix_site_lego(75345))
    # print(get_prix_piece_site_lego(300501))