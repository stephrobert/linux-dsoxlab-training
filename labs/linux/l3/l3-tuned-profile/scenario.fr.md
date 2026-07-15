# Contexte — régler la machine pour le débit

Cette machine fait du batch intensif en données mais reste sur le profil tuned
**`balanced`** par défaut. Bascule-la sur un profil taillé pour le **débit**, pour
que les réglages noyau (gouverneur CPU, I/O, VM) soient prévus pour une charge
soutenue — et que ça survive à un reboot.

Ta mission, sur la VM :

1. Règle le profil tuned actif sur **`throughput-performance`**
   (`tuned-adm profile throughput-performance`).
2. Confirme avec `tuned-adm active`.

L'idée : `tuned` regroupe des dizaines de réglages noyau/sysfs dans des profils
nommés ; `tuned-adm list` les affiche, `tuned-adm profile <nom>` bascule, et le
choix est stocké (dans `/etc/tuned/active_profile`) pour tenir aux reboots.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/tuned/
