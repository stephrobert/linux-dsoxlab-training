# Capstone — examen blanc LFCS

**17 tâches, 100 points, 120 minutes, une seule machine. Seuil de réussite :
70/100. Aucun indice.** Cet examen blanc est **LFCS uniquement** : il se joue sur
Ubuntu 24.04, il n'y a pas de cible AlmaLinux.

[**Le LFCS sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/certifications/lfcs/)

## Ce qu'est un examen blanc

Un examen blanc n'est ni un lab ni un drill. Un drill révise un sujet en vingt
minutes ; celui-ci reproduit une session complète, avec sa fatigue, ses
arbitrages de temps et sa note finale.

- **aucun indice n'est disponible**, même contre des points ;
- **les 5 domaines officiels y figurent à leurs poids réels** : Essential
  Commands 20 %, Operations Deployment 25 %, Users and Groups 10 %, Networking
  25 %, Storage 20 %. Deux domaines valent donc à eux seuls la moitié de la note ;
- **tout doit survivre à un redémarrage**. Une règle de pare-feu perdue au
  reboot, un montage absent de la table des systèmes de fichiers, un service
  démarré mais non activé : ces trois cas valent zéro, quelle que soit la
  commande que vous avez tapée.

## Ce qu'il faut savoir avant de le tenter

Ne passez pas cet examen blanc en premier. Il est fait pour être joué **après**
les labs et les drills, quand vous cherchez à mesurer un niveau, pas à apprendre.
Voici, domaine par domaine, où chaque sujet est enseigné.

| Domaine et ce qui y est demandé | Le lab où c'est enseigné |
|---|---|
| Essential Commands : chercher des fichiers sur un critère | `l1-find-files` |
| Essential Commands : archives compressées | `l1-tar-archives` |
| Essential Commands : filtrer des lignes | `l1-grep-regex` |
| Essential Commands : liens physiques et symboliques | `l1-links-hard-sym` |
| Essential Commands : droits et notation octale | `l1-permissions-ugo` |
| Essential Commands : répertoire partagé et bit set-GID | `l2-collaborative-setgid` |
| Operations : écrire et activer une unité de service | `l3-service-create-unit` |
| Operations : diagnostiquer un service qui ne démarre pas | `l3-service-diagnose` |
| Operations : timer `OnCalendar` | `l3-scheduling-timers` |
| Operations : table cron d'un utilisateur | `l3-scheduling-cron` |
| Users and Groups : créer un compte avec des attributs imposés | `l2-user-lifecycle` |
| Users and Groups : déléguer `sudo` au plus juste | `l2-sudo-delegation` |
| Networking : adresse et route statiques persistantes | `l4-network-static-persist` |
| Networking : résolution de noms locale, lue avec `getent hosts` | `l4-network-troubleshoot` |
| Networking : ouvrir un port sans se couper la session | `l4-firewall-persist` |
| Storage : partitionner un disque | `l2-partition-gpt` |
| Storage : pile LVM et extension | `l2-lvm-extend-persist` |
| Storage : système de fichiers XFS | `l2-filesystem-create-xfs` |
| Storage : montage persistant par UUID | `l2-fstab-persist-uuid` |
| Storage : swap | `l2-swap-management` |

Quatre sujets de l'examen n'ont pas de cours sur place, parce que les labs qui
les portent renvoient au guide en ligne plutôt que d'enseigner : `lfcs-package-apt`
pour la gestion des paquets Debian et le gel de version, `lfcs-netplan-static`
pour la configuration réseau, `lfcs-firewall-ufw` pour le pare-feu et
`lfcs-storage-quotas` pour les quotas. Ces quatre labs sont jouables et valent la
peine d'être faits avant : c'est le cours qui manque, pas l'exercice. Les labs
`l4-network-static-persist` et `l4-firewall-persist` enseignent le raisonnement
correspondant côté RHEL, avec d'autres outils.

## Se mettre en conditions

Cent vingt minutes pour dix-sept tâches, cela fait sept minutes par tâche. Ce
budget ne se tient que si vous décidez de l'ordre au lieu de le subir.

- **Lisez le sujet en entier avant la première commande**, et notez pour chaque
  tâche son domaine et son poids. Les tâches de Networking et de Storage pèsent
  lourd et prennent du temps : les garder pour la fin est le meilleur moyen de ne
  pas les finir. Essential Commands rapporte peu par tâche mais se traite vite,
  c'est de la marge à prendre au passage, pas un lieu où s'attarder ;
- **fixez-vous un temps par tâche et tenez-le**. Passé le double du budget prévu,
  laissez la tâche et avancez : vous y reviendrez avec l'esprit clair, et sept
  minutes perdues sur une tâche à cinq points en coûtent deux autres ailleurs ;
- **ne vous coupez pas la machine**. Deux gestes de cet examen peuvent vous
  enfermer dehors : activer le pare-feu, et toucher au réseau. Ouvrez une seconde
  session avant l'un ou l'autre, vérifiez que l'accès SSH reste autorisé avant
  d'activer le filtrage, et ne configurez jamais l'interface qui porte votre
  session : les tâches réseau visent une interface dédiée, identifiez-la et ne la
  confondez pas avec celle que vous donne `ip route get 1.1.1.1` ;
- **prouvez chaque tâche avec l'outil qui lit le système**, pas avec le fichier
  que vous venez d'écrire : `systemctl is-enabled` et `systemctl is-active` pour
  les unités, `findmnt` et `blkid` pour les montages, `swapon --show` pour le
  swap, `getent` pour les comptes et les noms, `sudo -l -U` pour une délégation ;
- **redémarrez la machine avant de valider**. C'est la seule preuve de
  persistance qui vaille, et c'est précisément ce que l'examen mesure. Prévoyez
  ces minutes-là dans votre budget dès le départ.

## Après coup

La correction ne dit pas seulement votre score : elle dit **quelle tâche** a
échoué et **ce que le système contenait** au moment du contrôle. Reportez ces
échecs sur les cinq domaines : trois tâches ratées dans le même domaine ne
signifient pas la même chose que trois tâches ratées un peu partout. Dans le
premier cas, il vous manque un sujet et vous savez lequel ; dans le second, c'est
la gestion du temps ou la persistance qu'il faut travailler.

Rejouez ensuite les labs des tâches manquées, puis les drills du domaine
concerné, avant de revenir à cet examen blanc. Le refaire immédiatement ne
mesure plus que votre mémoire de l'énoncé.
