# Contexte — lire un certificat TLS

On te remet `serveur.crt` et on te pose les questions de base que tout admin doit
savoir répondre en ligne de commande : pour qui est-il, quand expire-t-il, quelle
est son empreinte, et quelle clé publique porte-t-il.

L'idée : `openssl` lit tout ça hors ligne, sur le fichier, sans qu'aucun serveur
ne tourne. À chaque question son sélecteur, qu'il faut aller chercher. Les tests
relancent openssl sur le certificat et comparent : un fichier tapé à la main ou
vide échoue.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/reseaux/fondamentaux/tls-diagnostic/
