# Contexte — bon contenu, mauvaise étiquette

Du contenu web a été placé dans un répertoire personnalisé `/srv/labweb`, mais
sous SELinux enforcing un serveur web confiné ne peut pas le lire : les fichiers
portent le mauvais type (hérité de `/srv`, pas `httpd_sys_content_t`). Ré-étiquette
— et fais en sorte que la correction **tienne** à un relabel complet ou un reboot,
pas juste un `chcon` ponctuel.

Ta mission, sur la VM :

1. Ajoute une **règle de contexte** mappant `/srv/labweb` (et tout ce qui est
   dessous) vers le type **`httpd_sys_content_t`**
   (`semanage fcontext -a -t httpd_sys_content_t "/srv/labweb(/.*)?"`).
2. **Applique**-la aux fichiers existants (`restorecon -Rv /srv/labweb`).

L'idée : `chcon` change une étiquette maintenant mais un relabel l'efface ;
`semanage fcontext` écrit une **règle persistante** et `restorecon` l'applique
depuis cette règle — la façon RHCSA durable. `ls -Z` montre le type actif.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/
