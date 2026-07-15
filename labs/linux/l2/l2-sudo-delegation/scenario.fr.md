# Contexte — distribuer juste ce qu'il faut de sudo

L'équipe d'exploitation doit redémarrer des services, mais elle ne doit **pas**
obtenir root complet. C'est de la délégation au moindre privilège : un drop-in
`/etc/sudoers.d` qui autorise le groupe `operators` à lancer `systemctl` — et
seulement ça — sans mot de passe.

Ta mission, sur la VM :

1. Crée un drop-in `/etc/sudoers.d/operators`.
2. Accorde au groupe **`operators`** un sudo `NOPASSWD` pour **`/usr/bin/systemctl`
   uniquement** (pas `ALL`).
3. **Valide la syntaxe** avant qu'il ne prenne effet — un fichier sudoers cassé
   peut bloquer *tout* sudo. Utilise `visudo -cf <fichier>`.

L'idée : les drop-ins sudoers gardent la politique modulaire ; `%groupe` cible un
groupe ; limiter la liste de commandes, c'est le moindre privilège ; et la
validation `visudo` est non négociable car une erreur de syntaxe est
catastrophique.

`sudo -l -U ops` montre ce que l'utilisateur a réellement le droit de faire.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/sudo/
