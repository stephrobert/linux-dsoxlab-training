# Lab — choisir sa distribution serveur

## Rappel

[**Choisir une distribution Linux serveur**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/distributions-serveur/)

En contexte serveur, deux familles dominent : la famille **Debian** (Debian,
Ubuntu Server) et la famille **Red Hat** (RHEL, Rocky Linux, AlmaLinux). Le
guide les compare à des voitures : le moteur, le noyau Linux, est le même ; le
tableau de bord, les outils d'administration et l'emplacement de certains
fichiers changent selon le constructeur.

Ce que « noyau », « distribution » et « famille » veulent dire précisément est
traité dans `l1-discover-linux-map` : rien de tout cela n'est repris ici. Ce
lab-ci part de la question suivante, celle qui se pose vraiment le jour où l'on
monte un serveur : **sur quels critères tranche-t-on, et que signe-t-on en
tranchant ?**

## Le cours

Les mesures reproduites ci-dessous portent volontairement sur autre chose que le
challenge : elles interrogent des **dépôts de paquets** et l'**état de sécurité**
d'un poste, jamais l'identité du système. Elles viennent d'un poste
**Ubuntu 24.04.2 LTS** (noyau `6.8.0-134-generic`), et **la machine sur laquelle
vous jouez ce lab n'est peut-être pas de la même famille**. Aucune ne demande
`sudo`, aucune n'installe ni ne modifie quoi que ce soit : lancez-les chez vous et
comparez.

