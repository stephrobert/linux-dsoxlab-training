# Lab — LDAP authentication with SSSD

## Reminder

[**SSSD + LDAP on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/securiser/authentifier-ldap-sssd/)

SSSD is the client daemon that queries an LDAP directory on behalf of the
system. Its configuration lives in `/etc/sssd/sssd.conf` (mode `0600` mandatory)
and declares a domain with `id_provider`, `ldap_uri` and `ldap_search_base`.
`authselect` then wires NSS and PAM to SSSD, after which `getent passwd` and `id`
answer from the directory.

## The course

All the examples below deal with **another directory and other accounts** than
the challenge: an AlmaLinux 10 workshop machine that hosts both a 389 Directory
Server with base `dc=atelier,dc=demo` and the SSSD client. On it you find the
user `nlefevre` (uid `4201`) and the group `redaction` (gid `4200`). All the
outputs in this course were produced on that machine.

### The identity chain: NSS answers "who", PAM answers "with which password"

When you type `id`, the system does not know straight away where to look: it is
`/etc/nsswitch.conf` that tells it in which order to consult the sources. When
you log in, it is PAM that decides how to verify the password. The two chains are
**independent**, and SSSD serves both:

```text
getent / id        login / su / ssh
     |                    |
  nsswitch             PAM (pam_sss)
     |                    |
     +-------- SSSD ------+   (local on-disk cache)
               |
            LDAP (directory)
```

That independence explains half the failures on this topic: an account can be
perfectly visible to `getent passwd` and refuse every login, and the opposite is
true too. `getent` can also query **a single source** with `-s`, which settles
the "where does this account come from?" question immediately:

```bash
getent -s files passwd nlefevre   # nothing, rc=2: no local account
getent -s sss   passwd nlefevre   # nlefevre:*:4201:4200:...:/bin/bash
getent -s files passwd student    # student:x:1000:1000::/home/student:/bin/bash
```

The directory account only exists in `sss`, the local account only in `files`.
That is exactly what your validation will prove.

### Installing the packages and writing `sssd.conf`

On AlmaLinux 10, the daemon and the LDAP connector are in two separate packages,
to which you add the home-creation module and the inspection tooling:

```bash
sudo dnf install -y sssd-ldap oddjob-mkhomedir sssd-tools openldap-clients
```

Two remarks that save time: `sssd-common` (so the daemon and `sss_cache`) is
already present on a minimal installation, but **`sssctl` is not installed by
default**: it comes from `sssd-tools`. As for `openldap-servers`, it no longer
exists on RHEL 10 and derivatives; on the server side, you use `389-ds-base`.

The whole client configuration fits in one file:

```ini
[sssd]
services = nss, pam
domains = ATELIER

[domain/ATELIER]
id_provider = ldap
auth_provider = ldap
ldap_uri = ldap://10.10.30.14
ldap_search_base = dc=atelier,dc=demo
ldap_id_use_start_tls = False
override_homedir = /home/%u
default_shell = /bin/bash
cache_credentials = true
```

What matters: `id_provider` and `auth_provider` name the source (identity and
authentication); `ldap_uri` the address of the server; `ldap_search_base` the
branch where accounts are looked up; `override_homedir` and `default_shell`
impose a home and a shell even if the directory does not supply them;
`cache_credentials = true` allows logging in when the directory is unreachable.
The name of the domain (`ATELIER` here) is free, but it must be repeated
identically in `domains =` and in `[domain/...]`.

> The guide shows `config_file_version = 2` at the top of `[sssd]`. On SSSD 2.12
> (AlmaLinux 10), the directive is still tolerated but `sssctl config-check`
> reports it as not allowed; it is no longer necessary.

**The file must be `0600`, otherwise SSSD refuses to start.** This is not a
recommendation, it is a check at startup. With a `0644`:

```bash
sudo systemctl start sssd
sudo journalctl -u sssd -n 5 --no-pager
```

```text
sssd[29861]: [sssd] [access_check_file] (0x0020): Unexpected access to '/etc/sssd/sssd.conf' by other users
sssd[29861]: Can't read config: 'File ownership and permissions check failed'
sssd[29861]: Make sure configuration is readable by the user used to run service and doesn't have public rwx bits set.
```

