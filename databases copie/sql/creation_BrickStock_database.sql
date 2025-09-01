CREATE TABLE IF NOT EXISTS Tons(id_ton INTEGER PRIMARY KEY, nom TEXT NOT NULL, rgb_ref TEXT NOT NULL DEFAULT "#FFFFFF");
CREATE TABLE IF NOT EXISTS Couleurs(id_couleur INTEGER PRIMARY KEY, id_couleur_bricklink INTEGER NOT NULL, id_couleur_rebrickable INTEGER NOT NULL, nom TEXT, nom_lego TEXT, nom_bricklink TEXT, nom_rebrickable TEXT, ton TEXT NOT NULL, est_transparent TEXT NOT NULL DEFAULT "False", image_ref TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS Categories(id_categorie INTEGER PRIMARY KEY, nom TEXT, categorie_sup INTEGER, image_ref TEXT);

CREATE TABLE IF NOT EXISTS Design(id_design INTEGER PRIMARY KEY, id_lego INTEGER UNIQUE, id_bricklink TEXT, id_rebrickable TEXT, nom TEXT NOT NULL, nom_lego TEXT, nom_bricklink TEXT, nom_rebrickable TEXT, dimensions_stud TEXT NOT NULL, dimensions_cm TEXT NOT NULL, categorie INTEGER NOT NULL, masse REAL NOT NULL, quantite_mur_pick_a_brick INTEGER NOT NULL DEFAULT 1, image_ref TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS Piece(id_piece INTEGER PRIMARY KEY, id_Lego INTEGER UNIQUE, id_design INTEGER NOT NULL, id_couleur INTEGER NOT NULL, prix_site_lego REAL, image_ref TEXT NOT NULL);

CREATE TABLE IF NOT EXISTS Gammes(id_gamme TEXT PRIMARY KEY, nom_gamme TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS Sets(id_set INTEGER PRIMARY KEY, nom_anglais TEXT NOT NULL, nom_français TEXT NOT NULL, gamme TEXT, image_ref TEXT NOT NULL, annee TEXT NOT NULL, nb_pieces INTEGER NOT NULL DEFAULT 0, tranche_age TEXT NOT NULL, lien_amazon TEXT);
CREATE TABLE IF NOT EXISTS Minifigures(id_minifig TEXT PRIMARY KEY, id_rebrickable TEXT, nom TEXT NOT NULL, gamme TEXT, image_ref TEXT NOT NULL, prix_bricklink TEXT);
CREATE TABLE IF NOT EXISTS piece_dans_set(id_set INTEGER NOT NULL, id_piece INTEGER NOT NULL, quantite INTEGER NOT NULL DEFAULT 0, PRIMARY KEY(id_set, id_piece));
CREATE TABLE IF NOT EXISTS minifig_dans_set(id_set INTEGER NOT NULL, id_minifig TEXT NOT NULL, quantite INTEGER NOT NULL DEFAULT 1, PRIMARY KEY(id_set, id_minifig));