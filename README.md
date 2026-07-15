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

| Lab (id) | Title | Level | Runtime | Companion guide |
|---|---|---|---|---|
| `l1-discover-linux-map` | Map Linux: kernel, distribution and key directories | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/notions/) |
| `l1-choose-distro` | Choose your reference Linux distribution | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/distributions-serveur/) |
| `l1-prepare-vm` | Identify your Linux machine | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/installer-vm/) |
| `l1-first-terminal` | First steps in the terminal | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/prompt-terminal/) |
| `l1-read-a-command` | Read and decode a command | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/anatomie-commande/) |
| `l1-get-help` | Get help from the command line | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/decouvrir-linux/obtenir-aide/) |
| `l1-linux-filesystem` | Linux filesystem hierarchy (FHS) | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/arborescence-fhs/) |
| `l1-navigate-filesystem` | Navigate the filesystem | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/navigation-fichiers/) |
| `l1-paths-absolute-relative` | Absolute and relative paths | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/chemins-linux/) |
| `l1-redirections-pipes` | Redirect streams and chain commands with pipes | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/redirections-pipes/) |
| `l1-grep-regex` | Filter a log with grep and regular expressions | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/filtrer-texte/) |
| `l1-text-processing` | Transform and aggregate text with cut, sort, uniq, sed and awk | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/traiter-texte/cut-tr-paste/) |
| `l1-tar-archives` | Archive, compress and selectively extract with tar, gzip and bzip2 | l1 | shell | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/manipuler-fichiers-texte/archives-compression/) |

### Exploiter + Maintenir (l2)

| Lab (id) | Title | Level | Runtime | Companion guide |
|---|---|---|---|---|
| `l2-swap-management` | Add and manage swap space | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/swap/) |
| `l2-raid-mdadm` | Build a software RAID 1 with mdadm | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/raid-mdadm/) |
| `l2-luks-encryption` | Encrypt a disk with LUKS | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/chiffrement-luks/) |
| `l2-lvm-extend-persist` | Extend a logical volume and prove the mount survives a reboot | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/lvm/) |

### Dépanner

| Lab (id) | Title | Level | Runtime | Companion guide |
|---|---|---|---|---|
| `depanner-service-crash-loop` | Diagnose and fix a systemd service stuck in a crash loop | l2 | vm | [guide](https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/service-ne-demarre-pas/) |

_18 labs — table générée par `scripts/gen_catalog.py`._
<!-- LABS:END -->

## Contributing & license

- Contributions: see [CONTRIBUTING](./CONTRIBUTING.md).
- Conduct: [Code of Conduct](./CODE_OF_CONDUCT.md) · Security: [SECURITY](./SECURITY.md).
- Releases: [RELEASING](./RELEASING.md) (tar.gz bundles, no PyPI).
- License: [CC BY 4.0](./LICENSE).
