# Security Policy

**Language:** [English](./SECURITY.md) · [Français](./SECURITY.fr.md)

## Supported versions

`linux-dsoxlab-training` is in active development. Security fixes are applied to
the latest release on the `main` branch.

| Version | Supported |
| --- | --- |
| latest (`main`) | ✅ |
| older | ❌ |

## Reporting a vulnerability

**Please do not open a public issue for security vulnerabilities.**

If you believe you have found a security vulnerability, report it privately:

- Preferred: open a
  [private security advisory](https://github.com/stephrobert/linux-dsoxlab-training/security/advisories/new)
  on GitHub.
- Alternatively, use the contact details published at
  <https://blog.stephane-robert.info>.

Please include:

- a description of the vulnerability and its impact,
- the steps to reproduce it (command, environment, `dsoxlab --version`),
- any relevant logs or proof of concept.

We will keep you informed about the progress toward a fix, and credit you in the
release notes if you wish.

## Disclosure policy

We follow coordinated disclosure and commit to the following timelines, counted
from the moment your report reaches us:

| Stage | Target |
| --- | --- |
| Acknowledgement of your report | within **48 hours** |
| Initial assessment and severity triage | within **5 days** |
| Fix released, or a written remediation plan | within **30 days** |
| Public disclosure of the vulnerability | within **90 days** |

We publish the advisory once a fix is available, or at the **90-day** deadline at
the latest, whichever comes first. If a vulnerability is being actively
exploited, we may disclose it sooner to protect users. Should we need more time
on a complex fix, we will tell you before the deadline and agree on a new date
with you rather than let it lapse silently.

## Scope

This repository ships **lab content** (scenarios, tests, setup/cleanup and
provisioning fixtures, SSH public keys) executed by the external `dsoxlab` CLI.
In scope: unsafe or malicious lab material (setup/cleanup, tests,
Terraform/cloud-init templates), leaked secrets, or a private key committed by
mistake. Vulnerabilities in the `dsoxlab` engine itself belong to
[its own repository](https://github.com/stephrobert/dsoxlab); third-party
dependency issues should be reported to their respective projects.
