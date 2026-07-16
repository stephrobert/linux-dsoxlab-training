# Contexte — faire de cette machine une passerelle NAT

Cette machine doit router le trafic : les connexions entrantes sur **`tcp/8080`**
doivent être envoyées vers un backend en **`192.0.2.20:80`**, avec l'adresse
source masquée pour que les réponses reviennent. Et ça doit tenir après un reboot
— une règle NAT qui disparaît au redémarrage est pire que rien.

Ta mission, sur la VM :

1. **Active le routage IP**, de façon persistante : `net.ipv4.ip_forward = 1`
   dans `/etc/sysctl.d/` (le préalable absolu — sans routage, aucune règle NAT ne
   s'applique), puis `sysctl --system`.
2. Crée une **table `nat` nftables** `lab-nat` :
   - `prerouting` (`type nat hook prerouting priority dstnat`) :
     `tcp dport 8080 dnat to 192.0.2.20:80` ;
   - `postrouting` (`type nat hook postrouting priority srcnat`) :
     `ip daddr 192.0.2.20 masquerade`.
3. **Rends-la persistante** : sauvegarde la table dans `/etc/nftables/lab-nat.nft`,
   `include`-la dans `/etc/sysconfig/nftables.conf`, et `systemctl enable --now
   nftables`.

L'idée : `ip_forward=1` est le préalable ; nftables fait le DNAT (redirection de
port) en `prerouting` et le `masquerade` (SNAT) en `postrouting` ; et sur RHEL la
persistance passe par `/etc/sysconfig/nftables.conf` + le service `nftables`
activé, pas un `nft add` volatile perdu au reboot.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/securiser/reseaux/nat-port-forwarding/
