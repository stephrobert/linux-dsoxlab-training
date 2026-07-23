# Contexte — le pare-feu Debian : ufw

Sur Debian et Ubuntu, la façade conviviale du pare-feu est **`ufw`**
(Uncomplicated FireWall). Un service web doit être joignable, tu vas donc ouvrir
`http` et activer le pare-feu, tout en gardant ton accès SSH.

L'idée : `ufw` est le pendant Debian de `firewall-cmd`, même principe, syntaxe
volontairement minimale. Le pare-feu a un état actif ou inactif qui lui est
propre, distinct des règles qu'il contient : les deux comptent, et l'ordre dans
lequel tu t'en occupes décide si tu gardes ta session ouverte ou non.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/securiser/reseaux/ufw/
