# Changelog

**Language:** [English](./CHANGELOG.md) · [Français](./CHANGELOG.fr.md)

All notable changes to this project are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/), and the project follows
[Semantic Versioning](https://semver.org/).

## [0.2.3] - 2026-10-23

### Added

- A verdict can no longer be committed together with what it measures. The
  `verdicts-et-commun-separes` hook refuses a commit carrying
  `validation-labs.json` alongside anything the cycle plays:
  `challenge/tests/`, `setup.yaml`, `cleanup.yaml`, `lab.yaml` of any lab, and
  the shared tooling. It is itself tested, in both directions, by a hook of its
  own.

  This closes a case **no measurement can catch afterwards**. The staleness of
  a verdict used to be judged by comparing DATES, and that comparison was wrong
  in both directions on 2026-10-22: a correction committed together with the
  verdicts it invalidated passed as healthy, and labs re-attested on a branch
  came back "to be re-attested" after their squash merge, their content
  unchanged. When a squashed pull request touches a test *after* its campaign,
  the single commit carries both and the squash has destroyed what told them
  apart. It cannot be observed, so it is prevented.

  The statement stays allowed next to a verdict: it is not played by the cycle,
  and forbidding it would demand a campaign for a typo.

### Fixed

- `pipelineMustNotLeakSecretsInConfig` is removed from `.plumber.yaml`, where
  it was declared twice. Plumber dropped that control and answers "was removed
  and is now ignored: secret detection is no longer part of Plumber; remove
  this block". Keeping it suggested that secret detection was covered here. It
  is not, and `detect-private-key` is what comes closest, as a hook.

## [0.2.2] - 2026-10-19

### Fixed

- **`l1-first-terminal` awarded one point out of six before any work.** Its
  `test_le_fichier_a_ete_edite_et_non_recree` only checked the second half of
  what its name claims: it verified that the provided header survived, which
  is true of the starting file, without ever checking that the file had been
  edited. A learner who had done nothing therefore started at 17 points, and
  the catalogue's validator rightly refuses that: "a test that is green on the
  starting state is not a test, it is an assumption of the setup".

  The test now requires both: the placeholder gone and the header intact. It
  is therefore false at the start, true at the end, and still false if the
  file was recreated through a redirection, which was the original intent.

- **The `l3-service-diagnose` solution failed one run in three, and not for a
  configuration reason.** It fixed the file, then restarted the service. But
  the unit had exhausted its `StartLimitBurst` while crash-looping before the
  solution arrived, and systemd then refuses to restart it for the whole
  `StartLimitIntervalSec`. The message spoke of a "control process exited",
  which sends people hunting in the configuration they had just repaired.

  A `systemctl reset-failed` now precedes the restart. That is also the gesture
  this lab teaches: a learner who fixes the configuration without resetting
  the counter hits the same wall. Measured before and after: 1 VALID out of 3
  runs, then 4 out of 4.

### Attestation

- **All 89 labs are re-attested with dsoxlab 0.5.4**, full cycle on provisioned
  VMs with a frozen base, 0 before the work and 100 after.

  The earlier campaign that evening wrote a `dsoxlab 0.1.85` header into the
  record, and it was telling the truth: this repository's `.venv` held an
  `editable` install of dsoxlab frozen at that version, and `uv run` prefers it
  over the one on `PATH`. The labs were therefore being exercised by an engine
  three hundred versions old with nothing to signal it, apart from that very
  field nobody read. The venv is cleaned; `pyproject.toml` did not declare
  dsoxlab, so this was a local leftover and not a repository defect.

## [0.2.1] - 2026-10-19

### Changed

- **Every `doc_url` now points at `www.stephane-robert.info`.** The site moved
  from `blog.` to `www.`, and the old host redirects with a 301 to the same
  path. Nothing was broken: `validate-structure --check-urls` follows
  redirections, and this catalogue was green before a single line changed. The
  migration is housekeeping, not repair: a `doc_url` should point at the page
  rather than depend on a redirection that will be removed one day.

  The paths are identical between the two hosts, so only the host changed. The
  359 `doc_url` the catalogues declare were looked up in the site's own
  repository, offline: all of them exist there, including twenty-three pages
  the old host answered with a 404.

## [0.2.0] - 2026-10-17

### Changed

- **The validator reads the contract, not the terminal panel.**
  `scripts/valider-labs.py` parsed the score out of what `dsoxlab check`
  *displays*. That panel is interface: it changed in dsoxlab 0.4.0 and the
  regex stopped finding anything. It now reads `check --json`, which carries a
  `schema`, and the reading lives in `scripts/verdict_check.py`, **identical in
  all twelve catalogs**.

- **Three verdicts, not two.** A run where every collected test skipped
  measured nothing: it is **SKIP**, neither green nor red, and it stays to be
  measured. Painting it red would accuse the lab of what is missing from the
  machine. `--check` therefore exits `10` in that case, against `1` for a RED,
  mirroring `dsoxlab doctor --strict` where 9 is repaired and 10 is remeasured.

- **The README takes the reference structure** shared by the twelve catalogs:
  fourteen sections, in both languages. Seven of them describe dsoxlab rather
  than the subject, and are therefore identical everywhere.

### Requires

- **dsoxlab 0.4.1 or later**, which introduced the `status` field of
  `check --json`. Without it the validator refuses to conclude rather than
  guessing.

### Also

- trois labs eBPF : tracer le noyau avec BCC et bpftool, puis le durcir par sysctl.

## [0.1.1] - 2026-10-14

### Changed

- Every verdict in `validation-labs.json` carries the date it was replayed:
  without it, a stale record and a fresh one look alike.
- The twenty labs of block l1 replayed after the `conftest.py` change, which
  no earlier verdict covered any more.
- The release procedure re-attests labs modified since their verdict.

### Fixed

- Five GitHub actions brought up to date.

## [0.1.0] - 2026-10-09

### Changed

- **Build provenance now reaches SLSA Build Level 3.** The release workflow used
  to attest from its own build job, which GitHub's documentation rates at level
  2: "Artifact attestations by itself provides SLSA v1.0 Build Level 2", while
  "Reusable workflows can provide isolation between the build process and the
  calling workflow, to meet SLSA v1.0 Build Level 3". The README badge has
  claimed level 3 for a while; the workflow now produces it.
  - `.github/workflows/attester.yml` is the only workflow in the repository
    granted `attestations: write`. It performs no `checkout`, receives only a
    name and a digest, and runs no repository code.
  - `release.yml` is split into three jobs: build, attest, publish. The publish
    job writes the release but cannot attest, lacking the permission, and the
    archive is re-checked against its digest before publication so an artifact
    altered between two jobs is not published with provenance that does not
    describe it.
  - Two linters disagreed, then a third settled it. zizmor recommends the
    `uses: $/...` self-repository form, generally available on github.com since
    July 2026; actionlint 1.7.12, released in March, still rejects it as an
    invalid format. `$/` was kept at first, then dropped: Plumber takes it for
    an unpinned third-party action from an unauthorised source, two HIGH
    findings, and the score fell from 100/100 to 70/100. Security tooling
    cannot read it yet, and an analyser that does not understand a construct
    cannot judge it safe, least of all on the line that calls the workflow
    which signs. The call went back to `./`, with the measurement recorded
    beside it and a single scoped zizmor acknowledgement.
  - The check that proves the level is in `RELEASING.md`: it names the signing
    workflow and fails if the provenance came from anywhere else. It needs a
    real release, so it has not been exercised yet.

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

[Unreleased]: https://github.com/stephrobert/linux-dsoxlab-training/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/stephrobert/linux-dsoxlab-training/releases/tag/v0.1.1
[0.1.0]: https://github.com/stephrobert/linux-dsoxlab-training/releases/tag/v0.1.0
