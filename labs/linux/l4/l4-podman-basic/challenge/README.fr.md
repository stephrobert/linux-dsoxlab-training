# Challenge — l4-podman-basic

## Mission

Lance un conteneur détaché nommé `web` et prouve qu'il tourne.

## Objectif (état attendu)

1. Un conteneur nommé `web` existe.
2. Il tourne (`podman inspect -f '{{.State.Running}}' web` → `true`).
3. Il utilise l'image `ubi9/ubi-micro`.

## Contraintes

- On lit l'état du conteneur via Podman, pas ton historique shell.

## Validation

```bash
dsoxlab check l4-podman-basic
```
