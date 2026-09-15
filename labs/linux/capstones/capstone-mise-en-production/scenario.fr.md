# Contexte — la recette, puis le lendemain

Les deux examens blancs de la section évaluent une **certification**. Ce
capstone évalue autre chose : la capacité à **livrer un serveur qui tient**.

Un apprenant qui ne passe aucune certification mérite lui aussi une épreuve
finale. C'est celle-ci, et elle se résume à une phrase : on vous remet une
application, vous la mettez en service, et **la machine redémarre**.

## Ce que le capstone mesure vraiment

Neuf livrables, et un dixième test qui les reprend tous. La note ne porte
jamais sur les commandes tapées : chaque test lit un **état observable**.

| Livrable | Ce qui se vérifie |
|---|---|
| Stockage | un volume logique dédié, monté par `fstab` |
| Compte de service | système, sans shell de connexion, propriétaire du contenu |
| Service | actif, `enabled`, en écoute côté réseau |
| MAC | SELinux enforcing, port étiqueté, contexte durable |
| Pare-feu | port ouvert de façon permanente |
| Accès | un 200 obtenu **depuis une autre machine** |
| Journal | persistant sur disque |
| SSH | ni mot de passe, ni root |
| Sauvegarde | planifiée, et ayant déjà produit une archive |

## Le redémarrage, et pourquoi il vaut 10 points

Un serveur qui marche le jour de la recette et pas le lendemain n'a pas été
mis en production. Les quatre oublis qui produisent ce résultat sont toujours
les mêmes, et aucun ne se voit avant le reboot :

1. le montage n'est pas dans `fstab` ;
2. le service n'a jamais été passé en `enabled` ;
3. la règle de pare-feu a été posée sans `--permanent` ;
4. l'étiquette SELinux vient d'un `chcon` et non de `semanage`.

Le dernier test redémarre donc la machine pour de bon, puis redemande la page
**depuis le client**. Si elle revient, les quatre sont bons d'un coup.

## Trois pièges propres à cette machine, mesurés

Le port **8080 n'appartient pas** à `http_port_t` sur AlmaLinux 10 : la liste
par défaut est 80, 81, 443, 488, 8008, 8009, 8443, 9000. Le service refusera
de démarrer avec un message de permission qui ne nomme jamais SELinux.

`/var/log/journal` **n'existe pas** : tant qu'il manque, journald garde tout
en mémoire et l'historique disparaît au redémarrage.

La configuration de `sshd` est **éclatée en plusieurs fichiers**. Écrire le
vôtre ne suffit pas : `sshd` retient la **première** valeur lue, dans l'ordre
lexical des fichiers. `sshd -T` dit la configuration effective, le fichier que
vous venez d'écrire ne dit que vos intentions.
