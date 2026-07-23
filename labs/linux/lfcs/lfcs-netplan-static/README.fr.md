# Lab — IP statique & route avec netplan

## Rappel

[**netplan sur le guide compagnon**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/netplan/)

netplan décrit le réseau dans `/etc/netplan/*.yaml`. Un device reçoit
`addresses:` pour les IP statiques et `routes:` (`to:`/`via:`) pour les routes
statiques. `netplan generate` traduit sans rien activer, `netplan try` applique
avec retour arrière automatique, `netplan apply` applique sans filet (persistant
au boot dans les deux cas). Les fichiers de config doivent être en `0600`.

Travaille sur l'interface dédiée indiquée par l'énoncé, jamais sur l'interface de
gestion, celle qui porte ta route par défaut.

## Le cours

Les exemples ci-dessous travaillent sur une interface d'essai `atelier0`, un
fichier `/etc/netplan/70-atelier.yaml` et l'adresse `203.0.113.10/24` : le
challenge, lui, vous demandera une autre interface, un autre fichier et d'autres
adresses. Apprenez la méthode, ne recopiez pas une ligne. Toutes les sorties
viennent d'une VM **Ubuntu 24.04.4 LTS** (noyau **6.8.0-134-generic**) avec
**netplan.io 1.1.2-8ubuntu1~24.04.2** et **systemd-networkd** comme backend ;
`203.0.113.0/24` est un préfixe réservé à la documentation.

> **C'est le sujet le plus dangereux du parcours.** netplan configure aussi
> l'interface qui porte votre session SSH. Une erreur appliquée avec
> `netplan apply` vous éjecte sans recours et impose un accès console. Tout ce
> cours se déroule donc sur une interface fabriquée pour l'occasion.

### D'abord : quelle interface porte votre session, et quel fichier la décrit

Deux commandes, dans cet ordre, avant d'ouvrir le moindre fichier. La première
dit par où sort votre trafic, la seconde dit quel fichier de `/etc/netplan/`
configure cette interface :

```bash
ip route get 1.1.1.1
sudo grep -l enp1s0 /etc/netplan/*.yaml
```

```text
1.1.1.1 via 10.10.30.1 dev enp1s0 src 10.10.30.19 uid 1001
    cache
/etc/netplan/50-cloud-init.yaml
```

`enp1s0` est l'interface de gestion, `50-cloud-init.yaml` le fichier
**intouchable** : posé par cloud-init, il désigne le lien par son adresse MAC
(`sudo netplan get ethernets` le montre) et lui donne `dhcp4: true`. Notez le
nom, `enp1s0` et pas `eth0` : les noms prévisibles d'Ubuntu dépendent du
matériel. Relevez toujours le vôtre avec `ip -br link`, ne recopiez pas celui
d'un tutoriel.

### Une interface jetable, et le YAML qui la décrit

Une interface `dummy` est une carte purement logicielle. netplan sait la déclarer
avec la famille `dummy-devices:`, et tout ce qui suit (`addresses`, `routes`,
`nameservers`) s'écrit **exactement** comme pour une vraie carte. C'est le
terrain d'apprentissage idéal : rien de ce qu'on y fait ne peut couper la
session.

```yaml title="/etc/netplan/70-atelier.yaml"
network:
  version: 2
  renderer: networkd
  dummy-devices:
    atelier0:
      mtu: 1400
      addresses:
        - 203.0.113.10/24
      routes:
        - to: 192.168.240.0/24
          via: 203.0.113.254
          metric: 200
      nameservers:
        addresses: [9.9.9.9]
```

Le préfixe `70-` place le fichier **après** `50-cloud-init.yaml` dans l'ordre de
lecture (voir plus bas). `version: 2` est le format netplan, `renderer` le
backend qui exécutera, et `routes:` avec `to:`/`via:` remplace le `gateway4:` des
vieux tutoriels, déprécié depuis netplan 0.103 selon le guide.

**Deux espaces par niveau, jamais de tabulation.** C'est l'échec numéro un du
sujet, et le message ne laisse aucun doute :

```text
/etc/netplan/70-atelier.yaml:7:1: Invalid YAML: tabs are not allowed for indent:
	- 203.0.113.10/24
^
```

