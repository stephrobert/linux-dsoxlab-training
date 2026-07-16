# Context — get an image, label it, ship it

Containers start from images. The everyday image work: pull one from a registry,
give it a meaningful tag, and save it to a file you can move around or archive —
then inspect that archive to be sure of what's inside.

Your mission, on the VM:

1. **Pull** `registry.access.redhat.com/ubi9/ubi-micro` (`podman pull`).
2. **Tag** it as **`localhost/rapport:v1`** (`podman tag`).
3. **Save** the tagged image to **`/root/rapport.tar`**
   (`podman save -o /root/rapport.tar localhost/rapport:v1`).
4. **Inspect** the archive with skopeo:
   `skopeo inspect docker-archive:/root/rapport.tar`.

The point: `podman pull` fetches from a registry, `podman tag` gives an image a
local name, `podman save` writes it to a portable archive, and `skopeo inspect`
reads an image (registry or archive) without running it — the core of image
management.

Method in the companion guide:
https://blog.stephane-robert.info/docs/conteneurs/images-conteneurs/
