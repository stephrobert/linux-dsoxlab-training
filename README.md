# linux-dsoxlab-training — Linux security labs (RHCSA + LFCS)

**Language:** [English](./README.md) · [Français](./README.fr.md)

[![CI](https://github.com/stephrobert/linux-dsoxlab-training/actions/workflows/ci.yml/badge.svg)](https://github.com/stephrobert/linux-dsoxlab-training/actions/workflows/ci.yml)
[![OpenSSF Scorecard](https://img.shields.io/ossf-scorecard/github.com/stephrobert/linux-dsoxlab-training?label=OpenSSF%20Scorecard)](https://securityscorecards.dev/viewer/?uri=github.com/stephrobert/linux-dsoxlab-training)
[![Plumber compliance](https://score.getplumber.io/github.com/stephrobert/linux-dsoxlab-training.svg)](https://score.getplumber.io/github.com/stephrobert/linux-dsoxlab-training)
[![SLSA 3](https://slsa.dev/images/gh-badge-level3.svg)](https://slsa.dev)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](./LICENSE)

Hands-on **Linux security & DevSecOps** training, driven by the
[`dsoxlab`](https://github.com/stephrobert/dsoxlab) CLI. This repository is the
**lab catalog** behind the Linux track of
[blog.stephane-robert.info](https://blog.stephane-robert.info/docs/admin-serveurs/linux/),
geared toward the **RHCSA (EX200 v10)** and **LFCS** certifications with a
systematic hardening angle.

## What it is

`linux-dsoxlab-training` is a **content repository**, not an application. It
provides:

- **guided labs** with precise instructions,
- **challenges** with no step-by-step, to check autonomy,
- **capstones** that synthesize a full block,
- **automated validation** that proves the state of the system (not that a
  command was typed),
- **scoring** with cost-weighted hints.

The `dsoxlab` CLI is the single entry point: it starts a lab, shows the
instructions, validates, scores, and reports. The CLI lives in its **own repo**
and is installed **separately** — it is not part of this repository.

## Requirements

- Python 3.11+ and [`uv`](https://docs.astral.sh/uv/)
- `git`
- For L2+ (VM labs — systemd, firewall, SELinux, storage): a provider among
  **KVM/libvirt**, **Incus**, or a supported cloud (Outscale). Shell labs (L1)
  need nothing more than a terminal.

## Install

`dsoxlab` is published on [PyPI](https://pypi.org/project/dsoxlab/) — install it
as a standalone tool:

```bash
# 1. Install the dsoxlab CLI (external tool, stays out of this repo)
uv tool install dsoxlab        # or: pipx install dsoxlab

# 2. Clone this lab catalog
git clone <this-repo-url> linux-dsoxlab-training
cd linux-dsoxlab-training

# 3. Discover and run
dsoxlab list-labs
dsoxlab run <lab-id>
dsoxlab check <lab-id>
```

Check your environment with `dsoxlab doctor` (Python, pytest, runtimes, detected
labs). This repo declares several infrastructure providers, so VM labs need an
active one:

```bash
dsoxlab use --provider kvm     # persisted for this repo
# or, one-shot: DSOXLAB_PROVIDER=kvm dsoxlab provision
```

### Keeping it up to date

New labs land in this repository, and the CLI evolves separately. Update each on
its own:

```bash
git pull                       # pull new/updated labs into your clone
uv tool upgrade dsoxlab        # update the CLI (or: pipx upgrade dsoxlab)
```

Your in-progress answers live in each lab's `challenge/work/`, which is
gitignored — so `git pull` brings new labs without ever touching your work.

## How it works

### The declarative contract (two levels)

The catalog is described by data, not code — the `dsoxlab` engine stays
domain-agnostic and reads two levels of files:

- **`meta.yml`** at the repo root declares the repository identity, the
  infrastructure topology (network, hosts, providers), and the **order** of
  sections shown by `list-labs`.
- **`lab.yaml`** per lab (under `labs/linux/<section>/<lab>/`) declares its
  `skills`, `level`, `runtime` (shell/incus/kvm + target host), `distros`,
  `doc_url`, and a `validation` block (`functional`, `security`,
  `persistence_after_reboot`). An optional `lab.fr.yaml` overrides `title` and
  `description` in French.

`dsoxlab validate-structure` checks the whole contract: `meta.yml` is well
formed, every referenced lab exists with a valid `lab.yaml`, every
`runtime.host` points to a declared host, and every referenced test/script file
is present.

### The lab lifecycle

A learner drives everything through the CLI; a typical run:

```bash
dsoxlab use --provider kvm            # pick an infra provider (VM labs)
dsoxlab doctor                        # check the environment (Python, pytest, runtimes, labs)
dsoxlab list-labs                     # browse the catalog
dsoxlab show <id>                     # metadata + status of one lab
dsoxlab run <id>                      # prepare & start the lab environment
dsoxlab course <id>                   # read the guided course (optional)
dsoxlab challenge <id>                # read the mission (no step-by-step)
dsoxlab hint <id>                     # reveal a hint (deducted from the score)
dsoxlab check <id>                    # run the tests, compute & record the score
dsoxlab submit <id>                   # final submission, closes the session
dsoxlab progress                      # per-block progress, average score
```

`run` is where the environment comes up. For a **shell** lab it creates the
lab's `workdir` and copies the declared fixtures. For a **VM** lab it selects the
target host (Terraform-provisioned) and applies the lab's setup with Ansible.

### Runtimes

| Runtime | Backend | What it gives you |
|---|---|---|
| `shell` | local shell | Fast, single-host exercises (files, text, permissions). No VM cost — tests run on your own machine and validate its real state. |
| `incus` | Incus containers | Isolated Linux environments, quick to start. |
| `kvm` | Terraform + libvirt | Full VMs, the only runtime that can prove **reboot/persistence** (systemd, firewall, SELinux, storage). |

VM labs are provisioned once with `dsoxlab provision` (Terraform) and torn down
with `dsoxlab destroy`. Providers (KVM/Incus/Outscale) are interchangeable and
selected per repo with `dsoxlab use --provider <name>`; IPs are assigned by the
provider, never hard-coded.

### The validation model

Validation **proves the state of the system, it does not trust the learner**.
Each lab ships `pytest` / `pytest-testinfra` tests under
`challenge/tests/` that assert facts on the machine: the service is running
*and* enabled, the mount is present *and* declared in `/etc/fstab` by UUID, the
SELinux context is set persistently. A test that merely checks "a command was
typed" is rejected.

- In CI / instructor mode, a root `conftest.py` fixture **replays the reference
  `solution/`** before the tests, to prove the solution itself is correct.
- In `dsoxlab check` (the learner path) that replay is **disabled**
  (`LAB_NO_REPLAY=1`) so the tests validate the learner's own work.
- **Persistence after reboot** is a first-class criterion: it is exactly what
  fails RHCSA candidates, so VM labs that configure something meant to survive a
  reboot assert it explicitly.

### Scoring, hints, progress

`check` records a score (passed/total minus the cost of any hints used). Hints
are **cost-weighted** — revealing one deducts points, which is why they are
opt-in. History lives in a local SQLite database
(`~/.local/share/dsoxlab/progress.db`, XDG-overridable); `dsoxlab scores` and
`dsoxlab progress` read it. The active session (context, provider) is stored per
repo in `.dsoxlab-context.json`.

## Catalog

Labs live under `labs/linux/` and are ordered by `meta.yml`. The table below is
generated from the real `lab.yaml` files — run `python3 scripts/gen_catalog.py`
to refresh it.

<!-- LABS:START -->
### Fondamentaux (l1)

| Lab (id) | Title | Level | Certif | Runtime | Companion guide |
|---|---|---|---|---|---|
| `l1-discover-linux-map` | Map Linux: kernel, distribution and key directories | l1 | RHCSA · LFCS | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/notions/) |
| `l1-choose-distro` | Choose your reference Linux distribution | l1 | RHCSA · LFCS | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/distributions-serveur/) |
| `l1-prepare-vm` | Identify your Linux machine | l1 | RHCSA · LFCS | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/installer-vm/) |
| `l1-first-terminal` | First steps in the terminal | l1 | RHCSA · LFCS | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/prompt-terminal/) |
| `l1-read-a-command` | Read and decode a command | l1 | RHCSA · LFCS | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/anatomie-commande/) |
| `l1-get-help` | Get help from the command line | l1 | RHCSA · LFCS | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/obtenir-aide/) |
| `l1-linux-filesystem` | Linux filesystem hierarchy (FHS) | l1 | RHCSA · LFCS | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/arborescence-fhs/) |
| `l1-navigate-filesystem` | Navigate the filesystem | l1 | RHCSA · LFCS | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/navigation-fichiers/) |
| `l1-paths-absolute-relative` | Absolute and relative paths | l1 | RHCSA · LFCS | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/chemins-linux/) |
| `l1-redirections-pipes` | Redirect streams and chain commands with pipes | l1 | RHCSA | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/redirections-pipes/) |
| `l1-grep-regex` | Filter a log with grep and regular expressions | l1 | RHCSA · LFCS | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/filtrer-texte/) |
| `l1-text-processing` | Transform and aggregate text with cut, sort, uniq, sed and awk | l1 | RHCSA · LFCS | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/transformer-texte/) |
| `l1-find-files` | Locate files with find by name, size and permissions | l1 | RHCSA · LFCS | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/rechercher-fichiers/) |
| `l1-tar-archives` | Archive, compress and selectively extract with tar, gzip and bzip2 | l1 | RHCSA | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/archives-compression/) |
| `l1-permissions-ugo` | Set exact file permissions with chmod (octal and symbolic) | l1 | RHCSA · LFCS | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/utilisateurs-droits-processus/modifier-droits/) |
| `l1-links-hard-sym` | Create hard and symbolic links and tell them apart | l1 | RHCSA | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/navigation-fichiers/) |
| `l1-bash-script` | Write a first Bash script: variables, a loop and a condition | l1 | RHCSA · LFCS | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/efficace-shell/premier-script/) |
| `l1-git-basics` | Initialize a Git repo: commit, history and a branch | l1 | LFCS | shell | [guide](https://blog.stephane-robert.info/docs/developper/version/git/bases-git/) |
| `l1-env-profiles` | Environment variables: export, PATH and a sourced env file | l1 | LFCS | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/efficace-shell/variables-environnement/) |
| `l1-ssl-certificates` | Inspect a TLS certificate with openssl | l1 | LFCS | shell | [guide](https://blog.stephane-robert.info/docs/reseaux/fondamentaux/tls-diagnostic/) |

### Exploiter + Maintenir (l2)

| Lab (id) | Title | Level | Certif | Runtime | Companion guide |
|---|---|---|---|---|---|
| `l2-swap-management` | Add and manage swap space | l2 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/swap/) |
| `l2-fstab-persist-uuid` | Mount a filesystem persistently by UUID in /etc/fstab | l2 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/montage-persistance/) |
| `l2-partition-gpt` | Create GPT partitions on a disk with parted | l2 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/partitions/) |
| `l2-filesystem-create-xfs` | Create and label an XFS filesystem, then mount it | l2 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/xfs/) |
| `l2-disk-space-troubleshoot` | Diagnose a full filesystem and reclaim space | l2 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/espace-disque/) |
| `l2-storage-performance` | Tune a mount for performance with noatime (persistently) | l2 | LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/performances-disques/) |
| `l2-lvm-extend-persist` | Extend a logical volume and prove the mount survives a reboot | l2 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/lvm/) |
| `l2-nfs-mount-persist` | Mount an NFS export persistently from a server | l2 | LFCS | vm | [guide](https://blog.stephane-robert.info/docs/services/stockage/nfs/) |
| `l2-autofs-ondemand` | Mount a filesystem on demand with autofs | l2 | LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/autofs/) |
| `l2-raid-mdadm` | Build a software RAID 1 with mdadm | l2 | LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/raid-mdadm/) |
| `l2-luks-encryption` | Encrypt a disk with LUKS | l2 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/chiffrement-luks/) |
| `l2-user-lifecycle` | Create a local account with exact UID, shell and groups | l2 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/) |
| `l2-password-policy` | Enforce password aging and complexity policy | l2 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/utilisateurs-groupes/) |
| `l2-sudo-delegation` | Delegate limited sudo rights with a sudoers drop-in | l2 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/sudo/) |
| `l2-acl-posix` | Grant fine-grained access with POSIX ACLs | l2 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/acl/) |
| `l2-collaborative-setgid` | Set up a collaborative directory with the set-GID bit | l2 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/securiser/durcissement/permissions-ownership/) |
| `l2-package-management` | Install, remove and query packages with dnf | l2 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/) |
| `l2-repo-configure` | Configure a dnf repository with a .repo file | l2 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/dnf/) |

