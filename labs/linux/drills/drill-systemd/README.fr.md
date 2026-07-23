# Drill — systemd, timers et planification

**5 tâches, 100 points, 25 minutes. Aucun indice.** Partagé entre RHCSA et LFCS :
systemd se comporte à l'identique sur AlmaLinux et sur Ubuntu, vous choisissez la
cible qui vous arrange.

## Ce qu'est un drill

Un drill n'est pas un lab. Il n'y a pas de cours ici, et c'est délibéré : vous
êtes en conditions d'examen. On vous donne un énoncé, un chronomètre et une
machine, et vous devez retrouver seul des gestes que vous avez déjà pratiqués.

La différence avec un lab tient en trois points :

- **aucun indice n'est disponible**, même contre des points ;
- **le temps compte** : 25 minutes pour cinq tâches, c'est le rythme de
  l'examen, pas celui de l'apprentissage ;
- **les tâches sont indépendantes**. Si l'une résiste, passez à la suivante et
  revenez-y : une tâche non traitée coûte moins cher qu'un chronomètre épuisé
  sur la première.

Le seuil de réussite est fixé à **70 points sur 100**.

## Ce qu'il faut savoir avant de le tenter

Le fil de ce drill est l'écart entre le fichier que vous écrivez et l'état que
systemd retient. Si l'un des sujets ci-dessous ne vous est pas familier, jouez le
lab correspondant **avant** : vous y trouverez le cours, les indices et le droit
à l'erreur que le drill ne vous donnera pas.

| Ce que le drill exerce | Le lab où c'est enseigné |
|---|---|
| Écrire une unité de service, la charger, l'activer et la démarrer | `l3-service-create-unit` |
| Politique de redémarrage, et lire pourquoi un service tombe | `l3-service-diagnose` |
| Timer `OnCalendar`, et le couple timer plus service | `l3-scheduling-timers` |
| Table cron d'un utilisateur et syntaxe des cinq champs | `l3-scheduling-cron` |
| Retrouver dans le journal une exécution passée | `l3-journald-persist` |
| Cible de démarrage par défaut, et le lien symbolique qu'elle est | `l3-boot-target` |

Un seul sujet du drill n'a de lab nulle part : le **masquage définitif d'un
service**. Révisez-le dans le guide avant de vous lancer, en retenant la
différence entre désactiver et masquer.

## Se mettre en conditions

Lancez le chronomètre avant d'ouvrir l'énoncé, pas après. Vingt-cinq minutes
passent vite, et le premier réflexe d'examen consiste à **lire les cinq tâches
d'abord** pour repérer celles qui se traitent en une commande.

Trois habitudes propres à systemd :

- **vérifiez avec `systemctl show`, pas en relisant votre fichier**. Relire ce
  qu'on vient d'écrire ne prouve rien : systemd ne lit le disque qu'au
  rechargement, et il applique par-dessus des surcharges que votre fichier
  n'affiche pas. `systemctl cat` montre l'unité effective, surcharges comprises,
  et `systemctl show -p <Propriété>` donne la valeur que systemd retient vraiment.
  C'est cette valeur-là qui est notée ;
- **`enabled` et `active` sont deux états distincts**. Un service peut tourner
  sans être activé au démarrage, ou l'inverse. Contrôlez toujours les deux, avec
  `systemctl is-enabled` et `systemctl is-active`, avant de considérer une tâche
  finie. Pour un timer, `systemctl list-timers` ajoute la prochaine échéance, qui
  vous dit du même coup si votre expression de calendrier est bien comprise ;
- **oublier le rechargement du démon fausse tout le reste**. Un fichier neuf ou
  modifié qui n'a pas été pris en compte donne des messages incohérents, et vous
  perdrez plus de temps à soupçonner votre syntaxe qu'à taper la commande.
  `systemd-analyze verify` sur votre unité repère au passage les fautes de
  section et de directive.

Pour la partie planification, souvenez-vous que le nom du service de cron n'est
pas le même partout : c'est la table de l'utilisateur qui compte, et elle se
relit avec `crontab -l -u <utilisateur>`, jamais en ouvrant un fichier à la main.

## Après coup

La correction ne dit pas seulement combien de points vous avez : elle dit
**quelle tâche** a échoué et **ce que le système contenait** au moment du
contrôle. Relisez-la avant de rejouer.

Un drill se rejoue. La deuxième tentative sert à mesurer ce que vous avez retenu
de vos erreurs, pas à mémoriser des réponses : les valeurs exactes comptent
moins que les gestes, qui eux se transposent à n'importe quel énoncé.
