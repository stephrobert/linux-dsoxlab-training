# Contexte — une mine dans la config sshd

Quelqu'un a déposé un bout de config avec une faute : `sshd -t` échoue. Le sshd
**en cours** fonctionne encore (il ne relit qu'au reload), donc tu peux toujours
te connecter — mais le prochain `systemctl reload sshd` ou reboot rendrait le
serveur injoignable. Désamorce avant que ça arrive.

Ta mission, sur la VM :

1. Trouve la directive fautive dans `/etc/ssh/sshd_config.d/` (`sshd -t` te dit
   où).
2. **Corrige la valeur invalide** (`MaxAuthTries` doit être un nombre, ex. `3`)
   tout en **gardant `PermitRootLogin no`**.
3. **Valide** avec `sshd -t`, puis `systemctl reload sshd`.

L'idée : `sshd -t` vérifie la config *hors ligne* — lance-le toujours avant un
reload, car une config sshd cassée est la façon dont les admins se verrouillent
dehors. `sshd -T` affiche les réglages effectifs.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/perte-acces-ssh/