### Services + Dépannage (l3)

| Lab (id) | Title | Level | Certif | Runtime | Companion guide |
|---|---|---|---|---|---|
| `l3-boot-target` | Set the default systemd boot target | l3 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/demarrage-reboot/) |
| `l3-grub-kernel-args` | Add a persistent kernel boot parameter | l3 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/securiser/durcissement/grub/) |
| `l3-service-create-unit` | Create and enable a systemd service unit | l3 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/services/) |
| `l3-service-diagnose` | Diagnose and fix a systemd service stuck in a crash loop | l3 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/service-ne-demarre-pas/) |
| `l3-journald-persist` | Make the systemd journal persistent across reboots | l3 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/systemd/journaux/) |
| `l3-scheduling-cron` | Schedule a recurring job with cron | l3 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/cron/) |
| `l3-scheduling-at` | Schedule a one-shot job with at | l3 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/at/) |
| `l3-scheduling-timers` | Schedule a recurring job with a systemd timer | l3 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/timers/) |
| `l3-app-constraints` | Set per-user resource limits (open files) with limits.d | l3 | LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/processus/limites-ressources/) |
| `l3-sysctl-persist` | Harden kernel parameters persistently with sysctl.d | l3 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/securiser/durcissement/sysctl/) |
| `l3-process-signals-priority` | Lower a service's scheduling priority with Nice | l3 | LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/utilisateurs-droits-processus/comprendre-processus/) |
| `l3-tuned-profile` | Apply a tuned performance profile | l3 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/tuned/) |
| `l3-fs-readonly-recover` | Recover a read-only mount caused by a broken fstab | l3 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/systeme-fichiers-lecture-seule/) |
| `l3-ssh-access-recovery` | Repair a broken sshd config before it locks you out | l3 | RHCSA · LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/perte-acces-ssh/) |

