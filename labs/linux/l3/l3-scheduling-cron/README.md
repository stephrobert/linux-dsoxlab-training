# Lab — schedule a job with cron

## Reminder

[**cron on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/planification/cron/)

A cron line starts with five time fields, `minute hour day-of-month month
day-of-week`, then the command. System files (`/etc/crontab` and
`/etc/cron.d/`) insert a **user** field between the five fields and the command;
user crontabs (`crontab -e`, `crontab -l`) have none. A field set to `*` means
"every value". The `crond` service must be running.

## The course

The examples below schedule a script `/usr/local/sbin/inventaire` for the
`veille` account, every minute, in `/var/tmp/atelier`: the challenge will ask
you for a different script, a different schedule and a different location. The
goal is to learn the method and above all to know how to **prove** that a job
runs. All the output comes from an AlmaLinux 10 (package `cronie`).

### The daemon first: without it, a perfect crontab does nothing

This is the first reflex, and it saves an hour of searching in the wrong
direction.

```bash
systemctl status crond      # RHEL, Alma, Rocky, Fedora
systemctl status cron       # Debian, Ubuntu
```

```text
● crond.service - Command Scheduler
     Loaded: loaded (/usr/lib/systemd/system/crond.service; enabled; preset: enabled)
     Active: active (running) since Wed 2026-07-22 13:30:02 UTC; 1h 41min ago
   Main PID: 1081 (crond)
```

Two words matter: `running` (it is running now) and `enabled` (it will restart
at boot). If either is missing, `sudo systemctl enable --now crond`.

### The three locations, and how to tell them apart

| Location | User field | Own schedule | Who writes in it |
|---|---|---|---|
| `crontab -e` → `/var/spool/cron/<user>` | no | yes, 5 fields | the user |
| `/etc/crontab` and `/etc/cron.d/*` | **yes**, in 6th position | yes, 5 fields | root, packages |
| `/etc/cron.{hourly,daily,weekly,monthly}/` | no (root) | **no** | root, packages |

A user crontab is edited with `crontab -e`, never by opening the file by hand.
The command validates the syntax before installing, which an editor would not
do:

```bash
echo "* * * * /bin/true" | crontab -      # four time fields only
```

```text
"-":1: bad day-of-week
Invalid crontab file, can't install.
```

It also checks the bounds: `0 25 * * * /bin/true` gives `"-":1: bad hour`. The
file actually produced lives under `/var/spool/cron/`, one file per user, mode
`0600`:

```bash
sudo ls -l /var/spool/cron/
```

```text
-rw-------. 1 veille veille 162 Jul 22 15:11 veille
```

> The guide states `/var/spool/cron/crontabs/`: that is the location on Debian
> and Ubuntu. On this AlmaLinux, the file is directly
> `/var/spool/cron/<user>`. Look in both places.

To read another account's table, use `crontab -l -u <user>` as root. The files
in `/etc/cron.d/` have **six** fields, the user coming before the command, and
nothing requires it to be root:

```text
# m h dom mon dow user command
* * * * * veille /usr/bin/id -un >> /var/tmp/atelier/systeme.log 2>&1
```

Finally, `/etc/cron.hourly/` and the like contain **no** schedule: their scripts
are launched as a batch by another mechanism. It is `/etc/cron.d/0hourly`,
shipped by the package, that gives the time:

```text
01 * * * * root run-parts /etc/cron.hourly
```

### Watching the job run: the only proof that counts

Declaring a job proves nothing. You schedule it **every minute** for as long as
it takes to check it, then you put the real schedule back.

```bash
sudo useradd -m veille
sudo -u veille mkdir -p /var/tmp/atelier
sudo install -m 0755 /dev/stdin /usr/local/sbin/inventaire <<'EOF'
#!/bin/bash
echo "$(date +%H:%M:%S) inventaire lance" >> /var/tmp/atelier/battement.log
EOF
sudo -u veille crontab -e     # write in it:  * * * * * /usr/local/sbin/inventaire
```

Two minutes later, the first proof, the witness file:

```bash
cat /var/tmp/atelier/battement.log
```

```text
15:12:01 inventaire lance
15:13:02 inventaire lance
15:14:01 inventaire lance
```

The second proof, independent of the script: the journal. Mind the filter.

```bash
sudo journalctl _COMM=crond --since "-5min"
```

