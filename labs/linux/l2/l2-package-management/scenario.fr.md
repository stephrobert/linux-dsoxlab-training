# Contexte — amener la machine à l'état logiciel cible

Gérer les logiciels, c'est le quotidien : installer ce dont un service a besoin,
retirer ce qui ne doit pas être là, et savoir prouver le résultat. Là, `zip` est
installé mais indésirable, et `tree` manque mais est nécessaire.

Ta mission, sur la VM :

1. **Installe** le paquet `tree`.
2. **Retire** le paquet `zip`.
3. Sache **interroger** le résultat (`rpm -q tree`, `rpm -q zip`,
   `dnf list installed`).

L'idée : `dnf install`/`dnf remove` changent l'état logiciel et résolvent les
dépendances ; `rpm -q` et `dnf list installed` l'inspectent. Les tests lisent la
base RPM : c'est l'état réel de la machine qui compte.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/