### Réseau, Sécurité & Conteneurs (l4)

| Lab (id) | Title | Level | Certif | Runtime | Companion guide |
|---|---|---|---|---|---|
| `l4-ntp-sync` | Synchronize the clock with chrony and set the timezone, persistently | l4 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/services/reseau/chrony/) |
| `l4-network-static-persist` | Configure a persistent static IPv4 with NetworkManager | l4 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/networkmanager/) |
| `l4-network-troubleshoot` | Diagnose and restore a down network connection | l4 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/diagnostic/) |
| `l4-firewall-persist` | Open a firewalld service permanently | l4 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/securiser/reseaux/firewalld/) |
| `l4-ssh-key-auth-harden` | Set up hardened key-based SSH access for a service user | l4 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/ssh/cle-ssh/) |
| `l4-podman-basic` | Run a detached container with Podman | l4 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/) |
| `l4-podman-systemd-persist` | Run a container as a systemd service with Quadlet (boot-persistent) | l4 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/conteneurs/moteurs-conteneurs/podman/quadlet/) |
| `l4-podman-images` | Manage container images: pull, tag, save and inspect | l4 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/conteneurs/images-conteneurs/) |
| `l4-selinux-boolean-port` | Allow a service with SELinux: persistent boolean and labeled port | l4 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/) |
| `l4-selinux-context-fix` | Fix a file's SELinux context, persistently | l4 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/) |
| `l4-selinux-diagnose-avc` | Diagnose an SELinux denial (AVC) and fix it the right way | l4 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/securiser/durcissement/selinux/) |
| `l4-nat-portforward` | Set up persistent NAT port forwarding with nftables | l4 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/securiser/reseaux/nat-port-forwarding/) |
| `l4-ldap-integration` | Authenticate Linux against an LDAP directory with SSSD | l4 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/authentifier-ldap-sssd/) |
| `l4-reverse-proxy-lb` | Load-balance a web backend with HAProxy | l4 | LFCS | vm | [guide](https://blog.stephane-robert.info/docs/services/reseau/haproxy/) |
| `l4-bridge-bonding` | Aggregate links: an active-backup bond under a bridge with nmcli | l4 | LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/bond-bridge/) |

