# Contexte — mettre un répartiteur de charge devant le backend

Un backend web tourne sur un autre hôte et sert une page. Les requêtes ne doivent
pas l'atteindre directement : elles doivent passer par **HAProxy** sur cet hôte
frontal, qui fait reverse-proxy et répartit la charge vers le backend. Et ça doit
revenir après un reboot.

L'idée : HAProxy est un proxy applicatif (L7). Un `frontend` accepte les
connexions, un `backend` les transmet aux serveurs réels, et une politique de
répartition choisit lequel. À l'arrivée, une requête vers `http://localhost/` sur
cet hôte doit renvoyer la page du backend.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/services/reseau/haproxy/
