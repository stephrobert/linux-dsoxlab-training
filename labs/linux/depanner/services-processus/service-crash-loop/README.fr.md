# Lab — Diagnostiquer un service systemd en crash loop

> 💡 **Vous arrivez directement à ce lab sans avoir fait les précédents ?**
> Chaque lab de ce dépôt est **autonome**. Pré-requis unique : les 3 VMs
> du lab doivent être démarrées et accessibles en SSH avec sudo.
>
> ```bash
> cd /home/bob/Projets/linux-training
> make verify-conn   # → 3 hôtes répondent en SSH+sudo
> ```
>
> Si KO, lancez `make bootstrap && make provision` à la racine du repo.

## 🧠 Rappel

🔗 [**Diagnostiquer un service systemd en crash loop**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/services-processus/service-crash-loop/)

Un service `Restart=always` peut entrer en **crash loop** quand son
`ExecStart` échoue de manière reproductible : config absente, binaire
manquant, dépendance non démarrée, port occupé. Le diagnostic suit
toujours la même chaîne :

1. `systemctl status <svc>` → état + dernières lignes de log + sortie
   ExecStart.
2. `journalctl -u <svc> --since '1h ago'` → logs complets, on remonte
   le **premier** échec.
3. Hypothèse → vérification ciblée → correction → `daemon-reload` si
   l'unit a été modifié → `restart` → `is-active` + `is-enabled`.

C'est la **méthode** qui compte, pas la commande qui répare.

## 🎯 Objectifs

À la fin de ce lab, vous saurez :

- Identifier qu'un service est en **crash loop** (vs simplement arrêté
  ou en échec définitif).
- Lire un `systemctl status` pour distinguer **PID exit code**, **journal
  tail**, et **état du restart counter**.
- Remonter à la **cause racine** via `journalctl -u <svc>` (option `-b`,
  `--since`, `--no-pager`).
- Distinguer une correction **temporaire** (`systemctl restart`) d'une
  correction **durable** (qui survit au reboot — c'est le critère
  RHCSA `persistence_after_reboot`).
- Appliquer la règle : **`daemon-reload`** chaque fois qu'on touche au
  unit file.

## 🔧 Préparation

Le service en panne doit déjà être en place sur la VM cible. Côté
formateur, le posage est fait par `runtime/kvm.sh` (lancé par `dsoxlab
run` ou `make setup`).

Côté apprenant — `dsoxlab run` ouvre déjà ta session SSH sur la
VM cible. Si tu veux juste te reconnecter :

```bash
dsoxlab ssh alma-rhcsa-1
```

Une fois sur la VM, vérifie que le service est bien en crash loop :

```bash
systemctl is-active demo-crashloop.service
# Sortie attendue : "activating" ou "failed" (la boucle dure environ 2s
# entre chaque tentative).
```

## 📚 Exercice 1 — Confirmer le crash loop

Lancez :

```bash
sudo systemctl status demo-crashloop.service
```

**Sortie attendue** (extrait) :

```text
● demo-crashloop.service - Demo service stuck in crash loop (lab depanner/services-processus)
     Loaded: loaded (/etc/systemd/system/demo-crashloop.service; enabled; preset: disabled)
     Active: activating (auto-restart) (Result: exit-code) since ...; 1s ago
   Main PID: ... (code=exited, status=1/FAILURE)
   ...
```

### 🔍 Observation

Trois indices convergent :

- **`Active: activating (auto-restart)`** — le service **n'est pas
  stable** ; systemd est entre deux tentatives.
- **`Result: exit-code`** suivi d'un **`status=1/FAILURE`** — le binaire
  meurt avec un code de sortie non nul. Ce n'est pas un kill du système.
- Le **bloc « Main PID »** affiche un PID différent à chaque
  invocation (relancez la commande 2 fois pour le voir changer).

C'est la signature classique d'un crash loop. À partir de là, on cherche
**pourquoi** le binaire échoue.

## 📚 Exercice 2 — Trouver la cause racine

`systemctl status` n'affiche que les 10 dernières lignes du journal.
Pour la cause **première**, on remonte avec `journalctl` :

```bash
sudo journalctl -u demo-crashloop.service -b --no-pager | head -30
```

**Sortie attendue** (extrait) :

```text
... demo-crashloop[...]: FATAL: Configuration file not found: /etc/demo-crashloop/config.yml
... demo-crashloop[...]:        Service cannot start without configuration.
... systemd[1]: demo-crashloop.service: Main process exited, code=exited, status=1/FAILURE
... systemd[1]: demo-crashloop.service: Failed with result 'exit-code'.
... systemd[1]: demo-crashloop.service: Scheduled restart job, restart counter is at N.
```

### 🔍 Observation

Le **premier** message du démon dit tout : il cherche
`/etc/demo-crashloop/config.yml` qui n'existe pas. Inutile d'aller plus
loin avant d'avoir levé cette cause.

Vérifiez :

