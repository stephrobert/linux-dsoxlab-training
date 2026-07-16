# Lab — manage container images with podman & skopeo

> Prepare: `dsoxlab provision` then `dsoxlab run l4-podman-images`

## Recap

[**Container images on the companion guide**](https://blog.stephane-robert.info/docs/conteneurs/images-conteneurs/)

`podman pull <ref>` fetches an image from a registry; `podman tag <src> <name>`
gives it a local name; `podman save -o <file> <name>` writes a portable archive;
`skopeo inspect docker-archive:<file>` reads an archive's metadata without running
it. `podman image exists <name>` checks presence.

## Objectives

- `localhost/rapport:v1` exists (pulled + tagged);
- `/root/rapport.tar` is a saved image archive;
- `skopeo inspect docker-archive:/root/rapport.tar` succeeds.

## Validate

```bash
dsoxlab check l4-podman-images
```
