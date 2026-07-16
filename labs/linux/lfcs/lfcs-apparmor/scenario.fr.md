# Contexte — AppArmor, le contrôle d'accès obligatoire de Debian

Là où RHEL utilise SELinux, Debian/Ubuntu utilise **AppArmor** : des profils par
programme qui confinent ce qu'un binaire peut faire. Un profil tourne en
**enforce** (violations bloquées) ou **complain** (violations seulement
journalisées — le mode apprentissage utilisé pour régler un profil).

Ta mission, sur la VM Ubuntu :

1. Passe le profil du binaire `ping` (`/etc/apparmor.d/bin.ping`) en mode
   **complain** : `sudo aa-complain /etc/apparmor.d/bin.ping`.
2. Confirme avec **`sudo aa-status`** — `ping` doit apparaître parmi les profils en
   complain mode.

L'idée : `aa-status` montre les profils chargés et leur mode ; `aa-complain` passe
un profil en mode apprentissage, `aa-enforce` le remet en enforce, `aa-disable` le
décharge. C'est la réponse d'AppArmor à l'enforcing/permissive de SELinux — mais
par profil, pas globale.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/securiser/durcissement/apparmor/
