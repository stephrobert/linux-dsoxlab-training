# Faire de cette machine une passerelle NAT

## La situation

Cette machine doit router le trafic : les connexions entrantes sur **`tcp/8080`**
doivent être envoyées vers un backend en **`192.0.2.20:80`**, avec l'adresse
source masquée pour que les réponses reviennent. Et ça doit tenir après un
reboot : une règle NAT qui disparaît au redémarrage est pire que rien.

L'idée : router du trafic pour le compte d'autrui n'est pas le comportement par
défaut du noyau, il faut l'autoriser. Rediriger un port et masquer l'adresse
source sont ensuite deux traitements distincts, à deux moments différents du
parcours d'un paquet. Enfin, une règle nftables posée à chaud meurt au reboot :
la persistance se configure ailleurs.

Méthode dans le guide compagnon :
https://www.stephane-robert.info/docs/securiser/reseaux/nat-port-forwarding/

## Ce qui est demandé

### Mission

Fais de cette machine une passerelle NAT : redirige le `tcp/8080` vers
`192.0.2.20:80` avec masquerade, de façon persistante.

### Objectif (état attendu)

1. `net.ipv4.ip_forward` = `1` (actif) et déclaré dans `/etc/sysctl.d/`.
2. Le ruleset nftables a `tcp dport 8080 dnat to 192.0.2.20:80` (prerouting) et
   `192.0.2.20 masquerade` (postrouting).
3. Ça survit au reboot : `nftables.service` activé + les règles `include`es dans
   `/etc/sysconfig/nftables.conf`.

### Contraintes

- `ip_forward` est le préalable — une règle NAT sans lui ne fait rien.
- Un `nft add` volatile est perdu au reboot : persiste via la config RHEL.
- On lit sysctl, le ruleset nft et les fichiers de persistance.

### Validation

```bash
dsoxlab check l4-nat-portforward
```
