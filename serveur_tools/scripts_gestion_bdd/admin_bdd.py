from sys import path
# BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.1"
BRICKSTOCK_PATH = "/Users/alexis/Desktop/LEGO/BrickStock/BrickStock 2.2"
path.append(BRICKSTOCK_PATH)

DATABASE_NAME = BRICKSTOCK_PATH + "/databases/BrickStock database.db"
MOC = BRICKSTOCK_PATH + "/databases/My Own Collection.db"
print(DATABASE_NAME, MOC)

# from os.path import exists
# assert exists(DATABASE_NAME), "erreur d'importation : base de données non trouvée"
# assert exists(MOC), "erreur d'importation : base de données non trouvée"

PRIX_PICK_A_BRICK = 19.99
VOLUME_PICK_A_BRICK = 19 * 11 * (5 + 1 / 3)
PRIX_LEGOLAND = 10.0

MODE_SANS_ECHEC = True