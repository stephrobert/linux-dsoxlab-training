# Get an image, label it, ship it

## The situation

Containers start from images. The everyday image work: pull one from a registry,
give it a meaningful tag, and save it to a file you can move around or archive —
then inspect that archive to be sure of what's inside.

The point: an image first lives in a registry, then locally under one or more
names, then possibly in an archive you can carry around. Knowing how to move
between those forms, and how to read what an image contains without ever running
it, is the core of image management.

Method in the companion guide:
https://www.stephane-robert.info/docs/conteneurs/images-conteneurs/ (in French)

## What is asked

### Mission

Pull, tag, save and inspect a container image.

### Goal (expected state)

1. Image `localhost/rapport:v1` exists (pulled from the registry and tagged).
2. `/root/rapport.tar` is a saved image archive (`podman save`).
3. `skopeo inspect docker-archive:/root/rapport.tar` succeeds.

### Constraints

- Base image: `registry.access.redhat.com/ubi9/ubi-micro`.
- Validation reads Podman's image store and the archive with skopeo.

### Validation

```bash
dsoxlab check l4-podman-images
```
