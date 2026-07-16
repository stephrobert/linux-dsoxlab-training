# Challenge — l4-podman-basic

## Mission

Run a detached container named `web` and prove it's up.

## Goal (expected state)

1. A container named `web` exists.
2. It is running (`podman inspect -f '{{.State.Running}}' web` → `true`).
3. It runs the `ubi9/ubi-micro` image.

## Constraints

- Validation reads Podman's container state, not your shell history.

## Validation

```bash
dsoxlab check l4-podman-basic
```
