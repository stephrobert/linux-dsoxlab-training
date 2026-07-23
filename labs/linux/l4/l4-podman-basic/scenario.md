# Context — get a container running

Podman is installed and the image is already pulled. Run a container that stays
up in the background — the everyday Podman move: a named, detached container.

The point: a container runs either in the foreground or detached in the
background, and that second mode, with an explicit name, is the everyday one. Its
state is read from Podman, not from your shell history. This is the foundation
the container-persistence lab builds on.

Method in the companion guide:
https://blog.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/
