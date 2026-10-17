# Challenge : ebpf-inventaire-bpftool

## Mission

Un service au nom anodin charge un programme eBPF dans le noyau de cette
machine, et personne ne l'a déployé. Fais l'inventaire des programmes chargés
avec `bpftool`, retrouve le processus puis le service systemd qui portent
l'inconnu, arrête-le pour de bon, et consigne ce que tu as trouvé.

## Objectif (état attendu)

1. Le service systemd qui porte le programme est **arrêté** : plus aucun
   processus, et systemd ne le relance pas.
2. Il **ne revient pas au prochain démarrage** : `systemctl is-enabled` doit
   répondre `disabled` ou `masked` (ou `not-found` si tu as retiré l'unité).
   Toute autre réponse, `enabled` comprise, échoue.
3. Le noyau **ne porte plus** le programme chargé par ce service : `bpftool` ne
   le liste plus.
4. Le fichier `/var/tmp/reponse-inventaire-bpf.txt` contient une ligne
   `service=` qui donne le **nom de l'unité systemd** qui portait le programme.
   Le nom avec ou sans le suffixe `.service` est accepté.
5. Le même fichier contient une ligne `type=` qui donne le **type du programme**
   chargé, tel que `bpftool prog` l'affiche.
6. Les programmes que le système charge lui-même (ceux de systemd, du noyau) sont
   **toujours chargés** : seul celui du service inconnu doit partir.

Format attendu de `/var/tmp/reponse-inventaire-bpf.txt` : deux lignes
`cle=valeur`, sans espace autour du signe égal.

## Contraintes

- Le nom du service change à chaque `dsoxlab run` : la réponse d'une session
  précédente ne vaut rien.
- `bpftool` et `bpftrace` sont déjà installés. Lire ou lister les programmes
  demande les droits root (`sudo`).
- Le **type du programme** est celui que `bpftool prog show` donne en deuxième
  champ de la première ligne d'un programme. Ce n'est pas le type d'un lien
  (`bpftool link`), ni celui d'un descripteur de fichier.
- Tuer le processus ne règle rien : le service le relance. Retirer le fichier de
  l'unité n'arrête pas non plus un processus déjà lancé.
- N'arrête, ne masque et ne retire que le service inconnu : les unités du système
  et les programmes qu'elles chargent doivent rester en place.
- La validation lit l'état de la machine, pas ton historique de commandes.

## Validation

```bash
dsoxlab check ebpf-inventaire-bpftool                  # AlmaLinux 10 (cible par défaut)
dsoxlab check ebpf-inventaire-bpftool --target ubuntu  # Ubuntu 24.04
dsoxlab hint  ebpf-inventaire-bpftool                  # un indice, au prix de points
```