Une indentation simplement irrégulière donne un message voisin,
`Invalid YAML: inconsistent indentation`. Dans les deux cas netplan donne le
fichier, la ligne et la colonne : lisez-le, il désigne l'erreur exacte.

**Les droits comptent.** Un fichier créé avec `tee` naît en `644`, et netplan
vous le reproche à chaque commande :

```text
** (generate:19679): WARNING **: Permissions for /etc/netplan/70-atelier.yaml
are too open. Netplan configuration should NOT be accessible by others.
```

Ce n'est pas de la coquetterie : un fichier netplan peut contenir un mot de passe
Wi-Fi **en clair** sous `access-points:`, et il révèle de toute façon votre plan
d'adressage à n'importe quel compte local. La correction, à faire par réflexe
après chaque création, est un `sudo chmod 600` sur le fichier. Attention,
l'avertissement n'est **qu'un avertissement** : `netplan generate` rend malgré
tout `0` et le fichier trop ouvert s'applique quand même. Les keyfiles de
NetworkManager, eux, sont purement et simplement refusés.

### Valider sans appliquer : `generate`, `get`, et le rendu sous `/run`

`netplan generate` traduit vos YAML en fichiers pour le backend, sans toucher au
réseau. Silence et code 0 valent validation :

```bash
sudo netplan generate ; echo "rc=$?"
sudo ls /run/systemd/network/ ; ip -br link show atelier0
```

```text
rc=0
10-netplan-atelier0.netdev
10-netplan-atelier0.network
10-netplan-enp1s0.link
10-netplan-enp1s0.network
Device "atelier0" does not exist.
```