```bash
ls -la /etc/demo-crashloop/ 2>&1
# Sortie : "ls: cannot access '/etc/demo-crashloop/': No such file or directory"
```

## 📚 Exercice 3 — Lire l'unit file pour comprendre le contrat

Avant de créer le fichier de config, regardez ce que le binaire attend
exactement. L'unit file dit où est le binaire :

```bash
sudo systemctl cat demo-crashloop.service
```

Vous y voyez `ExecStart=/usr/local/bin/demo-crashloop`. Lisez ce
binaire :

```bash
sudo cat /usr/local/bin/demo-crashloop
```

Le script attend :

- Un fichier `/etc/demo-crashloop/config.yml`
- Une ligne `port: <numéro>` dedans (extraite par awk)
- Sinon il sort avec exit code 1 ou 2.

### 🔍 Observation

C'est typique d'une appli mal documentée : la doc d'erreur est dans le
code. Toujours lire le binaire/script du `ExecStart` quand `journalctl`
mentionne un fichier manquant.

## 📚 Exercice 4 — Corriger durablement

Trois étapes pour une correction **persistante** :

### 4.1 Créer le répertoire et le fichier de config

```bash
sudo mkdir -p /etc/demo-crashloop
sudo tee /etc/demo-crashloop/config.yml >/dev/null <<'EOF'
port: 8080
EOF
sudo chmod 0644 /etc/demo-crashloop/config.yml
sudo chown root:root /etc/demo-crashloop/config.yml
```

> **Sécurité** : `chmod 0644` quoté, `chown root:root` explicite. Cohérent
> avec la directive de sécurité par défaut du dépôt — un fichier de
> config ne doit jamais hériter du compte courant.

### 4.2 Relancer le service

```bash
sudo systemctl restart demo-crashloop.service
```

Pas besoin de `daemon-reload` ici (on n'a **pas** modifié l'unit file —
juste créé le fichier de config qu'il attendait).

### 4.3 Vérifier la persistance

```bash
sudo systemctl is-active demo-crashloop.service   # → active
sudo systemctl is-enabled demo-crashloop.service  # → enabled
sudo systemctl status demo-crashloop.service | head -5
```

### 🔍 Observation

- `is-active` doit retourner **`active`** (et non `activating` ou
  `failed`).
- `is-enabled` doit retourner **`enabled`** — c'est ce qui garantit que
  le service redémarrera après reboot. C'est le critère
  `persistence_after_reboot: true` validé par les tests.

## 🔍 Observations à noter

- **`Restart=always` masque les vraies erreurs** : un opérateur pressé
  voit juste « le service est UP par moments » et passe à autre chose.
  La méthode `journalctl --since '1h ago'` est non négociable.
- **La cause racine est toujours dans le PREMIER message d'erreur** —
  remonter le journal vers le haut, pas vers le bas.
- **`daemon-reload` après modification de l'unit, pas après modification
  de la config applicative** — c'est une distinction qui sert pour le
  RHCSA.
- **`is-active` + `is-enabled`** : les deux sont nécessaires pour la
  persistance reboot. Manquer `is-enabled` est l'erreur classique des
  débutants RHCSA.

## 🤔 Questions de réflexion

1. Si le service redémarrait correctement mais sortait au bout de
   30 minutes (au lieu d'instantanément), comment adapteriez-vous votre
   diagnostic ? Quels outils en plus (par exemple, `coredumpctl` ou
   `systemd-analyze blame`) ?

2. Vous trouvez le service en crash loop sur **3 serveurs identiques**
   en parallèle. Quelle stratégie de remédiation (en local vs en
   automation Ansible) ? Que faut-il documenter avant de toucher à
   quoi que ce soit ?

3. Comment auriez-vous **prévenu** ce crash loop ? (Indices : `validate=`
   dans Ansible, `systemd-analyze verify`, dépendance déclarée
   `Requires=` ou `ConditionPathExists=` dans l'unit.)

## 🚀 Challenge final

Voir [`challenge/README.md`](challenge/README.md). Le challenge te
demande de **diagnostiquer et corriger** le service en crash loop sur
la VM cible — directement à la ligne de commande, sans script. La
validation par `dsoxlab check` lance des tests pytest+testinfra qui
vérifient l'état final de la VM.

## 💡 Pour aller plus loin

- **`coredumpctl list`** + `coredumpctl info <pid>` : pour les services
  qui crashent avec un signal (SIGSEGV, SIGABRT) plutôt qu'un exit code.
- **`systemd-analyze blame`** + `critical-chain` : pour identifier les
  services qui ralentissent le boot (utile pour la sous-section
  `depanner/demarrage/`).
- **Drop-in d'override** dans `/etc/systemd/system/<svc>.d/override.conf`
  pour modifier `Restart`, `RestartSec`, ou `ExecStartPre` sans
  toucher à l'unit principal.
- **`journalctl -p err -b -u <svc>`** filtre par priorité (warning, err,
  alert, crit) — gain de temps quand le service est verbeux.