### LFCS

| Lab (id) | Title | Level | Certif | Runtime | Companion guide |
|---|---|---|---|---|---|
| `lfcs-package-apt` | Manage Debian packages with apt and dpkg | l2 | LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/maintenir/paquets/apt/) |
| `lfcs-firewall-ufw` | Open a service through the firewall with ufw | l4 | LFCS | vm | [guide](https://blog.stephane-robert.info/docs/securiser/reseaux/ufw/) |
| `lfcs-apparmor` | Manage an AppArmor profile: switch it to complain mode | l4 | LFCS | vm | [guide](https://blog.stephane-robert.info/docs/securiser/durcissement/apparmor/) |
| `lfcs-netplan-static` | Configure a static IP and route with netplan | l4 | LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/reseau/netplan/) |
| `lfcs-storage-quotas` | Enable XFS user quotas and enforce a limit | l2 | LFCS | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/references-complementaires/quotas/) |
| `lfcs-mount-cifs` | Mount an SMB/CIFS share persistently and safely | l2 | LFCS | vm | [guide](https://blog.stephane-robert.info/docs/services/stockage/smb/) |

### Capstones

| Lab (id) | Title | Level | Certif | Runtime | Companion guide |
|---|---|---|---|---|---|
| `rhcsa-mock-exam` | RHCSA EX200 mock exam — 20 tasks across 2 VMs | l2 | RHCSA | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/certifications/rhcsa/) |

_74 labs — table générée par `scripts/gen_catalog.py`._
<!-- LABS:END -->

## Contributing & license

- Contributions: see [CONTRIBUTING](./CONTRIBUTING.md).
- Conduct: [Code of Conduct](./CODE_OF_CONDUCT.md) · Security: [SECURITY](./SECURITY.md).
- Releases: [RELEASING](./RELEASING.md) (tar.gz bundles, no PyPI).
- License: [CC BY 4.0](./LICENSE).
