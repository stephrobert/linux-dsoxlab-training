# 🎯 Challenge — Diagnostiquer et corriger un service en crash loop

## ✅ Objectif

Faire passer le service `demo-crashloop` de l'état `failed`/`activating`
à l'état `active` ET `enabled` sur la VM cible (`alma-rhcsa-1.lab` par
défaut), de manière à ce que la correction **survive à un reboot**
(critère RHCSA `persistence_after_reboot`).

Tu travailles directement sur la VM via la session SSH ouverte par
`dsoxlab run`. Tape les commandes de diagnostic et de correction en
direct — pas de script à écrire. La validation se fera par
`dsoxlab check` qui lance des tests pytest+testinfra.

## 🧪 Méthode de diagnostic attendue

Un sysadmin senior n'écrit pas une recette toute prête. Il suit la
méthode :

1. **Confirmer le crash loop**
   `systemctl status demo-crashloop.service`

2. **Trouver la cause racine** dans le journal système (premier
   message d'erreur, pas le dernier)
   `sudo journalctl -u demo-crashloop.service -b --no-pager | head -30`

3. **Lire le contrat** que le binaire impose
   `sudo systemctl cat demo-crashloop.service`
   `sudo cat /usr/local/bin/demo-crashloop`

4. **Appliquer la correction durable** (le service doit `active` ET
   `enabled` pour survivre au reboot)

5. **Vérifier**
   `systemctl is-active demo-crashloop.service`
   `systemctl is-enabled demo-crashloop.service`

## 🧩 Pièges à éviter

- **Ne pas désactiver SELinux** ni `firewalld` pour faire taire le
  problème — le service ne fonctionne pas pour une raison précise.
- **Ne pas `chmod 777`** sur les fichiers de config système. Le bon
  mode est `0644`, owner `root:root`.
- **Le `systemctl restart`** suffit (pas besoin de `daemon-reload`
  ici : tu modifies la config applicative, pas l'unit file).
- **`enabled` est différent de `active`** : un service peut être
  `active` mais pas `enabled` (il ne redémarrera pas après reboot).

## 🚀 Lancement

Tu es déjà sur la VM si tu viens de faire `dsoxlab run`. Sinon :

```bash
dsoxlab ssh alma-rhcsa-1
```

## 🧪 Validation automatisée

Quand tu penses avoir résolu le problème (depuis ton hôte, pas depuis
la VM) :

```bash
dsoxlab check depanner-service-crash-loop
```

Le test vérifie sur la VM cible :

- Le fichier `/etc/demo-crashloop/config.yml` existe avec mode `0644`
  et `root:root`.
- Il contient bien une ligne `port: <numéro>`.
- `systemctl is-active demo-crashloop.service` retourne `active`.
- `systemctl is-enabled demo-crashloop.service` retourne `enabled`
  (critère persistence_after_reboot RHCSA).
- Le journal récent ne contient plus le pattern de l'erreur initiale.

## 🧹 Reset

Si tu veux recommencer le diagnostic depuis zéro :

```bash
dsoxlab reset depanner-service-crash-loop
```

Cela rejoue `cleanup.yaml` puis `setup.yaml` — la VM revient à l'état
de crash loop initial, prête pour un nouveau diagnostic.

## 💡 Pour aller plus loin

- **`systemctl status` codes de sortie** : 0 si le service est
  `active`, 3 sinon. Utile pour un script de monitoring.
- **`systemd-analyze verify <unit-file>`** : détecte les unit files
  syntaxiquement invalides AVANT d'essayer de les charger.
- **`journalctl --rotate`** + `--vacuum-time=1d` : rotation manuelle
  utile quand un crash loop a saturé `/var/log/journal/` pendant la
  nuit.
- **Drop-in d'override** dans `/etc/systemd/system/<svc>.d/override.conf`
  pour modifier `Restart=`, `RestartSec=`, `ExecStartPre=` sans
  toucher à l'unit principal.

## 🤔 Questions de réflexion

1. Si tu trouvais ce service en crash loop sur **3 serveurs identiques**
   en parallèle (production), quelle stratégie ? Tu corriges en local
   sur chacun, ou tu rédiges un playbook Ansible ?

2. Comment **prévenir** ce crash loop en amont ? (Indices :
   `validate=` dans Ansible, `systemd-analyze verify`, dépendance
   déclarée `Requires=` ou `ConditionPathExists=` dans l'unit.)

3. Si le service redémarrait correctement mais sortait au bout de
   30 minutes (au lieu d'instantanément), comment adapterais-tu ton
   diagnostic ? Quels outils en plus (`coredumpctl`,
   `systemd-analyze blame`) ?
