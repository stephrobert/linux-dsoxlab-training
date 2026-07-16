# Contexte — l'interface est configurée mais morte

Une connexion nommée `lab-net` existe sur l'interface `lab1` avec une adresse
statique correcte, pourtant l'interface ne porte aucune IP et elle ne reviendra
pas après un reboot. Quelque chose cloche dans son état — trouve-le et ranime le
lien.

Ta mission, sur la VM (travaille sur `lab1`, **ne touche jamais à `enp5s0`** —
gestion) :

1. **Diagnostique** pourquoi `lab-net` est morte (`nmcli con show lab-net`,
   `nmcli device`, `ip addr show lab1`). Elle est configurée mais inactive.
2. **Active-la** (`nmcli con up lab-net`).
3. Rends-la **auto-connectable** pour qu'elle survive au reboot
   (`nmcli con mod lab-net connection.autoconnect yes`).

L'idée : une connexion peut être entièrement configurée et pourtant **inactive**,
et une avec `autoconnect no` ne reviendra pas au boot — les deux pannes que tu
dois lire dans la sortie de `nmcli`, pas deviner.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/diagnostic/
