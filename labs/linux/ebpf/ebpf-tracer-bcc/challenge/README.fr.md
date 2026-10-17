# Challenge : ebpf-tracer-bcc

## Mission

Un service `lab-mystere` fait tourner un programme dont tu ignores le nom, et ce
programme écrit toutes les quelques secondes dans un fichier caché. Trouve les
deux, avec les outils de traçage eBPF, sans arrêter ni modifier le service.

## Objectif (état attendu)

1. Une famille d'outils de traçage est **installée et opérationnelle** sur la
   machine : les outils BCC (`bcc-tools` sur AlmaLinux, `bpfcc-tools` sur
   Ubuntu) ou `bpftrace`.
2. Le fichier `/var/tmp/reponse-ebpf.txt` contient une ligne `binaire=` qui donne
   le **nom du programme** qui écrit. Le nom seul suffit, le chemin complet
   qui se termine par ce nom est accepté.
3. Le même fichier contient une ligne `fichier=` qui donne le **chemin complet**
   du fichier caché où il écrit.
4. Le service `lab-mystere` tourne toujours, sans avoir été redémarré ni modifié.

Format attendu de `/var/tmp/reponse-ebpf.txt` : deux lignes `cle=valeur`, sans
espace autour du signe égal.

## Contraintes

- Le programme et le fichier changent à chaque `dsoxlab run` : la réponse d'une
  session précédente ne vaut rien.
- Le fichier n'est ouvert qu'un instant : la trace du noyau est le moyen de le
  voir, pas la lecture du disque.
- Ne redémarre pas, ne tue pas et ne modifie pas le service : il compte comme un
  service de production. Le critère 4 n'est compté qu'une fois une des tâches
  réussie.
- Charger un programme eBPF demande les droits root (`sudo`).
- La validation lit l'état de la machine, pas ton historique de commandes.

## Validation

```bash
dsoxlab check ebpf-tracer-bcc                  # AlmaLinux 10 (cible par défaut)
dsoxlab check ebpf-tracer-bcc --target ubuntu  # Ubuntu 24.04
dsoxlab hint  ebpf-tracer-bcc                  # un indice, au prix de points
```
