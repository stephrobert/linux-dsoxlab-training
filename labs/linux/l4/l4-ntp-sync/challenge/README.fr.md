# Remettre l'horloge à l'heure

## La situation

Cette machine a dérivé : mauvais fuseau, NTP désactivé et `chronyd` même pas
démarré. Les journaux affichent des horodatages incohérents et les poignées de
main TLS échouent quand l'horloge est fausse. Remets-la d'aplomb, et fais en
sorte que ça tienne après un reboot.

L'idée : le fuseau n'est qu'une convention d'affichage, il ne déplace pas
l'instant. L'enjeu est ailleurs, dans une question qui se pose au redémarrage
autant que maintenant : cette machine tient-elle son horloge par le réseau ?
C'est cet état durable qui sera vérifié, pas les commandes que tu auras tapées.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/services/reseau/chrony/

## Ce qui est demandé

### Mission

L'horloge est désynchronisée : mauvais fuseau, NTP désactivé, `chronyd` arrêté.
Remets-la d'aplomb et fais-la persister.

### Objectif (état attendu)

1. Le fuseau est `Europe/Paris`.
2. Le NTP est activé (`timedatectl show -p NTP --value` → `yes`).
3. `chronyd` **tourne et est activé**.

### Contraintes

- La persistance compte : un `chronyd` qui tourne sans être `enabled` échoue à la
  validation. On lit l'état **actif** du service et `timedatectl`, pas ton
  historique.

### Validation

```bash
dsoxlab check l4-ntp-sync
```
