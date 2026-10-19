# Journal des modifications

**Language:** [English](./CHANGELOG.md) · [Français](./CHANGELOG.fr.md)

Tous les changements notables de ce projet sont consignés dans ce fichier. Le
format s'appuie sur [Keep a Changelog](https://keepachangelog.com/), et le projet
suit le [versionnage sémantique](https://semver.org/lang/fr/).

## [0.2.1] - 2026-10-19

### Modifié

- **Chaque `doc_url` pointe désormais `www.stephane-robert.info`.** Le site est
  passé de `blog.` à `www.`, et l'ancien hôte redirige en 301 vers le même
  chemin. Rien n'était cassé : `validate-structure --check-urls` suit les
  redirections, et ce catalogue était vert avant qu'une ligne change. La
  migration est une mise au propre et non une réparation : un `doc_url` doit
  pointer la page, pas dépendre d'une redirection qu'il faudra bien retirer un
  jour.

  Les chemins sont identiques entre les deux hôtes : seul l'hôte a changé. Les
  359 `doc_url` que les catalogues déclarent ont été cherchés dans le dépôt du
  site, hors réseau : ils y existent tous, y compris vingt-trois pages que
  l'ancien hôte rendait en 404.

## [0.2.0] - 2026-10-17

### Modifié

- **Le validateur lit le contrat, plus l'encadré du terminal.**
  `scripts/valider-labs.py` lisait le score dans ce que `dsoxlab check`
  *affiche*. Cet encadré est de l'interface : il a changé en dsoxlab 0.4.0 et
  la regex a cessé de trouver quoi que ce soit. Il lit désormais
  `check --json`, qui porte un `schema`, et cette lecture vit dans
  `scripts/verdict_check.py`, **identique dans les douze catalogues**.

- **Trois verdicts, pas deux.** Une exécution dont tous les tests collectés ont
  skippé n'a rien mesuré : elle est **SKIP**, ni verte ni rouge, et reste à
  mesurer. La peindre en rouge accuserait le lab de ce qui manque au poste.
  `--check` sort donc en `10` dans ce cas, contre `1` pour un ROUGE, à l'image
  de `dsoxlab doctor --strict` où 9 se répare et 10 se remesure.

- **Le README prend la structure de référence** commune aux douze catalogues :
  quatorze sections, dans les deux langues. Sept d'entre elles décrivent
  dsoxlab et non le sujet, et sont donc identiques partout.

### Exige

- **dsoxlab 0.4.1 ou plus récent**, qui a introduit le champ `status` de
  `check --json`. Sans lui, le validateur refuse de conclure plutôt que de
  deviner.

### En propre

- trois labs eBPF : tracer le noyau avec BCC et bpftool, puis le durcir par sysctl.

## [0.1.1] - 2026-10-14

### Modifié

- Chaque verdict de `validation-labs.json` porte la date de son rejeu : sans
  elle, un relevé ancien et un relevé frais se ressemblent.
- Les vingt labs du bloc l1 rejoués après la modification du `conftest.py`,
  qu'aucun verdict antérieur ne mesurait plus.
- La procédure de release réatteste les labs modifiés depuis leur verdict.

### Corrigé

- Cinq actions GitHub remises à jour.

## [0.1.0] - 2026-10-09

### Modifié

- **La provenance du build atteint désormais SLSA Build Level 3.** Le workflow
  de release attestait depuis son propre job de build, ce que la documentation
  GitHub classe au niveau 2 : « Artifact attestations by itself provides SLSA
  v1.0 Build Level 2 », là où « Reusable workflows can provide isolation between
  the build process and the calling workflow, to meet SLSA v1.0 Build Level 3 ».
  Le badge du README annonçait le niveau 3 depuis un moment ; le workflow le
  produit maintenant.
  - `.github/workflows/attester.yml` est le seul workflow du dépôt à recevoir
    `attestations: write`. Il ne fait aucun `checkout`, ne reçoit qu'un nom et
    une empreinte, et n'exécute aucun code du dépôt.
  - `release.yml` est découpé en trois jobs : construire, attester, publier. Le
    job de publication écrit la release mais ne peut pas attester, faute de la
    permission, et l'archive est recomparée à son empreinte avant publication
    pour qu'un artefact altéré entre deux jobs ne parte pas avec une provenance
    qui ne le décrit pas.
  - Deux linters en désaccord, puis un troisième a tranché. zizmor recommande
    la forme « self-repository » `uses: $/...`, disponible sur github.com
    depuis juillet 2026 ; actionlint 1.7.12, publié en mars, la rejette encore
    comme un format invalide. `$/` a d'abord été retenue, puis retirée :
    Plumber la prend pour une action tierce non épinglée venant d'une source
    non autorisée, deux constats HIGH, et le score est tombé de 100/100 à
    70/100. L'outillage de sécurité ne sait pas encore la lire, et un
    analyseur qui ne comprend pas une construction ne peut pas la juger sûre,
    encore moins sur la ligne qui appelle le workflow qui signe. L'appel est
    revenu à `./`, avec la mesure consignée à côté et un seul acquittement
    zizmor, ciblé.
  - La vérification qui prouve le niveau est dans `RELEASING.fr.md` : elle nomme
    le workflow signataire et échoue si la provenance vient d'ailleurs. Elle
    demande une release réelle : elle n'a donc pas encore été jouée.

### Corrigé — la première campagne de validation complète

Les 84 labs ont été rejoués sur KVM avec contrôle négatif (rouge sans la
solution, vert avec). Neuf défauts sont remontés, tous invisibles jusque-là :
les tests d'un lab ne tournent que si quelqu'un le joue, et personne ne les
enchaînait.

- **`. /root/xxx.env 2>/dev/null || exit 0` ne protégeait rien.** En `sh` POSIX
  non interactif, un `.` sur un fichier absent tue le shell **avant** le `||`.
  Six `cleanup.yaml` en dépendaient (`l2-autofs-ondemand`,
  `l2-disk-space-troubleshoot`, `l2-filesystem-create-xfs`, `l2-partition-gpt`,
  `l2-storage-performance`, `l3-fs-readonly-recover`) : leur `dsoxlab reset`
  échouait, donc l'apprenant restait bloqué. Le test est désormais fait avant
  le source.
- **Trois labs laissaient une partition sur le disque partagé** en n'effaçant
  que la signature de la partition, jamais la table du disque. Ce n'était pas
  eux qui échouaient, mais le **lab suivant**.
- **`l2-lvm-extend-persist` échouait sur un `rmdir`** : `set +e` n'empêche pas
  le module `shell` de rendre le code de la dernière commande. Un `exit 0`
  explicite ferme le sujet.
- **`l2-filesystem-create-xfs` n'était rejouable qu'une fois.** Son `setup` se
  garde avec `creates: /root/.xfs-lab-ready`, que son `cleanup` n'effaçait pas :
  disque nettoyé, marqueur conservé, donc partition jamais recréée et solution
  en échec sur une partition inexistante.
- **`l2-luks-encryption` : le test était faux**, pas la solution. Il cherchait
  le « 2 » de `Version:` dans une tranche de 8 caractères, alors que
  l'alignement de `cryptsetup` le place en 9ᵉ position. Le volume était en LUKS2
  depuis le début. On lit maintenant la valeur du champ.
- **`l3-journald-persist` : la solution écrivait dans un répertoire absent.**
  Le module `copy` ne crée pas les parents, et `cleanup` supprimait
  `/etc/systemd/journald.conf.d`. La solution le crée désormais.
- **`l4-reverse-proxy-lb` et `l4-ldap-integration` étaient infaisables** : leur
  `setup` démarrait le service sur le second nœud sans **ouvrir le port dans
  son pare-feu**. HAProxy rendait un `503 No server is available`, et SSSD ne
  résolvait rien (`No route to host` sur le port 389). L'ouverture fait partie
  de l'état de départ : le sujet de ces labs est le proxy et SSSD, pas le
  pare-feu du serveur.
- **`drill-firewall` laissait `firewalld` désactivé** après son nettoyage, ce
  qui cassait `rhcsa-mock-exam` (« FirewallD is not running »). Un `cleanup`
  rend le système neutre, il ne laisse pas derrière lui l'état de départ du
  drill.
- **`rhcsa-mock-exam` gardait son VG sur le disque partagé.** Son `umount`
  échouait parce que l'export NFS tenait encore `/data/share` à ce moment,
  `exportfs -ua` venant après.

### Ajouté — les garde-fous

Chacun est né d'un défaut réel de cette campagne, et chacun a été vérifié en le
faisant échouer :

- **`tests/test_playbooks_syntaxe.py`** : `ansible-playbook --syntax-check` sur
  les 129 `setup.yaml`/`cleanup.yaml`. Un YAML valide ne prouve pas qu'Ansible
  charge les tâches : une apostrophe française dans un bloc `shell` suffit à
  casser le découpage des arguments, et le lab ne se voyait qu'à l'exécution,
  sous la forme d'un `reset` en `rc=4` sans une seule tâche jouée.
- **`tests/test_marqueurs_setup_cleanup.py`** : tout marqueur `creates:` d'un
  `setup` doit être effacé par son `cleanup`, sinon le lab ne se réinitialise
  qu'une fois. Jouable sans VM, donc en CI. Il a trouvé le défaut de
  `l2-filesystem-create-xfs` et un second cas, `l4-ldap-integration`, qui s'est
  avéré délibéré : il est exempté explicitement, avec son motif.
- **Contrôle du disque partagé** dans `verify-solutions.py` : après chaque lab
  `vm`, le `cleanup` est joué et l'état du disque **comparé à celui d'avant**.
  Un lab n'est accusé que de ce qu'il ajoute, et il est nommé au moment où il
  salit plutôt que de laisser échouer le suivant.

### Corrigé

- **La séquence l1 exigeait d'éditer un fichier sans jamais l'avoir enseigné.**
  Les trois premiers labs demandaient de compléter un fichier de réponses, et le
  challenge de `l1-first-terminal` interdit même de le recréer par redirection,
  alors qu'aucun cours l1 ne montrait comment ouvrir, écrire, sauvegarder et
  quitter un éditeur. La seule occurrence de `vim` dans toute la section était
  la **valeur** de la variable `EDITOR` au lab 19. Un débutant devait donc
  sortir de la formation dès le premier challenge, ce qu'un retour d'apprenant a
  confirmé.
  - `l1-first-terminal` gagne une section « Écrire dans un fichier sans quitter
    le terminal » (FR et EN) : `nano` (Ctrl+O, Ctrl+X), la survie sous `vi`
    (Échap, `:wq`, `:q!`), la variable `EDITOR`, et les entrées de dépannage
    correspondantes. Les exemples portent des noms étrangers au challenge, pour
    ne pas en donner la réponse.
  - `l1-first-terminal` passe **en tête** de la section l1, devant
    `l1-discover-linux-map`, `l1-choose-distro` et `l1-prepare-vm`.

### Ajouté

- **`scripts/verify-solutions.py`** : rejoue les solutions de référence
  chiffrées et prouve qu'elles passent encore les tests. Une montée de version
  peut casser une solution sans que personne ne s'en aperçoive, puisque les
  tests d'un lab ne tournent que si quelqu'un le joue. Le verdict est consigné
  dans `solution/verified-with.json`.
  - `--negative` ajoute le contrôle qui manque le plus : après un
    `dsoxlab reset`, les tests doivent **échouer** sans la solution. Un test qui
    passe dans les deux sens ne prouve rien.
  - Les labs `vm` sans infrastructure provisionnée sont comptés **ignorés**,
    jamais en échec : un harnais absent n'est pas une régression de contenu.
  - Le script refuse de tourner avec un interpréteur sans `pytest`, plutôt que
    de faire échouer les 84 labs d'un coup et de faire croire à une régression.
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

[Non publié]: https://github.com/stephrobert/linux-dsoxlab-training/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/stephrobert/linux-dsoxlab-training/releases/tag/v0.1.1
[0.1.0]: https://github.com/stephrobert/linux-dsoxlab-training/releases/tag/v0.1.0
