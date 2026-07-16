# Contexte — mettre un répartiteur de charge devant le backend

Un backend web tourne sur un autre hôte et sert une page. Les requêtes ne doivent
pas l'atteindre directement — elles doivent passer par **HAProxy** sur cet hôte
frontal, qui fait reverse-proxy et répartit la charge vers le backend. Et ça doit
revenir après un reboot.

Ta mission, sur la VM frontale (l'IP du backend est dans `/root/lb-backend.env`) :

1. Configure **`/etc/haproxy/haproxy.cfg`** :
   - un `frontend` qui écoute sur `*:80` ;
   - un `backend` (`balance roundrobin`) avec une ligne `server` pointant l'hôte
     backend sur le port 80.
2. **Valide** la conf : `haproxy -c -f /etc/haproxy/haproxy.cfg`.
3. **Active et démarre** `haproxy`.

L'idée : HAProxy est un proxy applicatif (L7) — le `frontend` accepte les
connexions et le `backend` les transmet aux serveurs réels, `balance` répartissant
entre eux. `haproxy -c` détecte les erreurs de conf avant qu'elles ne coupent le
service. Une requête vers `http://localhost/` sur cet hôte doit renvoyer la page
du backend.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/services/reseau/haproxy/
