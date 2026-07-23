# Lab — manage container images with podman & skopeo

## Reminder

[**Container images on the companion guide**](https://blog.stephane-robert.info/docs/conteneurs/images-conteneurs/)

`podman pull <ref>` fetches an image from a registry; `podman tag <src>
<name>` gives it a local name; `podman save -o <file> <name>` writes a portable
archive; `skopeo inspect docker-archive:<file>` reads an archive's metadata
without running it. `podman image exists <name>` checks presence.

## The course

The examples below build a `localhost/inventaire` image from
`registry.access.redhat.com/ubi9/ubi-minimal:9.6`, in an `~/atelier-image`
directory: the challenge starts from another image and asks for other actions.
The goal is to understand what an image is, not to copy a line. Every output
comes from an **AlmaLinux 10.2** VM running **Podman 5.8.2**, under an ordinary
account (rootless).

Rootless mode, the UID shift and the container life cycle are covered in the
`l4-podman-basic` lab: here we only talk about images.

### Writing a Containerfile and measuring what it produces

On a minimal AlmaLinux, Podman is not installed: `sudo dnf -y install podman`
pulls 16 packages (`crun`, `conmon`, `netavark`, `containers-common`…). Second
reflex before writing anything: here `/etc/containers/registries.conf` queries
**the Red Hat registries before Docker Hub**, in
`short-name-mode = "enforcing"`. So always write your images in full, registry
and tag included.

A `Containerfile` is a text file: one instruction per line, executed in order.
`FROM` picks the base image, `RUN` runs a command, `COPY` pours a file from the
build directory into the image, `LABEL` adds metadata and `CMD` sets the command
run by default.

```bash
mkdir ~/atelier-image && cd ~/atelier-image
printf 'ref;libelle\nA-100;vanne 3 pouces\nA-220;joint torique\n' > catalogue.txt
cat > Containerfile <<'EOF'
FROM registry.access.redhat.com/ubi9/ubi-minimal:9.6
LABEL org.opencontainers.image.title="inventaire"
RUN microdnf install -y findutils && microdnf clean all
COPY catalogue.txt /opt/inventaire/catalogue.txt
CMD ["cat", "/opt/inventaire/catalogue.txt"]
EOF
podman build -t localhost/inventaire:0.1 .
```

The trailing dot (`.`) is not decorative: it is the **build context**, the
directory from which `COPY` is allowed to read. The output announces each step,
and an identifier after each of them:

```text
STEP 1/5: FROM registry.access.redhat.com/ubi9/ubi-minimal:9.6
Trying to pull registry.access.redhat.com/ubi9/ubi-minimal:9.6...
[...]
STEP 3/5: RUN microdnf install -y findutils && microdnf clean all
[...]
--> 95fa94c7ade0
STEP 4/5: COPY catalogue.txt /opt/inventaire/catalogue.txt
--> c53008494027
STEP 5/5: CMD ["cat", "/opt/inventaire/catalogue.txt"]
COMMIT localhost/inventaire:0.1
--> bc5f1ccfccc4
```

Each `-->` is an intermediate image, reusable. The result can be measured:

```text
REPOSITORY                                   TAG   IMAGE ID      SIZE
localhost/inventaire                         0.1   bc5f1ccfccc4  121 MB
registry.access.redhat.com/ubi9/ubi-minimal  9.6   a2c5a85865a5  106 MB
```

106 MB for the base, 121 MB on arrival: the installed package and the catalogue
weigh 15 MB. A `podman run --rm localhost/inventaire:0.1` does display the
catalogue, without having to specify the command: that is the `CMD`.

### The build cache, and the order that preserves it

Run the same build again without changing anything:

```text
STEP 3/5: RUN microdnf install -y findutils && microdnf clean all
--> Using cache 95fa94c7ade03223914ff23462af010347a5bcc79013a9fa5c91d61fa9da1be2
STEP 4/5: COPY catalogue.txt /opt/inventaire/catalogue.txt
--> Using cache c53008494027ad796e9f5ff8ed56b1c23617772e5102eb80f0e73ddc27b31613
```

`Using cache` at each step, and **0.32 s** instead of the 12.7 s of the first
time, download of the base image included. Now add a line to `catalogue.txt` and
rebuild:

```text
STEP 3/5: RUN microdnf install -y findutils && microdnf clean all
--> Using cache 95fa94c7ade0[...]
STEP 4/5: COPY catalogue.txt /opt/inventaire/catalogue.txt
--> 196d41c74ed8
```

The `RUN` stays cached, the `COPY` is replayed: Podman compares the content of
the copied file, not its date. And **everything that follows an invalidated step
is replayed**, even if the text of the instruction has not moved.

Hence the importance of order. Let us write a second, identical Containerfile,
but with the `COPY` placed **before** the `RUN`. One line added to the
catalogue, then the two versions rebuilt one after the other, twice in a row:

| Order | 1st measurement | 2nd measurement | What is replayed |
|---|---|---|---|
| `RUN` then `COPY` | 0.550 s | 0.619 s | `COPY` only |
| `COPY` then `RUN` | 2.300 s | 2.480 s | `COPY` **and** the installation |

Four times slower for a single 563 kB package. With a real set of dependencies,
the gap is counted in minutes at each change of the code. The rule fits in one
sentence: **what changes rarely at the top, what changes often at the bottom.**

### Reading an image: `podman history` and `podman inspect`

`podman history` unrolls the instructions, from the last to the first, with what
each of them added:

```bash
podman history --format 'table {{.Size}}\t{{.CreatedBy}}' localhost/inventaire:0.4
```

```text
SIZE        CREATED BY
0B          /bin/sh -c #(nop) CMD ["cat", "/opt/invent...
3.07kB      /bin/sh -c #(nop) COPY file:249809c51d33da...
14.9MB      /bin/sh -c microdnf install -y findutils &...
0B          /bin/sh -c #(nop) LABEL org.opencontainers...
106MB       /bin/sh -c #(nop) LABEL "architecture"="x8...
[...]
```

Only three lines weigh anything: 106 MB for the base, 14.9 MB for the
installation, 3 kB for the copied file. Total 121 MB, which
`podman inspect -f '{{.Size}}'` confirms: `120954487`. The `LABEL`s and the
`CMD` are at `0B`: they do not touch the file system, they only write metadata.
The `#(nop)` mention indicates, by the way, that no command was run.

Do not confuse the number of instructions with the number of layers:
`podman history -q ... | wc -l` counts **23** lines when
`podman inspect -f '{{len .RootFS.Layers}}'` answers **3**. Only `FROM`, `RUN`,
`COPY` and `ADD` create a file layer.

Where `history` tells the story of the build, `inspect` gives the final state.
Without an option it returns a complete JSON; `-f` extracts a field from it, and
that is the form you use in a script:

```bash
podman inspect -f '{{.Config.Cmd}}' localhost/inventaire:0.4
podman inspect -f '{{index .Config.Labels "org.opencontainers.image.title"}}' localhost/inventaire:0.4
podman inspect -f '{{.Architecture}}/{{.Os}}' localhost/inventaire:0.4
```

```text
[cat /opt/inventaire/catalogue.txt]
inventaire
amd64/linux
```

### What is written stays written

Here is the most expensive trap of the subject. Two Containerfiles starting from
the same `FROM registry.access.redhat.com/ubi9/ubi-minimal:9.6` build a 40 MiB
file then erase it, one in two `RUN`s, the other in a single one:

```dockerfile
# the "separee" version
RUN dd if=/dev/urandom of=/opt/archive.bin bs=1M count=40 status=none
RUN rm -f /opt/archive.bin

# the "groupee" version
RUN dd if=/dev/urandom of=/opt/archive.bin bs=1M count=40 status=none \
 && rm -f /opt/archive.bin
```

In both images, the file really is absent:

```text
$ podman run --rm localhost/purge:separee ls -l /opt/archive.bin
ls: cannot access '/opt/archive.bin': No such file or directory
```

And yet:

```text
REPOSITORY:TAG                                   SIZE
localhost/purge:separee                          148 MB
localhost/purge:groupee                          106 MB
```

**42 MB of difference for a file nobody can read any more.** The `history` of
the two-`RUN` version shows it plainly:

```text
SIZE        CREATED BY
2.05kB      /bin/sh -c rm -f /opt/archive.bin
41.9MB      /bin/sh -c dd if=/dev/urandom of=/opt/arch...
```

The layer of the `rm` only records a *deletion*; the layer below still contains
the 42 MB. A layer is immutable: you can only stack on top of it. Hence the
rule: **you create and you clean up in the same `RUN`.**

When the large file is indispensable to the build but useless on arrival, a
multi-stage build solves the problem: a first `FROM` does the dirty work, a
second one starts from scratch and only copies the result.

```dockerfile
FROM registry.access.redhat.com/ubi9/ubi-minimal:9.6 AS travail
RUN dd if=/dev/urandom of=/opt/archive.bin bs=1M count=40 status=none
RUN sha256sum /opt/archive.bin > /opt/empreinte.txt

FROM registry.access.redhat.com/ubi9/ubi-minimal:9.6
COPY --from=travail /opt/empreinte.txt /opt/empreinte.txt
```

The final image weighs **106 MB**, the size of the base, and does contain the
checksum computed over the 42 MB. The companion guide details this technique and
the other ways of making an image lighter.

### Tagging: `podman tag`, `latest` and the `<none>` images

`podman tag` copies nothing at all: it adds a name that points to the same
image.

```bash
podman tag localhost/inventaire:0.4 localhost/inventaire:latest
podman tag localhost/inventaire:0.4 registry.exemple.lan/atelier/inventaire:stable
```

```text
REPOSITORY                               TAG      IMAGE ID      SIZE
registry.exemple.lan/atelier/inventaire  stable   0fb0af1ab155  121 MB
localhost/inventaire                     latest   0fb0af1ab155  121 MB
localhost/inventaire                     0.4      0fb0af1ab155  121 MB
```

**Three lines, a single `IMAGE ID`, and 121 MB displayed three times.** The
`SIZE` column is therefore not additive: at that moment, seven names were
displaying 121 MB each, that is 847 MB if you added them up, while
`podman system df` announced **222.6 MB** for the whole store. Common layers are
only stored once. `podman rmi` on one of the names only removes the name:

```text
Untagged: registry.exemple.lan/atelier/inventaire:stable
```

The prefix matters: `localhost/` designates a local image, never published;
`registry.exemple.lan/atelier/…` is the name you will need for a `podman push`.
As for `latest`, it is **not** "the latest version", only the implicit tag when
you specify none. Proof on the machine, after rebuilding `0.4` without touching
`latest`:

```text
REPOSITORY            TAG      IMAGE ID      CREATED
localhost/inventaire  0.4      09f03c2f59f3  17 seconds ago
localhost/inventaire  latest   0fb0af1ab155  49 seconds ago
```

`latest` is **older** than `0.4`. Nothing updates it on its own.

And the image that carried `0.4` before the rebuild? It has not disappeared: it
has lost its name.

```text
$ podman images --filter dangling=true --format 'table {{.ID}}\t{{.Size}}'
IMAGE ID      SIZE
d756ef94e0c4  148 MB
bc5f1ccfccc4  121 MB
[...]
```

These are the `<none>` images of `podman images`, called *dangling*. They occupy
the disk like the others: here, `podman image prune -f` removed fourteen of them
and brought the store down from **222.7 MB to 178 MB**.

### What stays on the disk

`podman system df` is the only honest view of the occupancy. With a container in
the middle of writing 20 MB into its file system:

```text
TYPE           TOTAL       ACTIVE      SIZE        RECLAIMABLE
Images         20          1           178MB       178MB (100%)
Containers     1           1           20.98MB     0B (0%)
```

The container owns its own writable layer, counted separately from the image. As
long as it exists, the image stays attached to it:

```text
Error: image used by 8ee48969ad21[...]: image is in use by a container:
consider listing external containers and force-removing image
```

Delete the container: the `Containers` line falls back to `0B`, its 20.98 MB
layer goes with it, **but the 178 MB of images stay unchanged**. Deleting a
container never frees the image it came from, it only frees the image from its
hold.

Two cleanups remain, not to be confused:

| Command | What it deletes |
|---|---|
| `podman image prune -f` | only the **nameless** images (`<none>`) |
| `podman image prune -a -f` | **every** image no container is using |

On the state above, `prune -f` no longer returns anything (there is no `<none>`
left) while `prune -a -f` deletes the twenty images: `podman images` displays
nothing but its header and `podman system df` falls to `0B` everywhere. The disk
follows, and that is the check that matters: measured separately on three images
built from an empty store, `du -sh ~/.local/share/containers` gives **158 MB**
before, **300 kB** after the `prune -a -f`. `podman system prune -a -f` does the
same thing for containers, images and networks in one go, but without asking
anything: on a shared machine, prefer explicit deletions.

### Troubleshooting

**`short-name resolution enforced but cannot prompt without a TTY`**: a `FROM`
with a short name that Podman cannot resolve on its own. Write the full name,
registry and tag included.

**`possible escaping context directory error`**: a `COPY ../file` will never
work. `COPY` only reads under the build context, the directory passed as the
last argument of `podman build`.

**`no Containerfile or Dockerfile specified or found in context directory`**:
you are building from the wrong directory, or your file has another name. In
that case, point at it: `podman build -f mon-fichier -t nom:tag .`

**`unable to delete image "..." by ID with more than one tag [...]: please force
removal`**: the image carries several names. Remove them one by one with
`podman rmi <name>:<tag>`, or force it with `podman rmi -f`.
