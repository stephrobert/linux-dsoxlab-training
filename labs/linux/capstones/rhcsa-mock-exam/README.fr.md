# Capstone — examen blanc RHCSA EX200

**20 tâches, 2 machines, 180 minutes. Seuil de réussite : 70 points sur 100.
Aucun indice.** Cet examen blanc est **RHCSA uniquement** : il se joue sur deux
AlmaLinux 10, un serveur et un client, il n'y a pas de cible Ubuntu.

[**Le RHCSA sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/certifications/rhcsa/)

## Ce qu'est un examen blanc

Un examen blanc n'est ni un lab ni un drill. Un drill révise un sujet en vingt
minutes ; celui-ci reproduit une session complète de trois heures, avec sa
fatigue, ses arbitrages de temps et sa note finale.

- **aucun indice n'est disponible**, même contre des points ;
- **les tâches ne pèsent pas toutes le même poids**, de 4 à 7 points selon le
  travail qu'elles demandent. Choisir dans quel ordre les traiter fait partie de
  l'épreuve ;
- **certaines tâches dépendent les unes des autres**, puisque deux machines sont
  en jeu : ce que vous exposez depuis le serveur, le client doit pouvoir le
  consommer. Une tâche serveur bâclée en fait tomber une autre côté client ;
- **tout doit survivre à un redémarrage**. Une règle de pare-feu perdue au
  reboot, un montage absent de la table des systèmes de fichiers, un service
  démarré mais non activé : ces trois cas valent zéro, quelle que soit la
  commande que vous avez tapée.

## Ce qu'il faut savoir avant de le tenter

Ne passez pas cet examen blanc en premier. Il est fait pour être joué **après**
les labs et les drills, quand vous cherchez à mesurer un niveau, pas à apprendre.
Voici, domaine par domaine, où chaque sujet est enseigné.

| Ce que l'examen exige | Le lab où c'est enseigné |
|---|---|
| Partitionner un disque en GPT | `l2-partition-gpt` |
| Pile LVM, et extension d'un volume à chaud | `l2-lvm-extend-persist` |
| Créer et étiqueter un système de fichiers XFS | `l2-filesystem-create-xfs` |
| Montage persistant par UUID | `l2-fstab-persist-uuid` |
| Swap sous forme de fichier, actif et persistant | `l2-swap-management` |
| Partage NFS, côté export et côté montage | `l2-nfs-mount-persist` |
| Créer un compte avec UID et shell imposés | `l2-user-lifecycle` |
| Vieillissement du mot de passe | `l2-password-policy` |
| Répertoire collaboratif et bit set-GID | `l2-collaborative-setgid` |
| ACL POSIX sans toucher aux droits classiques | `l2-acl-posix` |
| Adresse statique persistante et nom d'hôte | `l4-network-static-persist` |
| Diagnostiquer un réseau qui ne répond pas | `l4-network-troubleshoot` |
| Pare-feu `firewalld`, règles permanentes et zones | `l4-firewall-persist` |
| Écrire une unité de service et l'activer au démarrage | `l3-service-create-unit` |
| Diagnostiquer un service qui ne démarre pas | `l3-service-diagnose` |
| Timer `OnCalendar` persistant | `l3-scheduling-timers` |
| Synchronisation de temps avec `chrony` | `l4-ntp-sync` |
| Corriger le contexte SELinux d'un fichier | `l4-selinux-context-fix` |
| Booléens SELinux et étiquettes de ports | `l4-selinux-boolean-port` |
| Lire un refus SELinux dans le journal | `l4-selinux-diagnose-avc` |
| Installer et interroger des paquets avec DNF | `l2-package-management` |
| Authentification SSH par clé et durcissement | `l4-ssh-key-auth-harden` |

Deux sujets de l'examen n'ont pas de cours sur place. La **récupération du mot de
passe root** par interruption du chargeur de démarrage est le geste RHCSA par
excellence : le lab `l3-grub-kernel-args` porte les paramètres de noyau au boot,
mais son README renvoie au guide en ligne au lieu d'enseigner. **Flatpak** n'a
aucun lab du tout dans ce dépôt : révisez-le dans le guide avant de vous lancer,
c'est le seul sujet de l'examen que rien ici ne prépare.

Avant d'y aller, les drills couvrent les mêmes gestes en format court :
`drill-storage`, `drill-systemd`, `drill-users-groups`, `drill-network`,
`drill-firewall`, `drill-packages` et `drill-selinux`. Sept drills réussis valent
mieux qu'un examen blanc raté deux fois.

## Se mettre en conditions

Trois heures pour vingt tâches réparties sur deux machines, cela laisse neuf
minutes par tâche en moyenne. La moyenne ne veut rien dire ici : c'est votre plan
d'attaque qui décide du score.

- **Lisez les vingt tâches avant la première commande**, et repérez trois choses :
  quelles tâches se jouent sur le serveur, lesquelles sur le client, et lesquelles
  dépendent d'une autre. Traiter le montage avant l'export, ou l'authentification
  par clé avant la création du compte, revient à faire le travail deux fois ;
- **gardez pour la fin ce qui impose un redémarrage**. La récupération du mot de
  passe root en demande deux et se fait à la console, pas par SSH : la placer au
  milieu de l'épreuve coûte des minutes que vous n'aurez pas ;
- **ne vous coupez pas l'accès en figeant le réseau**. C'est le piège le plus
  cher de cet examen blanc : la machine tient sa configuration réseau du serveur
  d'adresses, et vous devez la rendre permanente. Conservez l'adresse que la
  machine porte déjà. En changer vous déconnecte, et déconnecte aussi le
  correcteur ;
- **avec `firewalld` et SELinux, écrivez dans la politique, pas seulement en
  mémoire**. Une règle de pare-feu sans l'option permanente, un booléen basculé
  sans l'option de persistance, un contexte posé sans être inscrit dans la
  politique de nommage : les trois disparaissent au premier rechargement ou à la
  première réétiquetage. C'est exactement ce que la correction va provoquer ;
- **prouvez chaque tâche avec l'outil qui lit le système**, pas avec le fichier
  que vous venez d'écrire : `systemctl show` et `systemctl is-enabled` pour les
  unités, `findmnt` et `blkid` pour les montages, `getfacl` pour une ACL,
  `getent` pour les comptes, `firewall-cmd --list-all` après rechargement,
  `semanage` et `getsebool` pour SELinux ;
- **redémarrez les deux machines avant de valider**, et gardez une demi-heure
  pour cela dans votre budget. C'est la seule preuve de persistance qui vaille.

Sur l'épreuve réelle comme ici, `man`, `--help` et `/usr/share/doc/` sont vos
seules ressources. Les consulter n'est pas un aveu de faiblesse : c'est la
compétence que l'examen mesure.

## Après coup

La correction ne dit pas seulement votre score : elle dit **quelle tâche** a
échoué et **ce que le système contenait** au moment du contrôle. Lisez-la comme
un diagnostic. Des échecs groupés sur un même domaine signalent un sujet à
reprendre, et vous savez lequel. Des échecs dispersés signalent autre chose : une
gestion du temps trop optimiste, ou des changements qui n'ont jamais été rendus
persistants.

Rejouez ensuite les labs des tâches manquées, puis les drills du domaine
concerné, avant de revenir à cet examen blanc. Le refaire immédiatement ne mesure
plus que votre mémoire de l'énoncé, alors que le jour J l'énoncé sera différent
et les gestes, eux, seront les mêmes.