Tout ce qui ne se mesure pas depuis un poste (cycles de vie, tarifs, gouvernance)
vient de deux pages du guide, citées à chaque fois : la page de référence liée
ci-dessus et le comparatif
[Debian vs Ubuntu vs AlmaLinux](https://blog.stephane-robert.info/docs/admin-serveurs/linux/distributions/comparatif/).

### Le critère qui décide vraiment : la durée, et surtout le périmètre

Choisir une distribution, ce n'est pas choisir un logo, c'est **signer un contrat
de support**. Ce contrat a deux termes, et presque tous les comparatifs n'en
citent qu'un.

Le premier terme, celui que tout le monde publie, est la **durée**. Voici ce
qu'annoncent les projets, tel que le comparatif du guide le relève :

| Distribution | Support gratuit | Détail du cycle |
|---|---|---|
| Debian 13 | 5 ans | 3 ans de support complet (jusqu'au 9 août 2028), puis 2 ans de LTS (jusqu'au 30 juin 2030) |
| Ubuntu 26.04 LTS | 5 ans | maintenance standard de `main` jusqu'en 2031 |
| AlmaLinux 10 | 10 ans | support actif jusqu'au 31 mai 2030, correctifs de sécurité jusqu'au 31 mai 2035 |

Le second terme, celui que personne ne publie, est le **périmètre** : la liste des
paquets que l'éditeur s'engage réellement à corriger. Et c'est lui qui décide,
parce qu'un nombre d'années sans périmètre ne veut rien dire.

Ce périmètre se mesure, sans droits particuliers. Sur une machine de la famille
Debian, `apt-cache policy` indique de **quel dépôt** sort chaque version d'un
paquet :

```bash
apt-cache policy nginx fail2ban
```

```text
nginx:
  Candidate: 1.24.0-2ubuntu7.15
     1.24.0-2ubuntu7.15 500
        500 http://fr.archive.ubuntu.com/ubuntu noble-updates/main amd64 Packages
        500 http://security.ubuntu.com/ubuntu noble-security/main amd64 Packages
[...]
fail2ban:
  Candidate: 1.0.2-3ubuntu0.1
     1.0.2-3ubuntu0.1 500
        500 http://fr.archive.ubuntu.com/ubuntu noble-updates/universe amd64 Packages
[...]
```

Deux paquets, deux contrats. `nginx` vient de **`main`** et sa dernière version
est servie par **`noble-security`**, la preuve qu'un correctif y est publié pour
lui. `fail2ban` vient de **`universe`** : le guide rappelle que l'engagement
gratuit de Canonical porte sur `main` seulement, `universe` étant couvert « au
mieux », sans engagement, et **dès le premier jour**. Un serveur exposé sur
Internet qui compte sur `fail2ban` compte donc sur un paquet hors contrat.

> **Nuance relevée sur la machine, et absente du guide.** Sur ce même poste,
> `apt-cache policy docker.io` montre une version servie par
> `security.ubuntu.com noble-security/universe` : un paquet de `universe` **peut**
> donc recevoir une mise à jour par le canal de sécurité. Il n'y a simplement
> **aucune garantie** qu'il en reçoive une, et `fail2ban` comme `certbot`, mesurés
> dans la même seconde sur la même machine, n'en ont aucune. « Sans engagement »
> ne veut pas dire « jamais corrigé », cela veut dire « rien à opposer à l'éditeur
> le jour où ça ne l'est pas ».

Retenez la méthode plus que le résultat : avant de choisir, listez les cinq ou six
paquets qui portent réellement votre service, et **demandez à la machine d'où ils
sortent**. C'est la seule façon honnête de comparer deux distributions.

### Qui publie les correctifs, et qui vend le support

La durée annoncée cache souvent un changement de main, et le guide le documente
pour les trois distributions.

Chez **Debian**, les années 4 et 5 ne sont pas portées par l'équipe de sécurité de
Debian mais par la **Debian LTS Team**, financée par un sponsoring d'entreprises
organisé par Freexian : l'indépendance de Debian ne s'étend pas mécaniquement à la
fin de son cycle. Chez **Ubuntu**, le contresens le plus répandu est de croire
qu'ESM prend le relais après cinq ans : c'est vrai pour `main` (`esm-infra`), faux
pour `universe`, couvert par `esm-apps` **dès la première année**. Chez
**AlmaLinux**, les dix ans sont réels mais engagent en retour : il n'existe **pas
d'EUS gratuit**, une version mineure meurt à la sortie de la suivante, donc rester
couvert signifie **suivre la branche** et non figer un état.

Le critère suivant en découle et se pose en une phrase : y a-t-il quelqu'un à
appeler, et à quel prix ?

- **RHEL** est payante, sous forme d'abonnement avec support : ce que l'on paie
  n'est pas le logiciel mais le support, les certifications et la conformité.
- **AlmaLinux** est à l'opposé : la fondation **ne vend rien**, il n'y a aucune
  souscription à activer ni agent d'abonnement à installer. Le support commercial
  existe, mais il est vendu par un tiers (TuxCare, chez CloudLinux, qui finance la
  fondation).
- **Ubuntu** occupe la position intermédiaire : Ubuntu Pro est gratuit jusqu'à
  5 machines en usage personnel (50 pour les membres officiels de la communauté),
  payant au-delà, à partir de 500 dollars par machine et par an au tarif public
  relevé par le guide en juillet 2026.
- **Debian** n'a pas d'éditeur : au-delà du LTS, l'ELTS est un service commercial
  de Freexian.

Ces montants et ces dates sont les faits les plus périssables de ce cours.
Revérifiez-les à la source avant une décision engageante : le comparatif du guide
donne les pages officielles à consulter.

### L'écosystème de paquets : la bonne question n'est pas « combien »

Le troisième critère se formule souvent en volume. Le volume, pourtant, ne
départage rien. Sur le poste de mesure, l'archive annonce plus de 82 000 paquets
binaires, toutes composantes confondues :

```bash
apt-cache stats
```

```text
Total package names: 162684 (4 555 k)
[...]
  Normal packages: 82982
[...]
```

Aucune distribution sérieuse ne manque de paquets. Ce qui départage, c'est
**lesquels existent et sous quel nom**, et le guide AlmaLinux 10 en donne trois
exemples qui coûtent cher quand on les découvre en production :

- **`redis` n'existe plus** dans la génération EL10. Le remplaçant est `valkey`.
  Un rôle d'automatisation qui installe `redis` ne se dégrade pas : il casse, sur
  un message de paquet introuvable.
- **Docker est hors distribution** : il faut passer par le dépôt de l'éditeur, ou
  utiliser Podman, présent et couvert.
- **`fail2ban` et `certbot` viennent d'EPEL**, un dépôt de la communauté Fedora
  sans aucun engagement de service.

La symétrie est instructive : les deux familles ont un trou de couverture, il
n'est simplement pas au même endroit, dans `universe` chez Ubuntu, à la frontière
AppStream/EPEL chez AlmaLinux. La question n'est donc pas « qui couvre le plus »
mais **« quel trou puis-je assumer »**, et cela dépend entièrement de ce que vous
posez sur la machine.

### La compatibilité avec les logiciels tiers : un problème contractuel

Le quatrième critère est celui que les comparatifs techniques manquent le plus
souvent, et c'est pourtant la vraie raison pour laquelle des entreprises paient
RHEL.

Un progiciel métier, un ERP, une base de données propriétaire sont **certifiés**
pour une distribution précise, presque toujours RHEL, parfois Ubuntu, rarement
autre chose. Le guide AlmaLinux 10 pose le cas sans détour : un logiciel certifié
RHEL **fonctionnera** sur AlmaLinux, puisque l'interface binaire est compatible,
mais **l'éditeur ne le supportera pas** tant que la certification n'existe pas. Si
vous ouvrez un ticket, la première question portera sur votre distribution et la
réponse sera de reproduire le problème sur RHEL. Le coût de ce choix n'est donc
**pas technique, il est contractuel** : nul pour un serveur web ou une
infrastructure maison, décisif pour une machine qui porte un progiciel critique
sous contrat.

### Les compétences de l'équipe : quatre écarts que l'on paie en formation

Le cinquième critère est le plus sous-estimé : ce que votre équipe sait déjà
faire. Les deux familles ont fait quatre choix techniques différents, et chacun se
paie en temps d'apprentissage. Chaque ligne renvoie au lab qui l'enseigne.

| Domaine | Famille Red Hat | Famille Debian | Labs |
|---|---|---|---|
| Paquets | `dnf` / `rpm` | `apt` / `dpkg` | `l2-package-management`, `lfcs-package-apt` |
| Contrôle d'accès obligatoire | SELinux | AppArmor | `l4-selinux-context-fix`, `lfcs-apparmor` |
| Pare-feu | firewalld | ufw | `l4-firewall-persist`, `lfcs-firewall-ufw` |
| Réseau | NetworkManager | netplan | `l4-network-static-persist`, `lfcs-netplan-static` |

Ces écarts ne sont pas cosmétiques. Un exemple par ligne suffit à le montrer.

**Paquets : deux philosophies de la suppression.** Le lab `l2-package-management`
a mesuré que `dnf remove` **nettoie les dépendances devenues orphelines**, parce
que `clean_requirements_on_remove=True` est actif par défaut dans
`/etc/dnf/dnf.conf`. Le lab `lfcs-package-apt` a mesuré l'inverse : `apt remove`
laisse l'orpheline en place, se contente de signaler
`Use 'sudo apt autoremove' to remove it.` et attend une seconde commande. Même
intention de l'administrateur, deux états du système à l'arrivée.

**Contrôle d'accès obligatoire : deux mondes.** Sur ce poste, la question se
tranche en deux commandes :

```bash
aa-status --enabled ; echo "AppArmor actif : $?"
ls /sys/fs/selinux
```

```text
AppArmor actif : 0
ls: cannot access '/sys/fs/selinux': No such file or directory
```

Un code de retour nul pour AppArmor, et pas de trace de SELinux. Sur une
AlmaLinux, le lab `l4-selinux-context-fix` relève exactement l'inverse :
`getenforce` répond `Enforcing`. Ce n'est pas une préférence, c'est un
dépaysement complet, avec ses commandes (`semanage`, `restorecon`, `ls -Z`) et
ses pannes propres.

**Pare-feu et réseau : les outils ne sont même pas installés.** Toujours sur ce
poste :

```bash
command -v nmcli firewall-cmd ufw netplan nft
```

```text
/usr/sbin/netplan
/usr/sbin/nft
```

Trois des cinq binaires cherchés n'existent pas ici. Une procédure écrite pour
l'une des familles ne s'exécute pas dans l'autre : elle échoue à la première
commande, sur un « commande introuvable ». C'est cela, le coût réel du changement
de famille, bien plus que la syntaxe.

> À noter, parce que c'est contre-intuitif : le guide relève qu'**aucune des
> images cloud mesurées, Debian comme AlmaLinux, n'a de pare-feu installé**. Le
> « firewalld actif par défaut » que l'on prête à la famille Red Hat est vrai
> pour une installation par l'ISO, faux en image cloud. Le filtrage est à votre
> charge dans tous les cas.

### Le paysage Red Hat depuis 2023, et ce qu'il change pour la RHCSA

C'est la question que tout débutant se pose devant les noms qui circulent.
Voici ce que le guide établit, et rien de plus.

**AlmaLinux et Rocky Linux sont des reconstructions gratuites de RHEL**,
utilisables pour s'entraîner sur un environnement identique à RHEL sans coût.
Ce sont les deux distributions que le guide recommande pour préparer la RHCSA,
en rappelant que **l'examen, lui, se passe sur RHEL**.

**Depuis juillet 2023, elles ne visent plus la même cible.** AlmaLinux a
abandonné la compatibilité « 1:1, bug pour bug » au profit de la **compatibilité
ABI** : un binaire compilé pour RHEL fonctionne sur AlmaLinux. Rocky Linux, lui,
**revendique toujours le bug pour bug**. Le guide insiste sur deux points de
prudence :

- N'écrivez pas « AlmaLinux n'est plus compatible RHEL » : c'est faux, et trois
  ans après, il n'existe aucun cas documenté de logiciel cassé par cet écart.
- N'écrivez pas non plus « Red Hat viole la GPL » : ni la Software Freedom
  Conservancy ni la Free Software Foundation ne l'affirment, et seul un tribunal
  pourrait trancher.

**La conséquence la plus concrète est matérielle.** RHEL 10 et ses
reconstructions exigent un processeur `x86-64-v3` (grosso modo un Intel Haswell
de 2013 ou plus récent). AlmaLinux fournit **en plus** une variante `x86-64-v2`,
ce que Rocky ne fait pas. Sur un hyperviseur qui expose un CPU générique
(`kvm64` par défaut sur Proxmox), la machine virtuelle **ne démarre pas**, sur un
`Fatal glibc error` trompeur. C'est le premier piège à connaître si vous montez
votre laboratoire d'entraînement vous-même.

**Pour la RHCSA, en pratique**, ce paysage ne change presque rien : les fichiers
de configuration, les commandes `systemd`, `dnf` et `firewalld` sont ceux de RHEL,
et c'est ce que l'examen vérifie. Le choix entre AlmaLinux et Rocky se joue sur des
détails d'exploitation, le matériel disponible en premier.

> **Ce que ce cours n'affirmera pas.** Vous croiserez aussi le nom **CentOS
> Stream**. Le corpus de ce site le range dans l'écosystème Red Hat, au même titre
> que RHEL, Rocky et AlmaLinux (mêmes outils, `dnf` et firewalld par défaut), mais
> aucun guide n'en donne le cycle de vie et **aucun ne le propose pour préparer la
> RHCSA** : les deux distributions nommées pour cela sont AlmaLinux et Rocky.
> Voulez-vous savoir précisément ce qu'est CentOS Stream et comment il se situe
> par rapport à RHEL ? Allez le vérifier chez le projet lui-même. Ce cours préfère
> se taire que vous transmettre une approximation, et c'est exactement le réflexe
> que ce lab veut vous donner.

### Récapitulatif : partir de sa situation, pas des mérites supposés

Le comparatif du guide entre par situation plutôt que par distribution. C'est la
bonne façon de trancher, parce qu'elle rend visible **ce que l'on accepte en
échange**.

| Votre situation | Le guide propose | Ce que vous acceptez en échange |
|---|---|---|
| Une pile auto-hébergée : conteneurs, cache, reverse proxy, `fail2ban`, `certbot` | Debian 13 | un cycle de 5 ans, donc une migration à préparer plus tôt |
| Un parc long et stable, sans budget de souscription | AlmaLinux 10 | `fail2ban` et `certbot` hors périmètre (EPEL), et un CPU `x86-64-v3` exigé |
| Du cloud public, des images officielles partout | Ubuntu 26.04 LTS | `universe` non couvert sans Ubuntu Pro |
| Un progiciel métier certifié RHEL | RHEL | un abonnement, en échange d'un support contractuel |
| Préparer la RHCSA | AlmaLinux ou Rocky Linux | rien : l'environnement est celui de l'examen |

Un dernier conseil du guide, pour qui n'a aucune contrainte : commencez par Debian
ou Ubuntu Server LTS, c'est le chemin le plus simple, et vous passerez plus tard à
une distribution Red Hat sans difficulté. Les concepts sont les mêmes ; seules
quelques commandes d'administration changent, et vous venez de voir lesquelles.
Une règle vaut d'ailleurs pour toutes les familles : **choisissez toujours une
version à support long**. Ubuntu publie aussi des versions intermédiaires (25.04,
25.10) avec neuf mois de support, ce qui n'a aucun sens pour un serveur.
