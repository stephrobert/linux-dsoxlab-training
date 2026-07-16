# Lab — run a detached container with Podman

> Prepare: `dsoxlab provision` then `dsoxlab run l4-podman-basic`

## Recap

[**Podman on the companion guide**](https://blog.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/)

`podman run -d --name <name> <image> <cmd>` runs a detached container.
`podman ps` lists running containers; `podman inspect -f '{{.State.Running}}'`
reads whether one is up. `podman rm -f` removes it.

## Objectives

- a container named `web` exists;
- it is **running** (`State.Running` = true);
- it uses the `ubi9/ubi-micro` image.

## Validate

```bash
dsoxlab check l4-podman-basic
```
