# Contexte — remettre l'horloge à l'heure

Cette machine a dérivé : mauvais fuseau, NTP désactivé et `chronyd` même pas
démarré. Les journaux affichent des horodatages incohérents et les poignées de
main TLS échouent quand l'horloge est fausse. Remets-la d'aplomb — et fais en
sorte que ça tienne après un reboot.

Ta mission, sur la VM :

1. Règle le fuseau sur **`Europe/Paris`** (`timedatectl set-timezone`).
2. Active le **NTP** (`timedatectl set-ntp true`).
3. **Active et démarre** `chronyd` pour qu'il survive au reboot
   (`systemctl enable --now chronyd`).

L'idée : `chronyd` est le client NTP sur RHEL ; `timedatectl` pilote le fuseau et
l'interrupteur NTP. Un service qui tourne maintenant mais n'est pas `enabled`
disparaît au prochain reboot — le piège classique du RHCSA.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/services/reseau/chrony/
