# Challenge : ebpf-durcir-sysctl

## Mission

L'audit est formel : eBPF est trop ouvert sur ce serveur. Ferme-le aux
utilisateurs sans privilège, durcis le compilateur JIT pour tous les
programmes, et fais en sorte que cela tienne : les réglages doivent résister à
un rechargement de la configuration sysctl, donc au prochain démarrage.

## Objectif (état attendu)

1. `kernel.unprivileged_bpf_disabled` vaut **2** dans le noyau.
2. `net.core.bpf_jit_harden` vaut **2** dans le noyau.
3. Un appel système `bpf()` (création d'une table eBPF) lancé par l'utilisateur
   sans privilège `nobody` est **refusé** par le noyau, avec l'erreur `EPERM`.
4. Si l'on remet à chaud les deux réglages à `0` puis que l'on recharge la
   configuration avec `sysctl --system`, `net.core.bpf_jit_harden` revient à `2`.
5. Dans les mêmes conditions, `kernel.unprivileged_bpf_disabled` revient aussi à
   `2`.

## Contraintes

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

## Validation

```bash
dsoxlab check ebpf-durcir-sysctl                  # AlmaLinux 10 (cible par défaut)
dsoxlab check ebpf-durcir-sysctl --target ubuntu  # Ubuntu 24.04
dsoxlab hint  ebpf-durcir-sysctl                  # un indice, au prix de points
```
