# Laisser passer le service web à travers le pare-feu

## La situation

Un serveur web va tourner sur cette machine, mais `firewalld` bloque HTTP. Ouvre
le service `http`, et fais en sorte que ça tienne après un reload et après un
reboot, pas seulement jusqu'au prochain rechargement du pare-feu.

L'idée : un pare-feu a deux états, celui qui tourne et celui qui est écrit sur
disque. Une règle posée à chaud est perdue au premier reload comme au reboot. À
l'arrivée, **les deux** listes, runtime et permanent, doivent montrer `http`.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/securiser/reseaux/firewalld/

## Ce qui est demandé

### Mission

Ouvre `http` à travers firewalld pour que ça survive au reload et au reboot.
Garde `ssh` ouvert.

### Objectif (état attendu)

1. `http` dans `firewall-cmd --list-services` (runtime).
2. `http` dans `firewall-cmd --permanent --list-services` (persistance reboot).
3. `ssh` toujours autorisé.

### Contraintes

- **Ne retire jamais `ssh`** — c'est ton accès de gestion.
- On lit la config runtime et permanente de firewalld, pas ton historique.

### Validation

```bash
dsoxlab check l4-firewall-persist
```