A `sudo chmod 0600 /etc/sssd/sssd.conf` followed by a `systemctl start sssd`
settles the matter. Note that the systemd unit itself resets the expected rights:
after startup, the file belongs to `root:sssd` in `-rw-r-----`.

### Wiring NSS and PAM with `authselect`

`authconfig` disappeared in RHEL 8 and later: it is `authselect` that now writes
`/etc/nsswitch.conf` and the files in `/etc/pam.d/`. Always start by looking at
where you are coming from:

```bash
sudo authselect current
sudo authselect list
```

```text
Profile ID: local
Enabled features: None

- local  	 Local users only
- sssd   	 Enable SSSD for system authentication (also for local users only)
- winbind	 Enable winbind for system authentication
```

Each profile exposes optional **features**, to be listed before choosing
(`authselect list-features sssd` gives more than twenty of them, including
`with-mkhomedir`, `with-sudo`, `with-faillock`). The switch:

```bash
sudo authselect select sssd with-mkhomedir
```

You have to see what the command actually writes. Before, `/etc/nsswitch.conf`
only knew about local files; after, the `sss` source is inserted:

```text
# before (local profile)
passwd:  files systemd
group:   files [SUCCESS=merge] systemd
shadow:  files systemd

# after (sssd profile)
passwd:  files sss systemd
group:   files [SUCCESS=merge] sss [SUCCESS=merge] systemd
shadow:  files systemd
```

`files` stays **first**: a local account keeps being resolved locally, the
directory is only consulted for what it does not find. Note, contrary to what the
guide suggests: on AlmaLinux 10, the `sssd` profile only adds `sss` to `passwd`
and `group`, **not to `shadow`**.

On the PAM side, `/etc/pam.d/system-auth` gains three lines (the `pam_usertype`
and `pam_localuser` ones serve to skip `pam_unix` for a non-local account):

```text
auth     [default=1 ignore=ignore success=ok]  pam_localuser.so
auth     sufficient   pam_unix.so nullok
auth     sufficient   pam_sss.so forward_pass
session  optional     pam_oddjob_mkhomedir.so
session  optional     pam_sss.so
```

These files are symbolic links into `/etc/authselect/`, and `authselect check`
verifies that consistency:

```bash
sudo authselect check
```

```text
Current configuration is valid.
```

If one of the files was replaced by a hand-edited copy, the check fails clearly
(return code 3):

```text
[error] [/etc/pam.d/system-auth] is not a symbolic link!
[error] [/etc/pam.d/system-auth] was not created by authselect!
Current configuration is not valid. It was probably modified outside authselect.
```

> On authselect 1.5.2 (AlmaLinux 10), an `authselect select` **without `--force`**
> does not stop in that case: it prints the same errors, adds "These changes will
> be overwritten. Please call 'authselect opt-out' in order to keep them", then
> overwrites anyway. So do not count on the absence of `--force` as a safeguard:
> make a copy of `/etc/pam.d/` before doing anything.

What remains is to start the daemon, and **`oddjobd`** if you asked for
`with-mkhomedir`: `authselect` reminds you of it in its own output.

```bash
sudo systemctl enable --now sssd oddjobd
```

### Checking: resolution, then a real login

The first test does not touch the password, it only checks that the system
**sees** the account:

```bash
getent passwd nlefevre
id nlefevre
getent group redaction
```

```text
nlefevre:*:4201:4200:Nadia Lefevre:/home/nlefevre:/bin/bash
uid=4201(nlefevre) gid=4200(redaction) groups=4200(redaction)
redaction:*:4200:
```

The second exercises the whole PAM chain. A plain `su -` from an unprivileged
account is enough, without touching the SSH configuration:

```bash
su - nlefevre -c id
```

```text
Password:
uid=4201(nlefevre) gid=4200(redaction) groups=4200(redaction) ...
```

On the very first attempt, with `oddjobd` stopped, the login succeeds but the
home is missing: `su: warning: cannot change directory to /home/nlefevre: No
such file or directory`. After `systemctl enable --now oddjobd`,
`pam_oddjob_mkhomedir` does its job and `ls -ld /home/nlefevre` returns
`drwx------. 2 nlefevre redaction`. That account was never created locally, and
yet it logs in, with its group and its home directory.