```text
crond[1081]: (veille) RELOAD (/var/spool/cron/veille)
CROND[22276]: (veille) CMD (/usr/local/sbin/inventaire)
CROND[22390]: (veille) CMDEND (/usr/local/sbin/inventaire)
```

`RELOAD` says the daemon saw the table change, `CMD` that it launched the
command, `CMDEND` that it has finished.

> The guide suggests `journalctl -u crond`. On this machine, that filter returns
> **no** `CMD` line: over the same six-minute window, `-u crond` counts 0 and
> `_COMM=crond` counts 29. The executions are attributed to a
> `session-<n>.scope` and not to `crond.service`; only the messages from the
> daemon itself (such as `BAD FILE MODE`) remain visible with `-u crond`. Use
> `_COMM=crond`, or the file `/var/log/cron` which contains the same lines.

Once the proof is made, you go back to the wanted schedule, for example
`15 4 * * 6` for a Saturday at 04:15.

### The cron environment: trap number one

A job that works at the keyboard and not in cron is almost always the `PATH`.
Let us have `env` executed **by cron** to measure it, rather than assume it:

```bash
# in veille's crontab
* * * * * /usr/bin/env > /var/tmp/atelier/env-cron.txt 2>&1
```

```text
HOME=/home/veille
LANG=en_US.UTF-8
LOGNAME=veille
PATH=/usr/bin:/bin:/usr/sbin:/sbin
PWD=/home/veille
SHELL=/bin/sh
USER=veille
```

Fourteen variables in all, a few `XDG_*` completing the list, against about
twenty in a login session whose `PATH` is much longer:

```text
/home/veille/.local/bin:/home/veille/bin:/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/sbin
```

Three differences to remember:

- cron's `PATH` contains **neither `/usr/local/bin` nor `/usr/local/sbin`**,
  which is exactly where home-made scripts land;
- `SHELL` is `/bin/sh`, not `/bin/bash`: bash conveniences (`[[ ]]`, `source`)
  are not guaranteed there;
- nothing set by `/etc/profile` and `~/.bashrc` is there, neither `MAIL`, nor
  `HISTSIZE`, nor your application's variables.

The demonstration, with the same command written without an absolute path:

```bash
* * * * * inventaire >> /var/tmp/atelier/chemin-relatif.log 2>&1
```

```text
/bin/sh: line 1: inventaire: command not found
```

Hence the rule: **absolute paths everywhere**. If you cannot modify the script,
declare the variables at the top of the crontab, before the job lines:

```text
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
```

### Where the output goes when nobody redirects it

A cron job has no terminal. Its output is mailed to the recipient in `MAILTO`
(`/etc/crontab` sets `MAILTO=root` by default). On this machine, no mail agent
is installed:

```bash
rpm -q postfix s-nail
```

```text
package postfix is not installed
package s-nail is not installed
```

The output does not vanish for all that: `cronie` copies it into the journal
under the `CMDOUT` label. With the line `* * * * * /bin/echo "bilan pret"`:

```text
CROND[22872]: (veille) CMD (/bin/echo "bilan pret")
CROND[22857]: (veille) CMDOUT (bilan pret)
```

Measured: setting `MAILTO=""` at the top of the crontab **does not remove**
those `CMDOUT` lines. `MAILTO` governs mail, not logging. The only way to
control the output is to redirect it yourself:
`>> /var/tmp/atelier/inventaire.log 2>&1` to keep it, `> /dev/null 2>&1` to
throw it away.

One last detail that costs dearly: in a crontab, `%` means "end of command,
what follows is standard input". Compare the two following lines and what the
journal makes of them.

```text
* * * * * /bin/date "+%F"  >> /var/tmp/atelier/pourcent-brut.log 2>&1
* * * * * /bin/date "+\%F" >> /var/tmp/atelier/pourcent-echappe.log 2>&1
```

