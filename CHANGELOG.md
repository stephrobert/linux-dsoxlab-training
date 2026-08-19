# Changelog

**Language:** [English](./CHANGELOG.md) · [Français](./CHANGELOG.fr.md)

All notable changes to this project are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/), and the project follows
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Fixed — the first full validation campaign

All 84 labs were replayed on KVM with a negative control (red without the
solution, green with it). Nine defects surfaced, all previously invisible: a
lab's tests only run when someone plays it, and nobody was chaining them.

- **`. /root/xxx.env 2>/dev/null || exit 0` protected nothing.** In a
  non-interactive POSIX `sh`, sourcing a missing file kills the shell **before**
  the `||`. Six `cleanup.yaml` relied on it (`l2-autofs-ondemand`,
  `l2-disk-space-troubleshoot`, `l2-filesystem-create-xfs`, `l2-partition-gpt`,
  `l2-storage-performance`, `l3-fs-readonly-recover`): their `dsoxlab reset`
  failed, leaving the learner stuck. The file is now tested before being
  sourced.
- **Three labs left a partition on the shared disk**, wiping only the
  partition's signature and never the disk's table. They did not fail
  themselves: the **next** lab did.
- **`l2-lvm-extend-persist` failed on an `rmdir`**: `set +e` does not stop the
  `shell` module from returning the last command's exit code. An explicit
  `exit 0` settles it.
- **`l2-filesystem-create-xfs` was replayable only once.** Its `setup` guards
  itself with `creates: /root/.xfs-lab-ready`, which its `cleanup` never
  removed: disk wiped, marker kept, so the partition was never recreated and
  the solution failed on a partition that did not exist.
- **`l2-luks-encryption`: the test was wrong**, not the solution. It looked for
  the `2` of `Version:` within an 8-character slice, while `cryptsetup`'s
  alignment puts it at position 9. The volume had been LUKS2 all along. The
  field's value is now read properly.
- **`l3-journald-persist`: the solution wrote into a missing directory.** The
  `copy` module does not create parents, and `cleanup` removed
  `/etc/systemd/journald.conf.d`. The solution now creates it.
- **`l4-reverse-proxy-lb` and `l4-ldap-integration` were impossible**: their
  `setup` started the service on the second node without **opening the port in
  its firewall**. HAProxy returned `503 No server is available`, and SSSD
  resolved nothing (`No route to host` on port 389). Opening it belongs to the
  starting state: these labs are about the proxy and SSSD, not the server's
  firewall.
- **`drill-firewall` left `firewalld` disabled** after cleaning up, which broke
  `rhcsa-mock-exam` ("FirewallD is not running"). A `cleanup` returns the system
  to neutral; it does not leave the drill's starting state behind.
- **`rhcsa-mock-exam` kept its VG on the shared disk.** Its `umount` failed
  because the NFS export still held `/data/share` at that point, `exportfs -ua`
  coming afterwards.

### Added — the guards

Each one came from a real defect in this campaign, and each was verified by
making it fail:

- **`tests/test_playbooks_syntaxe.py`**: `ansible-playbook --syntax-check` over
  the 129 `setup.yaml`/`cleanup.yaml`. Valid YAML does not prove Ansible can
  load the tasks: a French apostrophe inside a `shell` block is enough to break
  argument splitting, and the breakage only showed at run time, as a `reset`
  exiting `rc=4` without running a single task.
- **`tests/test_marqueurs_setup_cleanup.py`**: every `creates:` marker in a
  `setup` must be removed by its `cleanup`, otherwise the lab resets only once.
  Runs without a VM, so it runs in CI. It found the `l2-filesystem-create-xfs`
  defect and a second case, `l4-ldap-integration`, which turned out to be
  deliberate: it is explicitly exempted, with its rationale.
- **Shared-disk check** in `verify-solutions.py`: after each `vm` lab the
  `cleanup` is played and the disk state **compared against the state before**.
  A lab is only blamed for what it adds, and it is named the moment it dirties
  the disk instead of letting the next one fail.

### Fixed

- **The l1 sequence required editing a file it never taught how to edit.** The
  first three labs asked learners to fill in an answer file, and the
  `l1-first-terminal` challenge even forbids recreating it with a redirection,
  while no l1 course ever showed how to open, write, save and quit an editor.
  The only occurrence of `vim` in the whole section was the **value** of the
  `EDITOR` variable in lab 19. A beginner therefore had to leave the course at
  the very first challenge, as a learner report confirmed.
  - `l1-first-terminal` gains a "Writing to a file without leaving the terminal"
    section (FR and EN): `nano` (Ctrl+O, Ctrl+X), `vi` survival (Esc, `:wq`,
    `:q!`), the `EDITOR` variable, and the matching troubleshooting rows. Its
    examples use names foreign to the challenge, so they do not give away the
    answer.
  - `l1-first-terminal` moves to the **front** of the l1 section, ahead of
    `l1-discover-linux-map`, `l1-choose-distro` and `l1-prepare-vm`.

### Added

- **`scripts/verify-solutions.py`**: replays the encrypted reference solutions
  and proves they still pass the labs' tests. A version bump can break a
  solution unnoticed, since a lab's tests only run when someone plays it. The
  verdict is recorded in `solution/verified-with.json`.
  - `--negative` adds the missing check: after a `dsoxlab reset`, the tests must
    **fail** without the solution. A test that passes both ways proves nothing.
  - `vm` labs with no provisioned infrastructure are counted as **skipped**,
    never as failures: a missing harness is not a content regression.
  - The script refuses to run under an interpreter without `pytest`, rather than
    failing all 84 labs at once and looking like a massive regression.
- Initial lab catalog for the Linux security / DevSecOps track (RHCSA + LFCS):
  - 9 **L1** fundamentals labs (shell), each validated against the **real state**
    of the machine (no fill-in-the-blank worksheets).
  - **L2** storage & security labs: swap, LUKS, RAID.
  - a troubleshooting lab (systemd service crash loop) and an **RHCSA mock-exam**
    capstone.
- Bilingual governance (EN/FR): `README`, `CONTRIBUTING`, `CODE_OF_CONDUCT`,
  `SECURITY`, `RELEASING`.
- CI and release tooling: structure validation, linting, and `tar.gz` release
  bundles (no PyPI — the content ships as a downloadable archive).
