# Context — get a container running

Podman is installed and the image is already pulled. Run a container that stays
up in the background — the everyday Podman move: a named, detached container.

Your mission, on the VM:

1. Run a **detached** container named **`web`** from
   `registry.access.redhat.com/ubi9/ubi-micro`, kept alive with `sleep infinity`.
2. Confirm it is running (`podman ps`).

The point: `podman run -d --name web <image> <cmd>` starts a container in the
background; `podman ps` lists running containers; `podman inspect` reads their
state. This is the foundation the container-persistence lab builds on.

Method in the companion guide:
https://blog.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/
