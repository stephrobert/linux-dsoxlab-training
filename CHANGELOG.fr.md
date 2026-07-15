# Journal des modifications

**Language:** [English](./CHANGELOG.md) · [Français](./CHANGELOG.fr.md)

Tous les changements notables de ce projet sont consignés dans ce fichier. Le
format s'appuie sur [Keep a Changelog](https://keepachangelog.com/), et le projet
suit le [versionnage sémantique](https://semver.org/lang/fr/).

## [Non publié]

### Ajouté

- Catalogue de labs initial pour la formation sécurité Linux / DevSecOps
  (RHCSA + LFCS) :
  - 9 labs **L1** de fondamentaux (shell), chacun validé contre l'**état réel**
    de la machine (fini les exercices à trous).
  - labs **L2** stockage et sécurité : swap, LUKS, RAID.
  - un lab de dépannage (service systemd en crash loop) et un capstone
    **examen blanc RHCSA**.
- Gouvernance bilingue (EN/FR) : `README`, `CONTRIBUTING`, `CODE_OF_CONDUCT`,
  `SECURITY`, `RELEASING`.
- Outillage CI et release : validation de structure, lint, et bundles de release
  `tar.gz` (pas de PyPI : le contenu est livré comme archive téléchargeable).
