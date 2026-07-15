# Contexte — Service systemd en crash loop

Vous êtes administrateur sur **alma-rhcsa-1.lab**. Le matin, l'astreinte
vous remonte une alerte : un service applicatif appelé
**`demo-crashloop`** est censé tourner en permanence pour exposer une
API interne, mais il **redémarre en boucle** depuis le déploiement
nocturne.

Aucune trace dans le ticket de release ne mentionne un changement de
code. Vous suspectez un problème de configuration ou de packaging.

Votre mission :

1. **Confirmer** que le service est bel et bien en crash loop.
2. **Trouver la cause racine** via les outils standard du sysadmin Linux.
3. **Corriger durablement** pour que le service tourne ET survive à un
   reboot.

Le service est volontairement simple : il s'agit d'un faux démon HTTP
qui démarre, lit sa config, puis attend les requêtes. Tout l'enjeu
pédagogique est dans la **méthode de diagnostic**.
