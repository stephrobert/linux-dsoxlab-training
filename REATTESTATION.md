# Re-attesting this catalogue's labs

> Written on 2026-10-19, with values **measured on disk** rather than copied.
> Numbers age: `validation-labs.json` remains the source of truth for verdicts.

## Why this page exists

On 2026-10-19, a re-attestation campaign recorded **twelve false REDs** in one
catalogue before being stopped, and hung for twenty-three minutes in another.
Neither cause had anything to do with the labs: a `.venv` whose shebangs still
named the repository's former path after a rename, and a command-line tool
waiting on network access the sandbox does not grant.

In both cases the validator **looked like it was measuring the labs when it was
measuring its own breakdown**, and it wrote that into the record. A false RED
costs more than a missing verdict: it sends people hunting for a defect in a lab
that has none.

## What this catalogue requires

- **dsoxlab 0.5.4 or newer** on the `PATH`. That is the engine version the record will carry, and the record states it for ALL labs: see the section on partial replays.
- **`.vault-pass` at the root**: 89 solution file(s) in this catalogue are ansible-vault encrypted, and the cycle lays them decrypted. The secret is never committed. Here: present.
- **Provisioned infrastructure**: 69 lab(s) are `runtime: vm` on the `lab-linux` network and require `dsoxlab provision` before the campaign and `dsoxlab destroy` after. Expected hosts: `alma-rhcsa-1.lab`, `alma-rhcsa-2.lab`, `ubuntu-lfcs-1.lab`.
- Real free memory, not what `doctor` reports: destroy the other repositories' infrastructure BEFORE provisioning this one, or the VMs compete for RAM and labs fail by exhaustion, which looks like a lab defect.

## The command

```bash
uv run scripts/valider-labs.py
```

A single lab, to exercise the harness before committing to all 89:

```bash
uv run scripts/valider-labs.py --lab <lab-id>
```

**Starting with one lab is not a matter of principle.** It is what separates an
environment defect from a lab defect: if the single lab passes, the harness is
sound; if it fails like the others, the harness is what needs fixing.

## Current state

Current record: 89 VALIDE. Declared engine: dsoxlab 0.4.1. Verdict dates: 2026-10-12, 2026-10-17. Cumulative duration of the last measured cycle: **40 minutes** for 89 labs, excluding infrastructure provisioning and teardown.

## The four traps that produce a false verdict

**1. A `.venv` with dead shebangs.** If the repository was renamed, the scripts
in `.venv/bin/` still point at the old path and no longer execute. The symptom
is an identical failure on every lab, often on decrypting the solution. Check
and fix:

```bash
head -1 .venv/bin/ansible-vault      # the path must exist
uv venv --clear && uv sync           # recreate it
```

**2. `uv run --no-sync` on an empty venv.** The flag assumes an already
populated environment. On a fresh clone it raises `ModuleNotFoundError` before
looking at a single lab. Run without `--no-sync` the first time.

**3. A tool waiting on network access the sandbox does not grant.** Measured on
an `octl --version` that hung for twenty-three minutes: only the top-level
command is exempt, a subprocess is not. If a campaign stops progressing, look at
its child processes before suspecting a lab:

```bash
ps -eo pid,etimes,cmd | grep -E 'python.*valider[-]labs'
ps --ppid <validator-pid> -o pid,etimes,cmd
```

**4. A partial replay makes the record's header false.** The engine version is
recorded **once for the whole file**, while verdicts are per lab. Replaying a
single lab therefore rewrites that header, and the record then claims all its
labs were attested with the current version. Either replay everything, or
restore the record:

```bash
git checkout -- validation-labs.json
```

## What the record does not say

It does not say **which engine version attested each lab**, only the one from
the last campaign. This is a known gap, and it shows as soon as a campaign is
partial.

This catalogue does record that header (`genere_le`, `dsoxlab` and the versions of the tools used), which is the collection's good practice.

## Why this catalogue's verdicts are stale

A **single** commit made them stale, and it is verified rather than taken from a list: `6f25b79` of **2026-10-17**, "fix(labs): les messages d'échec en EN + FR, et une contrainte qu'aucun test ne tenait (#84)", touching **87 test files**.

So this is not gradual drift: it is a coordinated campaign to make failure messages bilingual, carried out on 2026-10-17 across eight catalogues and 289 test files. That commit's subject also names a defect fixed along the way, and that is what makes the replay mandatory: a test that graded wrongly invalidates the verdict it produced.

Not to be confused with the 2026-10-19 commit, which moved the `doc_url` host from `blog.` to `www.`. That one touches descriptors and documentation, changes no action, and makes nothing stale.

## The record's shape decides what the site can say about it

This catalogue's record uses the **enveloppé** shape, and the site does read the engine version from it, currently "dsoxlab 0.4.1".

The site's generator reads `genere_le` and `dsoxlab` **only when the `labs`
key is a dictionary**: a record whose top-level keys are lab identifiers falls
into another branch, which returns an empty date and tool. Fixing the field
without fixing the shape would therefore change nothing, which is why both are
stated together here.
