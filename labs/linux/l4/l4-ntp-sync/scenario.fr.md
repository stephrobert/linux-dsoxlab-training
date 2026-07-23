# Contexte — remettre l'horloge à l'heure

Cette machine a dérivé : mauvais fuseau, NTP désactivé et `chronyd` même pas
démarré. Les journaux affichent des horodatages incohérents et les poignées de
main TLS échouent quand l'horloge est fausse. Remets-la d'aplomb, et fais en
sorte que ça tienne après un reboot.

L'idée : le fuseau n'est qu'une convention d'affichage, il ne déplace pas
l'instant. L'enjeu est ailleurs, dans une question qui se pose au redémarrage
autant que maintenant : cette machine tient-elle son horloge par le réseau ?
C'est cet état durable qui sera vérifié, pas les commandes que tu auras tapées.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/services/reseau/chrony/
