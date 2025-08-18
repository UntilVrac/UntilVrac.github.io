import sqlite3

connexion = sqlite3.connect("../BrickStock database.db")
curseur = connexion.cursor()

# remplissage tons
def remplissage_tons() :
    file_tons = open("table_tons.csv", "r")
    content_tons = file_tons.read().split("\n")
    file_tons.close()
    for l in content_tons[1:] :
        l = l.replace("\r", "").split(",")
        curseur.execute('''INSERT INTO Tons VALUES (?, ?, ?);''', (int(l[0]), l[1], l[2]))
    connexion.commit()

# remplissage couleurs
def remplissage_couleurs() :
    file_couleurs = open("table_couleurs.csv", "r")
    content_couleurs = file_couleurs.read().split("\n")
    file_couleurs.close()
    for l in content_couleurs[1:] :
        l = l.replace("\r", "").split(",")
        print(l)
        assert l[8] in ("True", "False")
        curseur.execute('''INSERT INTO Couleurs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''', (int(l[0]), int(l[1]), int(l[2]), l[3], l[4], l[5], l[6], int(l[7]), l[8], l[9]))
    connexion.commit()


# remplissage autres tables
def remplissage_minifigures() :
    file_couleurs = open("table_minifigures2.csv", "r")
    content_couleurs = file_couleurs.read().split("\n")
    file_couleurs.close()
    for l in content_couleurs[1:] :
        curseur.execute('''INSERT INTO Minifigures VALUES (?, ?, ?, ?, ?);''', tuple(l.split(",")))
    connexion.commit()

def remplissage_sets() :
    file_sets = open("table_sets.csv", "r")
    content_sets = file_sets.read().split("\n")
    file_sets.close()
    for l in content_sets[1:] :
        l = l.split(",")
        curseur.execute('''INSERT INTO Sets (id_set, nom_anglais, nom_français, gamme, image_ref, annee, nb_pieces, tranche_age, lien_amazon) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);''', (int(l[0]), l[1], l[2], l[3], l[4], int(l[5]), int(l[6]), l[7], l[8]))
    connexion.commit()


# remplissage_tons()
# remplissage_couleurs()

connexion.close()