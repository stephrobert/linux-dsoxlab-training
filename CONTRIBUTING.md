# Contributing to linux-dsoxlab-training

**Language:** [English](./CONTRIBUTING.md) · [Français](./CONTRIBUTING.fr.md)

This repository is a **lab catalog** consumed by the
[`dsoxlab`](https://github.com/stephrobert/dsoxlab) CLI. Contributions are new
labs, fixes, and translations. The CLI itself lives in its own repository — do
not add engine code here.

## Setup

```bash
uv tool install dsoxlab        # the CLI (external tool)
git clone <this-repo-url> linux-dsoxlab-training
cd linux-dsoxlab-training
dsoxlab doctor                 # check your environment
```

## The golden rule: validation proves state

A lab's tests must assert **the state of the system**, never that a command was
typed. The service is running *and* enabled; the mount is present *and* declared
in `/etc/fstab` by UUID; the SELinux context is set persistently. Whenever a lab
configures something meant to survive a reboot, the tests assert
**persistence after reboot** explicitly — it is exactly what fails RHCSA
candidates.

## Anatomy of a lab

```text
labs/linux/<section>/<lab>/
├── lab.yaml            # the contract (id, level, runtime, validation…)
├── lab.fr.yaml         # optional: French override of title/description ONLY
├── README.md / scenario.md
├── setup.yaml / cleanup.yaml       # VM labs
└── challenge/
    ├── README.md       # the mission, no step-by-step
    ├── hints.yaml      # cost-weighted hints
    ├── tests/test_functional.py    # the proof: system state
    └── work/           # starting material (shell labs)
solution/…              # reference solution, replayed in CI to prove itself
```

## Proposing a lab

- **Start from a capability, not a guide.** Describe a demonstrable capability
  ("extend a logical volume and prove the mount survives a reboot"), open an
  issue, and agree on scope before writing.
- **Pick the runtime the subject demands:** VM (`kvm`/`incus`) for anything
  touching systemd, the firewall, SELinux, boot, or persistent storage; `shell`
  for files, text, and permissions.
- Point `doc_url` at the real guide the lab makes the learner practice.

## Local checks (before opening a PR)

```bash
dsoxlab validate-structure     # the meta.yml + lab.yaml contract
dsoxlab check <lab-id>         # run the lab's tests (or: pytest)
python3 scripts/gen_catalog.py # refresh the README catalog (labs + guide URLs)
```

**Required before every push:** the root `README.md` and `README.fr.md` must
list every lab together with its companion-guide URL. The catalog is generated
from the real `lab.yaml` files — run `python3 scripts/gen_catalog.py` after
adding or renaming a lab, and `python3 scripts/gen_catalog.py --check` to verify.
CI and the `pre-push` hook both reject a stale catalog.

## Conventions

- **Lab id:** `<level>-<slug>` (e.g. `l1-first-terminal`), matching the
  directory name.
- **Commits:** `feat(<lab>): …`, `fix: …`, `docs: …`, `test: …`.
- **i18n:** `lab.fr.yaml` overrides `title` and `description` only — nothing else.

## Pull requests

Work on a dedicated branch, keep `dsoxlab validate-structure` green, write a
clear description, and link the capability/issue it addresses.
