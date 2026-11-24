# SELinux, et ce qui ne survit pas

## La situation

Le réflexe qui fait échouer les candidats RHCSA : basculer SELinux en enforcing
à la volée, et passer à la suite. Ça marche, jusqu'au reboot. Même histoire avec
un contexte de fichier posé à la main : le service démarre, tout va bien, et la
première relabellisation l'efface.

SELinux a un **runtime** et une **policy**. Ce que tu changes au runtime est
temporaire, ce que tu écris dans la policy survit. Chaque tâche de ce drill est
bâtie sur cette distinction.

Ce drill est un **chrono** : 4 tâches, 20 minutes, aucun indice. RHCSA
uniquement ; Debian a AppArmor, un modèle entièrement différent, travaillé dans
`drill-apparmor`.

Lis le sujet : `dsoxlab challenge drill-selinux`.

## Drill — SELinux

**Format** : 4 tâches, 100 points, 20 minutes. **Aucun indice.**

```bash
dsoxlab check drill-selinux
```

SELinux est en **permissive**, un contexte est faux, un booléen est éteint.

---

### Tâche 1 — Enforcing, pour de bon (25 pts)

SELinux doit être en **enforcing maintenant**, et l'être encore après un
**reboot**.

### Tâche 2 — Le bon contexte (25 pts)

`/srv/web/index.html` doit porter le contexte **`httpd_sys_content_t`** — et le
**conserver après une relabellisation**.

### Tâche 3 — Le booléen (25 pts)

**`httpd_can_network_connect`** doit être **on**, et le rester après un reboot.

### Tâche 4 — Un port non standard (25 pts)

Le port **`8888/tcp`** doit porter le label **`http_port_t`**, pour qu'un service
web puisse s'y attacher.

---

**Tes contextes sont vérifiés après une relabellisation.** Ce que la policy ne
connaît pas n'y survit pas.

## Valider

```bash
dsoxlab check drill-selinux
```
