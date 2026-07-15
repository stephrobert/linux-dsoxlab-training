# Changelog

**Language:** [English](./CHANGELOG.md) · [Français](./CHANGELOG.fr.md)

All notable changes to this project are documented in this file. The format is
based on [Keep a Changelog](https://keepachangelog.com/), and the project follows
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

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
