# Harden the kernel, permanently

## The situation

A security scan flags this host: it forwards IP packets and accepts ICMP
redirects — neither is wanted on a normal server. Turn them off, at the kernel
level, so it holds now **and** after a reboot.

The point: a `sysctl` parameter can be changed live, but whatever is set live is
gone after a reboot. Making the setting active right now and making it durable
are two distinct moves: the tests will look at both.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/secure/sysctl/

## What is asked

### Mission

Harden the kernel: turn off IP routing and ICMP redirects, persistently.

### Goal (expected state)

1. `sysctl -n net.ipv4.ip_forward` → **0** (live).
2. `sysctl -n net.ipv4.conf.all.accept_redirects` → **0** (live).
3. Both are declared in `/etc/sysctl.d/` (reboot persistence).

### Constraints

- Drop-in `/etc/sysctl.d/99-hardening.conf`, then `sudo sysctl --system`.
  Validation reads the kernel's **active values** + the contents of sysctl.d.

### Validation

```bash
dsoxlab check l3-sysctl-persist
```
