# Challenge — l4-podman-images

## Mission

Pull, tag, save and inspect a container image.

## Goal (expected state)

1. Image `localhost/rapport:v1` exists (pulled from the registry and tagged).
2. `/root/rapport.tar` is a saved image archive (`podman save`).
3. `skopeo inspect docker-archive:/root/rapport.tar` succeeds.

## Constraints

- Base image: `registry.access.redhat.com/ubi9/ubi-micro`.
- Validation reads Podman's image store and the archive with skopeo.

## Validation

```bash
dsoxlab check l4-podman-images
```