```text
CROND[22742]: (veille) CMD (/bin/date "+)
CROND[22722]: (veille) CMDOUT (/bin/sh: -c: line 1: unexpected EOF while looking for matching `"')
CROND[22786]: (veille) CMD (/bin/date "+%F" >> /var/tmp/atelier/pourcent-echappe.log 2>&1)
```

The first line is truncated at the `%`: the redirection itself has disappeared
and no file is created. The second, escaped as `\%`, does write its
`2026-07-22`. Escape **every** `%`.

### What cron refuses, and how to undo everything

Three files dropped into `/etc/cron.d/`, three different fates, measured over
three minutes:

| File | Mode | Result |
|---|---|---|
| `atelier-systeme` | `0644` | executed |
| `atelier.avec.point` | `0644` | **executed too** |
| `atelier-droits` | `0666` | never executed |

> Contrary to a widespread belief, `cronie` does **not** reject a file in
> `/etc/cron.d/` whose name contains a dot: `atelier.avec.point` did write its
> three lines. On the other hand, a file writable beyond its owner is
> discarded, and not silently:

```text
crond[1081]: (root) BAD FILE MODE (/etc/cron.d/atelier-droits)
```

This is one of the rare lines that `journalctl -u crond` displays. Files in
`/etc/cron.d/` are laid down as `0644 root:root`.

The sorting of the periodic directories obeys `run-parts`, and you can ask for
it without waiting for the hour:

```bash
sudo run-parts --test /etc/cron.hourly
```

```text
/etc/cron.hourly/0anacron
/etc/cron.hourly/atelier-menage
/etc/cron.hourly/atelier-menage.sh
```

A fourth file, `atelier-non-exec` in `0644`, does not appear: **the execute bit
is mandatory**. The `.sh` one, however, passes.

> The guide writes that `run-parts` ignores files whose name contains a dot.
> That is not true of the version shipped here (package `crontabs`): reading
> `/usr/bin/run-parts` shows a closed list of discarded suffixes (`.rpmsave`,
> `.rpmorig`, `.rpmnew`, `.swp`, `.cfsaved`, `,v`, plus names ending in `~` or
> `,`). That is Debian's rule, not this one. Avoid extensions anyway: they are
> portable nowhere.

Cron also refuses people: `/etc/cron.allow` and `/etc/cron.deny` filter access
to the `crontab` command. Three states measured with `veille`:

| State of the files | `crontab -l` as `veille` |
|---|---|
| `cron.deny` present and empty, no `cron.allow` | displays the table |
| neither of the two | `You (veille) are not allowed to use this program` |
| `cron.allow` containing only `root` | `You (veille) are not allowed to use this program` |

The second case confirms the rule of the RHEL distributions: with neither of
the two files, only root can use cron. If AlmaLinux opens cron to everyone, it
is because it ships an **empty** `/etc/cron.deny`, which must not be deleted
carelessly.

For cleanup, `crontab -r` removes the whole table without confirmation, and `r`
sits next to `e` on the keyboard. `cronie` softens the mistake by keeping a
copy, which `sudo -u veille crontab -r` announces itself:

```text
Backup of veille's previous crontab saved to /home/veille/.cache/crontab/crontab.bak
```

This safety net does not exist everywhere: get into the habit of
`crontab -l > ~/crontab-sauvegarde.txt` before any change, and of
`crontab ~/crontab-sauvegarde.txt` to restore. The full cleanup of the
demonstration, and its verification:

```bash
sudo -u veille crontab -r
sudo rm -f /etc/cron.d/atelier-* /usr/local/sbin/inventaire
sudo rm -rf /var/tmp/atelier
sudo userdel -r veille
sudo crontab -l -u veille    # no crontab for veille
ls /etc/cron.d/              # 0hourly only
```

A forgotten job running every minute is the worst legacy to leave on a server:
never skip those last two lines.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| Nothing fires, no `CMD` line | `crond` stopped, check `systemctl status crond` |
| `journalctl -u crond` looks empty | wrong filter, use `_COMM=crond` or `/var/log/cron` |
| `Invalid crontab file, can't install.` | fewer than five time fields, or a value out of bounds |
| `command not found` in the job's log | cron's `PATH` is reduced, use an absolute path |
| The script works at the keyboard, not in cron | profile variables absent, `SHELL=/bin/sh` |
| The command is truncated in `CMD (...)` | an unescaped `%`, write `\%` |
| A file in `/etc/cron.d/` is ignored | mode too permissive, look for `BAD FILE MODE` in the journal |
| A script in `/etc/cron.hourly/` does not run | execute bit missing, check with `run-parts --test` |
| `You (…) are not allowed to use this program` | `/etc/cron.allow` or `/etc/cron.deny` |
| No trace of the output | neither redirection nor mail agent, look at the `CMDOUT` lines |
