# Une panne qui ne dit pas son nom

## La situation

Ce capstone n'est pas un lab de dépannage de plus. La section en compte déjà
plusieurs, et ils ont tous le même défaut : leur titre donne la moitié du
diagnostic. « Réparer un problème SELinux » vous a déjà dit où chercher.

Ici, vous ne recevez qu'un **symptôme** :

> Le site interne ne répond plus.

Le setup a monté un site qui **fonctionnait**, l'a prouvé, puis a cassé **une
seule chose**, tirée au sort parmi six. Personne ne vous dira laquelle. C'est
la différence entre appliquer une procédure et savoir dépanner.

## Les six pannes possibles

Elles ne sont listées ici que pour que vous sachiez que la liste est **finie**,
et qu'aucune n'est exotique. Toutes produisent le même symptôme vu du client.

| Famille | Ce qu'il faut savoir regarder |
|---|---|
| Service | l'état et la persistance de l'unité |
| Port | ce qui écoute, et sur quelle adresse |
| Pare-feu | ce qui est ouvert, et de façon permanente ou non |
| SELinux | le contexte du contenu servi |
| Permissions | la traversée du répertoire et la lecture du fichier |
| Écoute locale | l'adresse d'écoute, pas seulement le numéro de port |

Une septième panne a été écartée après mesure : remplir le disque **n'arrête
pas** un site statique. Servir un fichier ne demande aucune écriture.

## La règle qui fait la valeur de l'épreuve

Trois réparations « marchent » et sont notées **zéro** :

- passer SELinux en permissive ;
- arrêter le pare-feu ;
- ouvrir le docroot en écriture à tout le monde.

Chacune fait répondre le site, et chacune désarme une protection de la machine
entière pour un problème local. Un serveur qui répond parce qu'il n'est plus
protégé n'est pas réparé.

## Persistance

Ce qui ne survivrait pas à un redémarrage vaut zéro. Attention au cas SELinux :
un `chcon` survit à un reboot, mais **pas à un réétiquetage**. Les tests lancent
`restorecon` avant de conclure.

## Capstone — serveur cassé

**Format** : 1 symptôme, 7 tests, 100 points, 2 VM, 45 minutes.
**Score de réussite** : 80/100. **Aucun indice** ne sera révélé.

### Le symptôme

> Le site interne hébergé sur `alma-rhcsa-1.lab` ne répond plus.
> Les utilisateurs, qui y accèdent depuis `alma-rhcsa-2.lab`, n'obtiennent rien.
>
> À vous de jouer.

C'est tout ce que vous aurez. Le site fonctionnait il y a quelques minutes.

### Vos machines

| Hôte | Rôle |
|---|---|
| `alma-rhcsa-1.lab` | AlmaLinux 10 — le serveur en panne |
| `alma-rhcsa-2.lab` | AlmaLinux 10 — le client, d'où se prend le verdict |

Connexion : `dsoxlab ssh alma-rhcsa-1.lab`. Vous êtes `student` avec sudo
NOPASSWD.

**Le verdict se prend depuis le client.** Un `curl localhost` qui répond 200 sur
le serveur ne prouve rien : c'est exactement ce qui se passe quand le service
n'écoute que sur la boucle locale, ou quand le pare-feu a refermé le port.
Testez comme un utilisateur.

### Ce qui est noté

| Points | Ce que le test constate |
|---|---|
| 30 | Le client obtient un **200** et la bonne page |
| 10 | Le service est **actif** et **enabled** |
| 10 | L'écoute est ouverte au réseau, pas seulement locale |
| 10 | Le pare-feu **tourne** et le port est ouvert en **permanent** |
| 15 | SELinux est **toujours en enforcing** |
| 15 | Le contexte du contenu servi est **durable** |
| 10 | Le docroot n'est **pas** inscriptible par tous |

### Les trois pièges qui vous coûtent le capstone

Ils font répondre le site, et ils sont notés zéro :

1. `setenforce 0` ou `SELINUX=permissive` ;
2. `systemctl stop firewalld` ;
3. `chmod -R 777` sur le docroot.

Ce ne sont pas des réparations, ce sont des régressions de sécurité. Le capstone
existe précisément pour faire la différence.

### Persistance

Ce qui ne survivrait pas à un redémarrage vaut zéro. Un cas mérite votre
attention : `chcon` corrige le contexte SELinux **du moment**, et survit même à
un reboot, mais un réétiquetage du système l'efface. Les tests lancent
`restorecon` avant de conclure : seule une règle `semanage fcontext` tient.

### Méthode

Aucune méthode ne vous est imposée. Celle qui marche, en revanche, part
toujours de l'**observation avant la modification** :

```text
constater le symptôme depuis le client
        ↓
observer l'état du serveur, sans rien changer
        ↓
formuler UNE hypothèse
        ↓
la vérifier, puis corriger ce point-là
        ↓
re-tester depuis le client
```

Validation finale : `dsoxlab check`.
