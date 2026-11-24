# Construire une arborescence à la main

## La situation

Un projet qui démarre, c'est d'abord une structure de répertoires : les sources
d'un côté, les tests, la documentation, la configuration. Personne ne la fabrique
en cliquant. On la pose au clavier, en quelques commandes, et on vérifie ensuite
qu'elle est exactement conforme à ce qui était demandé.

Ce lab te donne l'arborescence cible et te laisse la construire dans ton
répertoire de travail, avec le shell seul. La validation vérifie chaque chemin :
un fichier au bon nom mais au mauvais endroit ne compte pas, et un fichier en
trop non plus.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/navigation-fichiers/

## Construire une arborescence

### Mission

Construis l'arborescence suivante dans `challenge/work/` en n'utilisant que des
commandes shell (`mkdir`, `touch`, `cp`, `mv`) :

```
projet/
├── src/
│   ├── app.py
│   └── utils.py
├── tests/
│   └── test_app.py
├── docs/
│   └── README.txt
└── config/
    └── settings.conf
```

### Contraintes

- Travaille uniquement dans `challenge/work/`.
- Les cinq fichiers doivent exister à leur chemin exact.
- Les quatre répertoires doivent exister.
- N'ajoute pas de fichiers supplémentaires : seulement ceux demandés.

### Validation

```bash
dsoxlab check l1-navigate-filesystem
```
