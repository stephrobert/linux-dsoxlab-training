# Politique de sécurité

**Langue :** [English](./SECURITY.md) · [Français](./SECURITY.fr.md)

## Versions supportées

`linux-dsoxlab-training` est en développement actif. Les correctifs de sécurité
sont appliqués à la dernière version de la branche `main`.

| Version | Supportée |
| --- | --- |
| dernière (`main`) | ✅ |
| plus anciennes | ❌ |

## Signaler une vulnérabilité

**N'ouvrez pas d'issue publique pour une vulnérabilité de sécurité.**

Si vous pensez avoir trouvé une vulnérabilité, signalez-la en privé :

- De préférence : ouvrez un
  [avis de sécurité privé](https://github.com/stephrobert/linux-dsoxlab-training/security/advisories/new)
  sur GitHub.
- Sinon, utilisez les coordonnées publiées sur
  <https://blog.stephane-robert.info>.

Merci d'inclure :

- une description de la vulnérabilité et de son impact,
- les étapes pour la reproduire (commande, environnement, `dsoxlab --version`),
- tout log ou preuve de concept pertinent.

Nous vous tiendrons informé de l'avancement du correctif et vous créditerons dans
les notes de version si vous le souhaitez.

## Politique de divulgation

Nous pratiquons la divulgation coordonnée et nous engageons sur les délais
suivants, décomptés à partir de la réception de votre signalement :

| Étape | Délai visé |
| --- | --- |
| Accusé de réception de votre signalement | sous **48 heures** |
| Évaluation initiale et qualification de la sévérité | sous **5 jours** |
| Correctif publié, ou plan de remédiation écrit | sous **30 jours** |
| Divulgation publique de la vulnérabilité | sous **90 jours** |

Nous publions l'avis de sécurité dès qu'un correctif est disponible, ou au plus
tard à l'échéance des **90 jours**, selon ce qui arrive en premier. Si une
vulnérabilité est activement exploitée, nous pouvons la divulguer plus tôt pour
protéger les utilisateurs. Si un correctif complexe demande plus de temps, nous
vous prévenons avant l'échéance et convenons d'une nouvelle date avec vous,
plutôt que de la laisser expirer sans rien dire.

## Périmètre

Ce dépôt livre du **contenu de labs** (scénarios, tests, fixtures de mise en
place/nettoyage et de provisioning, clés SSH publiques) exécuté par la CLI
externe `dsoxlab`. Sont dans le périmètre : du matériel de lab dangereux ou
malveillant (setup/cleanup, tests, templates Terraform/cloud-init), une fuite de
secret, ou une clé privée commitée par erreur. Les vulnérabilités du moteur
`dsoxlab` lui-même relèvent de
[son propre dépôt](https://github.com/stephrobert/dsoxlab) ; les problèmes des
dépendances tierces doivent être signalés à leurs projets respectifs.
