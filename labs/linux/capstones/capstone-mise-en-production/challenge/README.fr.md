# La recette, puis le lendemain

## La situation

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

## Capstone — mettre un serveur en production

**Format** : 1 mission, 10 tests, 100 points, 2 VM, 90 minutes.
**Score de réussite** : 80/100. **Aucun indice** ne sera révélé.

### La mission

L'équipe de développement a livré l'application **cotisation** dans
`/opt/livraison` sur `alma-rhcsa-1.lab`. Elle contient une page, un fichier
`VERSION` et une consigne d'exploitation.

> Mettez-la en service. Elle doit répondre en HTTP sur le port **8080**, être
> joignable depuis `alma-rhcsa-2.lab`, et **tout doit revenir après un
> redémarrage**.

Lisez `/opt/livraison/LISEZ-MOI.txt` : les contraintes d'exploitation y sont.

### Vos machines

| Hôte | Rôle |
|---|---|
| `alma-rhcsa-1.lab` | AlmaLinux 10 — le serveur à mettre en production, disque `/dev/vdb` libre |
| `alma-rhcsa-2.lab` | AlmaLinux 10 — le client, d'où se prend le verdict |

Connexion : `dsoxlab ssh alma-rhcsa-1.lab`. Vous êtes `student` avec sudo
NOPASSWD.

### Ce qui est noté

| Points | Ce que le test constate |
|---|---|
| 15 | Le contenu vit sur un **volume logique dédié**, monté de façon persistante |
| 10 | Le service tourne sous un **compte système** sans shell de connexion |
| 15 | Le service est **actif**, **enabled**, et écoute sur le réseau |
| 15 | SELinux **enforcing**, port **étiqueté**, contexte du contenu **durable** |
| 10 | Le pare-feu ouvre le port de façon **permanente** |
| 15 | Le **client** obtient un 200 et la bonne page |
| 5 | Le **journal** survit au redémarrage |
| 5 | `sshd` refuse le **mot de passe** et le **compte root** |
| 10 | Une **sauvegarde planifiée** existe et a déjà produit une archive |
| 10 | **Tout revient après un redémarrage réel** |

### Le dernier test redémarre vraiment la machine

Ce n'est pas une formalité. Une mise en production se juge à ce qui **revient
tout seul**. Quatre oublis classiques ne se voient qu'au reboot :

- un montage absent de `/etc/fstab` ;
- un service jamais passé en `enabled` ;
- une règle de pare-feu posée sans `--permanent` ;
- une étiquette SELinux posée par `chcon` plutôt que par `semanage`.

Le test redémarre le serveur, puis redemande la page **depuis le client**. Si
elle revient, les quatre sont bons. Sinon, la livraison est refusée.

### Trois pièges mesurés sur cette machine

Le port **8080 n'appartient pas** à `http_port_t` sur AlmaLinux 10. Les ports
déjà autorisés sont 80, 81, 443, 488, 8008, 8009, 8443 et 9000. Sans
`semanage port`, le service ne peut pas s'y attacher, et le message d'erreur
parlera de permission, pas de SELinux.

`/var/log/journal` **n'existe pas** au départ : journald garde tout en mémoire
et perd l'historique à chaque redémarrage, c'est-à-dire précisément quand vous
en auriez besoin.

La configuration de `sshd` arrive **éclatée en plusieurs fichiers**, comme sur
tout serveur récent. Écrire le vôtre ne garantit donc pas qu'il s'applique :
`sshd` retient la **première** valeur lue, et les fichiers sont lus dans
l'ordre lexical. Le seul contrôle qui vaut est `sshd -T`, qui affiche la
configuration **effective**, pas celle que vous venez d'écrire.

### Méthode

L'ordre qui marche est celui d'un exploitant : le **stockage** d'abord, puisque
tout s'y pose ; le **service** ensuite ; les **protections** après, parce qu'on
n'ouvre que ce qui doit l'être ; la **sauvegarde** en dernier, parce qu'elle
sauvegarde un état qui existe.

Validation : `dsoxlab check`.
