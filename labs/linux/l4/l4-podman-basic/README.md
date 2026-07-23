# Lab — run a detached container with Podman

## Reminder

[**Podman on the companion guide**](https://blog.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/)

`podman run -d --name <name> <image> <cmd>` runs a detached container.
`podman ps` lists the running containers; `podman inspect -f '{{.State.Running}}'`
reads whether it is up. `podman rm -f` removes it.

## The course

The examples below work with the image `docker.io/library/alpine:3.21` and
containers named `horloge`, `ephemere` and `port-haut`: the challenge will ask
for another name and another image. The goal is to learn the gesture, not to
copy a line. All the outputs come from an **AlmaLinux 10.2** VM running
**Podman 5.8.2**, as an ordinary user with **UID 1001**.

### Checking Podman, and knowing where images come from

On a minimal AlmaLinux, Podman is not there. The package pulls in `crun` (the OCI
runtime), `conmon` (the supervisor of a container), `netavark` and `aardvark-dns`
(the network) and `passt` (the user-space network stack), without enabling a
single service:

```bash
command -v podman || sudo dnf -y install podman
podman --version          # podman version 5.8.2
```

Less obvious: **a short image name is not necessarily a Docker Hub name**.
Resolution is driven by `/etc/containers/registries.conf`:

```bash
grep -vE '^\s*#|^\s*$' /etc/containers/registries.conf
```

```text
unqualified-search-registries = ["registry.access.redhat.com", "registry.redhat.io", "docker.io"]
short-name-mode = "enforcing"
```

On a RHEL base, the Red Hat registries are therefore queried **before** Docker
Hub. Some very common names also carry an explicit alias, shipped by the
`containers-common` package in `registries.conf.d/000-shortnames.conf`: it is
that alias, and not the search list, that answered `podman pull alpine`:

```text
Resolved "alpine" as an alias (/etc/containers/registries.conf.d/000-shortnames.conf)
Trying to pull docker.io/library/alpine:latest...
```

Hence the rule: **write the image in full, with its tag**
(`docker.io/library/alpine:3.21`). You then know what you are pulling, and the
implicit `:latest` will not change under your feet.

### Rootless: no daemon, no privileges

This is what sets Podman apart from Docker, and it is something to observe
rather than to assert. Three questions asked of the machine:

```bash
podman info --format 'Rootless: {{.Host.Security.Rootless}}'
podman info --format 'GraphRoot: {{.Store.GraphRoot}}'
pgrep -a podman ; echo "code retour pgrep = $?"
```

```text
Rootless: true
GraphRoot: /home/ansible/.local/share/containers/storage
code retour pgrep = 1
```

`pgrep` returns nothing (code 1): **no `podman` process runs permanently**. The
CLI is not a client talking to a daemon, it starts the container itself. Storage
is not shared either: the images live in your `$HOME`, never in
`/var/lib/containers`.

> An optional `podman.socket` service exists for tools that require the Docker
> API. It is not active by default: `systemctl is-active podman.socket` answers
> `inactive`, both system-wide and in `--user` mode.

Let us start a detached container that produces something to read:

```bash
podman run -d --name horloge docker.io/library/alpine:3.21 \
  sh -c 'while true; do date; sleep 5; done'
podman ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'
```

```text
NAMES       IMAGE                          STATUS
horloge     docker.io/library/alpine:3.21  Up 9 seconds
```

The same container, seen from two sides. **Inside**,
`podman top horloge user pid comm`:

```text
USER        PID         COMMAND
root        1           sh
root        5           sleep
```

**On the host**, `ps -eo user,pid,args | grep -E 'while true|sleep 5'`:

```text
ansible     6016 sh -c while true; do date; sleep 5; done
ansible     6031 sleep 5
```

`root` as PID 1 on the container side, `ansible` on the host side: it is the
same process, seen from two namespaces, and it never had the slightest
privilege. Next to it runs a `conmon`, also owned by `ansible`, which holds the
streams and the exit code.

### The UID shift: subuid, subgid and volumes

How can you be `root` inside without being root outside? Through a *user
namespace*, whose ranges are declared when the account is created:

```bash
grep "^$USER:" /etc/subuid /etc/subgid
podman unshare cat /proc/self/uid_map
```

```text
/etc/subuid:ansible:589824:65536
/etc/subgid:ansible:589824:65536
         0       1001          1
         1     589824      65536
```

Read each line of `uid_map` from left to right: *starting UID inside the
container*, *matching UID on the host*, *number of UIDs*. Two lines, so two
rules:

| Inside the container | On the host | Why |
|---|---|---|
| `0` (root) | `1001` (you) | your own UID, a single value |
| `1` to `65536` | `589824` to `655359` | the range reserved in `/etc/subuid` |

Checking it on a file is better than a diagram. Create a volume, write to it as
root **of the container**, then look at the result from the host (`:Z` is the
SELinux part: it asks for the content to be relabelled):

```bash
podman volume create notes
podman run --rm -v notes:/data:Z docker.io/library/alpine:3.21 \
  sh -c 'echo bonjour > /data/note.txt; ls -ln /data'
ls -ln "$(podman volume inspect notes --format '{{.Mountpoint}}')"
```

```text
-rw-r--r--    1 0        0                8 Jul 22 15:49 note.txt   # inside
-rw-r--r--. 1 1001 1001 8 Jul 22 15:49 note.txt                     # outside
```

**UID 0 inside, UID 1001 outside: the file belongs to you.** The same file
`chown 1000:1000` from the container then belongs, on the host, to `590823`
(`589824 + 1000 - 1`), which matches no account at all. That is the origin of
the `permission denied` errors on shared directories, which `--userns=keep-id`
fixes.

### The two surprises of rootless

**A port below 1024 is refused.** The kernel reserves them for root, and you are
not root:

```bash
podman run -d --name essai-port -p 80:8080 \
  docker.io/library/alpine:3.21 sleep 300
```

```text
Error: pasta failed with exit code 1:
Failed to bind port 80 (Permission denied) for option '-t 80-80:8080-8080'
```

The message does not talk about Podman but about **pasta**, the process that
carries the rootless network and actually opens the socket on the host. Above
1024 everything goes fine, and `ss` confirms who is listening:

```bash
podman run -d --name port-haut -p 8080:8080 \
  docker.io/library/alpine:3.21 sleep 30
podman port port-haut ; ss -tlnp | grep 8080
```

```text
8080/tcp -> 0.0.0.0:8080
LISTEN 0  128  *:8080  [...]  users:(("pasta.avx2",pid=5753,fd=6))
```

The threshold is the `net.ipv4.ip_unprivileged_port_start` sysctl, at `1024`
here: it can be lowered, but publishing on a high port stays the reflex.

**A rootless container does not survive your logout.** Verified by leaving
`horloge` running, then closing all the user's sessions. Watched from another
account, the user goes to `closing`, then disappears from `loginctl list-users`
after about a minute. On return,
`podman ps -a --format 'table {{.Names}}\t{{.Status}}'`:

```text
NAMES       STATUS
horloge     Exited (137)
```

`137` = `128 + 9`, so `SIGKILL`: systemd unmounted `/run/user/1001` along with
the last session and took the container with it. The fix is a single command:

```bash
loginctl enable-linger        # or: sudo loginctl enable-linger <user>
loginctl list-users
```

The test redone with *linger* enabled gives, after two minutes without a single
session open, a user in `lingering` (no longer `closing` then gone) and the
container process still alive:

```text
 UID USER    LINGER STATE
1001 ansible yes    lingering
```

Without `enable-linger`, a rootless service dies with your `exit`.

### The life cycle, end to end

`podman ps` shows only the **running** containers; `podman ps -a` also shows the
dead ones, and that is where the surprises hide:

```bash
podman exec horloge cat /etc/alpine-release      # in a live container
podman logs --tail 3 horloge                     # the standard output of PID 1
podman run --rm docker.io/library/alpine:3.21 echo "conteneur jetable"
podman run -d --name ephemere docker.io/library/alpine:3.21 date
podman ps -a --format 'table {{.Names}}\t{{.Status}}'
```

```text
3.21.7
Wed Jul 22 15:54:30 UTC 2026
Wed Jul 22 15:54:35 UTC 2026
Wed Jul 22 15:54:40 UTC 2026
conteneur jetable
NAMES       STATUS
horloge     Up 2 minutes
ephemere    Exited (0) 2 seconds ago
```

Two containers started, only one remains: `--rm` made the throwaway one vanish as
soon as its command ended, whereas `ephemere` stays in `Exited (0)` because its
command (`date`) finished. **A container lives exactly as long as its main
process**: that is why a detached service needs a command that lasts.

An `Exited` container still holds its name. Running `podman run -d --name
horloge ...` again then gives (real message, shortened):

```text
Error: creating container storage: the container name "horloge" is already
in use by d1bd081db09315[...]. [...] use --replace to instruct Podman to do so.
```

Stopping and removing, finally:

```bash
podman stop horloge
podman rm ephemere
```

```text
time="[...]" level=warning msg="StopSignal SIGTERM failed to stop container
horloge in 10 seconds, resorting to SIGKILL"
horloge
ephemere
```

`podman ps -a` then shows `horloge  Exited (137)`: `sh` does not relay `SIGTERM`
to its loop, Podman waits ten seconds, then kills. A real service exits with
`0`.

### Images, disk space, and what remains when you think you deleted everything

Images are listed and removed separately from containers, and an image held by a
container, **even a stopped one**, cannot be removed:

```bash
podman images
podman rmi docker.io/library/alpine:3.21
```

```text
REPOSITORY                 TAG         IMAGE ID      CREATED        SIZE
docker.io/library/alpine   3.21        2607caa98058  3 months ago   8.13 MB
[...]
Error: image used by d1bd081db093[...]: image is in use by a container:
consider listing external containers and force-removing image
```

Once all the containers are gone, what you had forgotten remains:

```bash
podman rm -af && podman system df
```

```text
TYPE           TOTAL       ACTIVE      SIZE        RECLAIMABLE
Images         3           0           21.51MB     21.51MB (100%)
Containers     0           0           0B          0B (0%)
Local Volumes  1           0           8B          8B (100%)
```

`podman ps -a` is empty, and yet 21 MB of images and a volume are sleeping in
`~/.local/share/containers` (`du -sh` confirms the 21 MB there). The column to
read is **RECLAIMABLE**. Hence three commands to clean up:

```bash
podman rm -af            # containers, even running ones
podman rmi -af           # images  → Untagged: ... / Deleted: ...
podman volume prune -f   # unused volumes → notes
```

and three more to prove it, not one fewer:

```bash
podman ps -a --format 'table {{.Names}}\t{{.Status}}'
podman images ; podman system df
```

```text
NAMES       STATUS
REPOSITORY  TAG         IMAGE ID    CREATED     SIZE
TYPE           TOTAL       ACTIVE      SIZE        RECLAIMABLE
Images         0           0           0B          0B (0%)
Containers     0           0           0B          0B (0%)
Local Volumes  0           0           0B          0B (0%)
```

Three headers without a single data line: nothing is left.
`podman system prune -a --volumes -f` does all of that at once, but deletes
without discussion: on a shared machine, prefer the explicit removals.

> On Podman 6, `podman volume prune` only removes **anonymous** volumes by
> default; you need `--all` to get back the behaviour shown here. The VM of this
> lab runs 5.8, so the question does not arise yet.

Networks, pods, Quadlet and image building are out of scope here: the
[companion guide](https://blog.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/)
covers them chapter by chapter.