Deux enseignements dans cette sortie. D'abord **netplan n'est qu'un
générateur** : il a produit un `.netdev` (créer la carte) et un `.network`
(l'adresser), et c'est systemd-networkd qui exécutera. Votre YAML est devenu de
l'INI, lisible avec `sudo cat /run/systemd/network/10-netplan-atelier0.network` :

```text
[Match]
Name=atelier0
[Network]
Address=203.0.113.10/24
DNS=9.9.9.9
[Route]
Destination=192.168.240.0/24
Gateway=203.0.113.254
Metric=200
```

Ensuite **`generate` n'applique rien** : l'interface n'existe toujours pas. Et
ces fichiers vivent sous `/run`, régénéré à chaque démarrage : ne les éditez
jamais, ils seront écrasés. La seule source de vérité est `/etc/netplan/`.
`sudo netplan get dummy-devices.atelier0` répond à l'autre question, celle de la
configuration **fusionnée** de tous vos fichiers.

### `netplan try` : le filet de 120 secondes

`netplan try` applique la configuration puis attend une confirmation au clavier.
Sans `Entrée` dans le délai, il **revient tout seul** en arrière : votre session
étant morte, vous ne confirmez rien, et la machine redevient joignable seule. Le
délai par défaut est de 120 secondes (`DEFAULT_INPUT_TIMEOUT = 120` dans le code
de la commande), réglable par `--timeout`.

```bash
sudo netplan try --timeout 20
```

```text
Do you want to keep these settings?

Press ENTER before the timeout to accept the new configuration

Changes will revert in 20 seconds [...] Changes will revert in  1 seconds
Reverting.
```

Pendant l'essai la configuration est réellement active ; après `Reverting.`,
l'adresse et la route ont disparu. Avec `Entrée`, la réponse est
`Configuration accepted.` et la configuration reste, déjà persistante. La
commande exige un vrai terminal, puisqu'elle lit votre clavier.

> **Trois limites du filet, mesurées sur cette machine.**
>
> - `netplan try` ne sauvegarde **pas** `/etc/netplan` mais le rendu,
>   c'est-à-dire `/run/systemd/network`. Après `Reverting.`, votre YAML est
>   toujours là, donc appliqué au prochain démarrage : un revert n'annule pas le
>   fichier.
> - Corollaire redoutable : si vous avez lancé `netplan generate` **avant** le
>   `try`, `/run` contient déjà la nouvelle configuration, la sauvegarde
>   photographie donc la nouvelle configuration, et le revert ne revient nulle
>   part. Deux essais identiques, seul `generate` les sépare : sans lui,
>   l'adresse a bien disparu après `Reverting.` ; avec lui, elle est encore là.
> - Une carte virtuelle déjà créée n'est détruite ni par le retour arrière ni
>   par `netplan apply` : elle perd ses adresses et garde sa coquille. Seul
>   `sudo ip link del atelier0` la fait disparaître.

La règle pratique qui en découle, à distance : **lancez `try` en premier**. Il
fait son `generate` lui-même et refuse un YAML invalide *avant* de toucher au
réseau, en rendant 78 (`EX_CONFIG`) :

```text
Invalid YAML: inconsistent indentation:
       routes: []
       ^
rc=78
```

Gardez `netplan generate` pour les machines dont vous tenez la console, ou
lancez-le **après** un `try` accepté. `netplan apply`, lui, n'a aucun mécanisme
d'annulation : réservez-le à la console locale ou à un changement trivial.

### L'ordre alphabétique, et ce que « fusionner » veut dire

Tous les `.yaml` de `/etc/netplan/` sont lus dans l'**ordre alphabétique** de
leurs noms, puis fusionnés. D'où les préfixes numériques. Ajoutons un second
fichier, lu après le nôtre, qui redéclare la même interface, et relisons la
fusion avec `sudo netplan get dummy-devices.atelier0` :

```yaml title="/etc/netplan/80-atelier-suite.yaml"
network:
  version: 2
  dummy-devices:
    atelier0:
      mtu: 1300
      addresses:
        - 203.0.113.60/24
```

```text
addresses:
- "203.0.113.10/24"
- "203.0.113.60/24"
mtu: 1300
[...]
```

Regardez bien : la fusion ne se comporte pas de la même façon selon le type de la
clé. Le scalaire `mtu` est **remplacé**, le dernier fichier lu gagne, 1300 écrase
1400. La liste `addresses` est **concaténée**, les deux adresses coexistent.
L'état réel après application le confirme, `ip -br addr show atelier0` donne
`203.0.113.10/24 203.0.113.60/24` et `ip -d link show atelier0` affiche
`mtu 1300`.

C'est la panne la plus déroutante du sujet : une configuration correcte,
appliquée sans erreur, et pourtant sans effet, parce qu'un fichier de nom
supérieur redéfinit la même clé. `netplan get` tranche en une commande, puisqu'il
montre le résultat après fusion et non ce que vous avez écrit.

### Les deux backends, et le monde d'en face

netplan ne configure rien lui-même, il génère la configuration d'un autre
service, désigné par `renderer` : **systemd-networkd** sur un serveur,
**NetworkManager** sur un poste de travail. Lequel tourne ici ?
`systemctl is-active systemd-networkd NetworkManager` répond `active` puis
`inactive`. Méfiez-vous de ce second mot : sur cette machine NetworkManager
n'est même pas installé, et `systemctl status NetworkManager` répond
`Unit NetworkManager.service could not be found.` La commande ne distingue pas
« installé mais arrêté » de « absent ». Déclarer un `renderer` vers un backend
absent est le piège classique, et il passe la validation :

```bash
sudo netplan generate ; echo "rc=$?"        # avec renderer: NetworkManager
sudo ls /run/systemd/network/ /run/NetworkManager/system-connections/
```

```text
rc=0
/run/systemd/network/:  10-netplan-enp1s0.link  10-netplan-enp1s0.network
/run/NetworkManager/system-connections/:  netplan-atelier0.nmconnection
```

`generate` valide la **syntaxe**, pas la **faisabilité** : il rend 0 sans un mot
et déplace simplement le rendu vers l'autre backend, au format INI. À
l'application, la sanction tombe (`Failed to start NetworkManager.service: Unit
NetworkManager.service not found.`, suivi d'une trace Python), l'interface perd
son adresse et `networkctl list` la déclare `unmanaged`. Alignez toujours le
`renderer` sur le service réellement actif.

Le tableau ci-dessous résume ce qui change quand on passe de la voie RHEL, vue
dans le lab NetworkManager, à la voie Ubuntu. C'est la comparaison à avoir en
tête en salle d'examen :

| | netplan (Ubuntu) | NetworkManager (RHEL) |
|---|---|---|
| Ce qu'on écrit | du YAML déclaratif dans `/etc/netplan/*.yaml` | des commandes `nmcli con add/mod` |
| Qui exécute | un backend généré : networkd ou NetworkManager | NetworkManager lui-même |
| Où vit la persistance | `/etc/netplan/*.yaml` en `0600` | `/etc/NetworkManager/system-connections/*.nmconnection` en `0600` |
| Droits trop ouverts | avertissement, le fichier s'applique quand même | fichier **refusé** au chargement |
| Filet à distance | `netplan try`, retour arrière automatique | aucun équivalent, `nmcli con up` applique sec |
| Rattrapage d'erreur | attendre l'expiration du délai | réactiver l'ancien profil, s'il reste joignable |
| Plusieurs fichiers | fusionnés par ordre alphabétique | un profil par connexion, pas de fusion |

Retenez surtout la ligne « filet » : c'est l'avantage décisif de netplan, et il
n'a pas d'équivalent côté `nmcli`, où une adresse mal saisie éjecte
instantanément.

### Persistance, dépannage et retour à l'état initial

La persistance ne se déduit pas, elle se vérifie. Après `sudo systemctl reboot`,
avec pour seule action l'écriture du fichier, `ip -br addr` et `ip route show` :

```text
enp1s0           UP             10.10.30.19/24 metric 100 [...]
atelier0         UNKNOWN        203.0.113.10/24 fe80::1c0a:a1ff:fe05:38b9/64
default via 10.10.30.1 dev enp1s0 proto dhcp src 10.10.30.19 metric 100
192.168.240.0/24 via 203.0.113.254 dev atelier0 proto static metric 200
203.0.113.0/24 dev atelier0 proto kernel scope link src 203.0.113.10
```

L'interface est revenue seule avec son adresse et sa route, et la route par
défaut n'a pas bougé. Notez la dernière ligne, `203.0.113.0/24 [...] scope link` :
elle est déduite du masque `/24`, personne ne l'a déclarée, et c'est elle qui
rend la passerelle `via` joignable ; une passerelle posée hors de ce réseau
donnerait une route absente. `sudo netplan status --diff` complète la
vérification en marquant les écarts entre l'état réel et vos fichiers.

| Symptôme | Cause probable | Correction |
|---|---|---|
| `Invalid YAML: tabs are not allowed for indent` | une tabulation dans le fichier | deux espaces par niveau, jamais de tabulation |
| `Invalid YAML: inconsistent indentation` | niveaux d'indentation irréguliers | réaligner sur la colonne indiquée |
| `Permissions ... are too open` | fichier créé en `644` | `sudo chmod 600 /etc/netplan/<fichier>.yaml` |
| Appliqué sans erreur, aucun effet | un fichier de nom supérieur redéfinit la clé | `sudo netplan get` pour lire la fusion |
| Interface `unmanaged`, sans adresse | `renderer` vers un backend absent | `systemctl is-active systemd-networkd NetworkManager` |
| `Reverting.` mais la config est toujours là | `netplan generate` lancé avant le `try` | relancer `try` seul, sans `generate` préalable |
| L'interface d'essai survit au retrait du fichier | `apply` ne détruit pas une carte virtuelle | `sudo ip link del <interface>` |
| Session perdue après un changement | `netplan apply` employé au lieu de `netplan try` | reprendre par la console, puis appliquer la règle |

Quand le tableau ne suffit pas, `journalctl -u systemd-networkd` et
`sudo netplan --debug apply` donnent l'étape fautive. Pour tout défaire, retirez
le fichier, appliquez, puis supprimez la carte : les deux gestes sont
nécessaires, `apply` ne fait que la désadresser.

```bash
sudo rm -f /etc/netplan/70-atelier.yaml /etc/netplan/80-atelier-suite.yaml
sudo netplan apply
sudo ip link del atelier0
ip -br addr ; sudo ls /run/systemd/network/ ; ip route get 1.1.1.1
```

```text
lo               UNKNOWN        127.0.0.1/8 ::1/128
enp1s0           UP             10.10.30.19/24 metric 100 fe80::5054:ff:fecd:18/64
10-netplan-enp1s0.link  10-netplan-enp1s0.network
1.1.1.1 via 10.10.30.1 dev enp1s0 src 10.10.30.19 uid 1001
```

Plus d'interface, plus de fichier généré, la session est intacte. Un dernier
réflexe, avant même la première ligne écrite : sauvegardez le répertoire avec
`sudo cp -a /etc/netplan /root/netplan.avant`, seul moyen de revenir à
l'identique quand plus rien ne s'explique.
