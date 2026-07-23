# Contexte — faire de cette machine une passerelle NAT

Cette machine doit router le trafic : les connexions entrantes sur **`tcp/8080`**
doivent être envoyées vers un backend en **`192.0.2.20:80`**, avec l'adresse
source masquée pour que les réponses reviennent. Et ça doit tenir après un
reboot : une règle NAT qui disparaît au redémarrage est pire que rien.

L'idée : router du trafic pour le compte d'autrui n'est pas le comportement par
défaut du noyau, il faut l'autoriser. Rediriger un port et masquer l'adresse
source sont ensuite deux traitements distincts, à deux moments différents du
parcours d'un paquet. Enfin, une règle nftables posée à chaud meurt au reboot :
la persistance se configure ailleurs.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/securiser/reseaux/nat-port-forwarding/