> The guide describes a "TLS trap": SSSD would refuse to send a password over an
> unencrypted `ldap://` link, hence the
> `ldap_auth_disable_tls_never_use_in_production` directive. Measured on SSSD 2.12
> (AlmaLinux 10), authentication **succeeds without that directive**, and
> `sssctl config-check` rejects it as not allowed. The underlying advice stands:
> in production you encrypt the link (`ldaps://` or
> `ldap_id_use_start_tls = True` with a trusted certificate).

### The SSSD cache: the "I fixed it and nothing changed" failure

SSSD caches identities **and the absence of identities**, on disk, in
`/var/lib/sss/db/`. It is the leading cause of wrong diagnosis. After changing
the user's shell in the directory:

```bash
ldapsearch -x -H ldap://127.0.0.1 -b "dc=atelier,dc=demo" "(uid=nlefevre)" loginShell
getent passwd nlefevre
```

```text
loginShell: /bin/zsh
nlefevre:*:4201:4200:Nadia Lefevre:/home/nlefevre:/bin/bash
```

And above all, **restarting the service is not enough**, since the cache survives
the restart:

```bash
sudo systemctl restart sssd && getent passwd nlefevre   # still /bin/bash
sudo sss_cache -E        && getent passwd nlefevre      # /bin/zsh
```

The negative cache is even more confusing: an account queried **before** it
exists stays untraceable a few seconds after its creation.

```bash
getent passwd tmartin      # rc=2, the account does not exist yet
# ... creation of the entry in the directory ...
getent passwd tmartin      # rc=2: it is the negative cache answering
sudo sss_cache -E
getent passwd tmartin
```

```text
tmartin:*:4202:4200:Theo Martin:/home/tmartin:/bin/bash
```

A reflex to acquire: `sudo sss_cache -E` after **every** change on the directory
side, before concluding anything at all.

### Troubleshooting

`sssctl` (package `sssd-tools`) gives the two most useful answers: is the
configuration valid, and is the domain reachable?

```bash
sudo sssctl config-check
sudo sssctl domain-status ATELIER
```

```text
Issues identified by validators: 0

Online status: Online

Active servers:
LDAP: 10.10.30.14
```

To illustrate the NSS/PAM independence announced at the top of the course:
removing `pam` from the `services =` line of `sssd.conf` leaves
`getent passwd nlefevre` answering, but `su - nlefevre` fails on
`su: Authentication failure`, and the log gives the real reason:
`pam_sss(su-l:auth): Request to sssd failed. Connection refused`. The PAM
responder of SSSD was simply not running.

| Symptom | Likely cause | Check |
|---|---|---|
| `getent passwd` returns nothing although `sssd` is running | `sss` missing from `nsswitch.conf` | `authselect current`, `grep ^passwd: /etc/nsswitch.conf` |
| `sssd` does not start | `sssd.conf` readable by others | `journalctl -u sssd`, then `chmod 0600` |
| Resolution OK, login refused | `pam` missing from `services =`, or PAM not switched | `pam_sss` in `/etc/pam.d/system-auth` |
| A fix has no effect | SSSD cache | `sss_cache -E` (a `restart` is not enough) |
| Login OK but no home | `oddjobd` stopped | `systemctl is-active oddjobd` |
| No shell (`/usr/sbin/nologin`) | the directory does not supply `loginShell` | `default_shell` in `sssd.conf` |
| The user resolves, but not their group | the group is not readable by the bind used | compare anonymous and authenticated `ldapsearch -x` |

The last line deserves a word, because it happened on this machine:
`getent passwd` answered, `getent group` did not, and SSSD had nothing to do with
it. The 389 server only allowed anonymous reading of groups for `groupOfNames`
entries, while the group created was merely a `posixGroup`. An anonymous
`ldapsearch -x` returned nothing, the same `ldapsearch` authenticated did return
the entry. When the two do not give the same result, the problem is in the
directory permissions, not in the client. In production you do not rely on the
anonymous bind anyway: you declare a read-only service account
(`ldap_default_bind_dn` and `ldap_default_authtok`), and you restrict who can log
in with `access_provider = ldap` and a filter.
