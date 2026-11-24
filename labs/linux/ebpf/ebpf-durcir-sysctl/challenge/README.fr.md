# L'audit qui trouve eBPF grand ouvert

## La situation

La semaine dernière, un prestataire a profilé une application sur ce serveur.
Son outil lançait des sondes eBPF sans être root, et pour que cela fonctionne
quelqu'un a relâché les réglages du noyau, à la main, puis a oublié d'y revenir.
Le ticket est clos, le prestataire est parti, et l'audit de sécurité du
trimestre vient de tomber : n'importe quel compte ordinaire de la machine peut
charger du code dans le noyau, et le compilateur qui traduit ces programmes en
instructions processeur n'est pas durci.

Ce n'est pas un détail. Plusieurs failles du noyau n'ont été exploitables que par
un appelant sans privilège, et fermer cette porte est l'un des gestes les moins
coûteux du durcissement Linux. Mais un réglage noyau corrigé à chaud n'est
corrigé que jusqu'au prochain redémarrage, et celui qui a ouvert la porte a
peut-être aussi laissé de quoi la rouvrir.

Ce qui sera vérifié, c'est l'état de la machine : ce que le noyau applique
maintenant, ce qu'il refuse réellement à un utilisateur sans privilège, et ce
qu'il appliquera après un rechargement de la configuration. Pas les commandes
que tu auras tapées.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/ebpf/durcissement/durcir-ebpf/

## Ce qui est demandé

### Mission

L'audit est formel : eBPF est trop ouvert sur ce serveur. Ferme-le aux
utilisateurs sans privilège, durcis le compilateur JIT pour tous les
programmes, et fais en sorte que cela tienne : les réglages doivent résister à
un rechargement de la configuration sysctl, donc au prochain démarrage.

### Objectif (état attendu)

1. `kernel.unprivileged_bpf_disabled` vaut **2** dans le noyau.
2. `net.core.bpf_jit_harden` vaut **2** dans le noyau.
3. Un appel système `bpf()` (création d'une table eBPF) lancé par l'utilisateur
   sans privilège `nobody` est **refusé** par le noyau, avec l'erreur `EPERM`.
4. Si l'on remet à chaud les deux réglages à `0` puis que l'on recharge la
   configuration avec `sysctl --system`, `net.core.bpf_jit_harden` revient à `2`.
5. Dans les mêmes conditions, `kernel.unprivileged_bpf_disabled` revient aussi à
   `2`.

### Contraintes

- La valeur attendue pour `kernel.unprivileged_bpf_disabled` est **2**, pas 1.
  Les deux interdisent eBPF aux utilisateurs sans privilège, mais `1` ne peut
  plus être modifié avant un redémarrage de la machine : le lab ne pourrait plus
  se réinitialiser.
- Lire `net.core.bpf_jit_harden` demande les droits root (`sudo`).
- Pas de redémarrage de la VM : la validation rejoue elle-même le chargement de
  la configuration.
- Tu n'as pas à modifier les fichiers de `/usr/lib/sysctl.d/`, ceux de la
  distribution.
- La validation lit l'état de la machine, pas ton historique de commandes.

### Validation

```bash
dsoxlab check ebpf-durcir-sysctl                  # AlmaLinux 10 (cible par défaut)
dsoxlab check ebpf-durcir-sysctl --target ubuntu  # Ubuntu 24.04
dsoxlab hint  ebpf-durcir-sysctl                  # un indice, au prix de points
```
