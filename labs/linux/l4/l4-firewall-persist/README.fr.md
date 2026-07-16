# Lab — ouvrir un service firewalld de façon permanente

> Préparer : `dsoxlab provision` puis `dsoxlab run l4-firewall-persist`

## Rappel

[**firewalld sur le guide compagnon**](https://blog.stephane-robert.info/docs/securiser/reseaux/firewalld/)

`firewalld` filtre par **zone** (défaut `public`). `firewall-cmd --add-service`
change le runtime seulement (perdu au reload/reboot) ; `--permanent` écrit la
config de zone, et `--reload` applique le permanent au runtime. Vérifie avec
`--list-services` (runtime) et `--permanent --list-services`.

Ne retire jamais `ssh` — ça fermerait ton accès de gestion.

## Objectifs

- `http` est dans la liste de services runtime ;
- `http` est dans la liste permanente (persistance reboot) ;
- `ssh` est toujours autorisé.

## Valider

```bash
dsoxlab check l4-firewall-persist
```
