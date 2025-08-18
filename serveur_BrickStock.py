from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
import serveur_tools.requetes as requetes


# choix du numéro de port (max = 65535)
# certains ports comme 80 ont des usages spécifiques
port = 1520

### socketserver.TCPServer.allow_reuse_address = True
s = socket(AF_INET, SOCK_STREAM)
s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
s.bind(("", port)) # le script réserve le port

s.listen(5)
# socket se met à l'écoute.
# les demandes de connexions se mettent à la queue avant d'être traitées
# on en accepte jusque 5 ici, au-delà elles sont rejetées

# serveur se met en écoute -> boucle infinie
while True :
    # s.accept() attend une demande de connexion
    # quand la demande arrive, s.accept() renvoie
    # connexion et address
    connexion, address = s.accept()

    #print("Connexion acceptée de ", address)

    requete_bin = connexion.recv(2**16)
    # le message venant du client peut-être plus ou moins long
    # on supposera que ce message fait toujours moins de 1024 octets.
    requete_str = requete_bin.decode()
    # print(requete_str)
    # la requête est en binaire. decode: binaire -> string
    if requete_str != "" :
        url = requetes.get_url(requete_str)
        print(url)
        # si la requête n'est pas vide
        # print(requete_str) # affiche la requête
        if requetes.is_GET(requete_str) :
            answer_bin = requetes.get_file(url)
            if "Fin" in requete_str :
                answer_bin = requetes.get_file("Fin")
            connexion.send(answer_bin)
        elif requetes.is_POST(requete_str) :
            print(requete_str)
            answer_bin = requetes.rep_post(url, requetes.get_params(requete_str))
            connexion.send(answer_bin)
    # fermeture de la requête
    connexion.close()

    # pour éteindre le serveur, il faudra que le client demande "Fin"
    # extinction dès que "Fin" est contenu quelque part dans la requête
    if "Fin" in requete_str :
        s.close()