# Contexte — le pare-feu Debian : ufw

Sur Debian/Ubuntu, la façade conviviale du pare-feu est **`ufw`** (Uncomplicated
FireWall). Un service web doit être joignable, tu vas donc ouvrir `http` et
activer le pare-feu — tout en gardant ton accès SSH.

Ta mission, sur la VM Ubuntu :

1. Autorise le service **`http`** : `sudo ufw allow http` (ou `ufw allow 80/tcp`).
2. **Active** le pare-feu : `sudo ufw enable`.
3. **Ne retire jamais `OpenSSH`** — il est déjà autorisé ; garde-le pour ne pas te
   verrouiller dehors.

L'idée : `ufw allow <service|port>` ajoute une règle, `ufw enable` active le
pare-feu (et le fait démarrer au boot), `ufw status` liste les règles. C'est le
pendant Debian de `firewall-cmd` — même idée, syntaxe plus simple.

Méthode dans le guide compagnon :
https://blog.stephane-robert.info/docs/securiser/reseaux/ufw/
