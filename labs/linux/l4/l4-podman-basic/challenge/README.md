# Get a container running

## The situation

Podman is installed and the image is already pulled. Run a container that stays
up in the background — the everyday Podman move: a named, detached container.

The point: a container runs either in the foreground or detached in the
background, and that second mode, with an explicit name, is the everyday one. Its
state is read from Podman, not from your shell history. This is the foundation
the container-persistence lab builds on.

Method in the companion guide:
https://www.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/ (in French)

## What is asked

### Mission

Run a detached container named `web` and prove it's up.

### Goal (expected state)

1. A container named `web` exists.
2. It is running (`podman inspect -f '{{.State.Running}}' web` → `true`).
3. It runs the `ubi9/ubi-micro` image.

### Constraints

- Validation reads Podman's container state, not your shell history.

### Validation

```bash
dsoxlab check l4-podman-basic
```
