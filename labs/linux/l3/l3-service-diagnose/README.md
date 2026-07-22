# Lab — Diagnose a systemd service stuck in a crash loop

## Reminder

[**Troubleshoot a Linux service that does not start with systemd**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/service-ne-demarre-pas/)

A service whose `ExecStart` always fails for the same reason, and which a
`Restart=` directive restarts endlessly, goes into a restart loop. The guide
reduces troubleshooting to five steps: read the state, read the logs, check the
configuration, fix, restart and verify. Two commands answer the vast majority of
cases, `systemctl status` and `journalctl`. The exit code guides the diagnosis:
below 125 it comes from the program itself, from 200 upwards it is systemd that
failed to prepare the execution environment, and the error is then in the unit,
not in the program.

## The course

The examples below are about a demonstration service, `releve-metriques`, built
for the occasion on a workshop machine: the challenge hands you another service,
under another name, with another failure. What transposes is not a repair
command, it is an order of reading.

### Three readings, always in the same order

This lab teaches a method. It fits in three gestures, and the order matters as
much as the commands:

1. `systemctl status <unit>` gives the state, the exit code and the last ten
   journal lines;
2. `journalctl -u <unit> -b --no-pager` gives the complete journal of that unit
   for the current boot;
3. in that journal, you look for the **first** error message, not the last.

That third rule is the one that separates the beginner from the practitioner.
Here is why, measured on the workshop machine. The `releve-metriques` service is
looping, and here is the end of its journal:

```text
Jul 22 15:47:16 atelier systemd[1]: releve-metriques.service: Scheduled restart job, restart counter is at 4.
Jul 22 15:47:18 atelier systemd[1]: releve-metriques.service: Scheduled restart job, restart counter is at 5.
Jul 22 15:47:18 atelier systemd[1]: releve-metriques.service: Start request repeated too quickly.
Jul 22 15:47:18 atelier systemd[1]: Failed to start releve-metriques.service - Releve de metriques (atelier).
```

Those four lines say nothing about the failure. They describe the end of a loop,
that is, a symptom of the fifth attempt. The cause is at the top of the same
journal:

```text
Jul 22 15:47:12 atelier systemd[1]: Started releve-metriques.service - Releve de metriques (atelier).
Jul 22 15:47:12 atelier releve-metriques[1338]: erreur: fichier de configuration illisible: /etc/releve-metriques.conf
Jul 22 15:47:12 atelier systemd[1]: releve-metriques.service: Main process exited, code=exited, status=78/CONFIG
```

Hence the reflex: `journalctl -u <unit> -b --no-pager | head -20`, never `tail`.

> **The journal is not necessarily kept from one boot to the next.** On the
> workshop machine, `/var/log/journal` does not exist: the journal lives in
> memory and `journalctl --list-boots` knows only one boot. Concretely,
> rebooting the machine erases the evidence. You diagnose **before** rebooting,
> and you check the situation with `ls -d /var/log/journal`.

### Signature 1: the binary could not be started (`203/EXEC`)

First failure: the unit points at an `ExecStart` that does not exist.

```bash
systemctl status releve-metriques.service
```

```text
● releve-metriques.service - Releve de metriques (atelier)
     Loaded: loaded (/etc/systemd/system/releve-metriques.service; disabled; preset: disabled)
     Active: activating (auto-restart) (Result: exit-code) since Wed 2026-07-22 15:43:22 UTC; 809ms ago
    Process: 3530 ExecStart=/usr/local/sbin/releve-metriques (code=exited, status=203/EXEC)
   Main PID: 3530 (code=exited, status=203/EXEC)
```

Three hints can be read at once: `activating (auto-restart)` (the service is not
stable, systemd is between two attempts), `Result: exit-code` (the process died
by itself, it was not killed) and `status=203/EXEC`. The journal names the
cause:

```text
(etriques)[3527]: releve-metriques.service: Unable to locate executable '/usr/local/sbin/releve-metriques': No such file or directory
(etriques)[3527]: releve-metriques.service: Failed at step EXEC spawning /usr/local/sbin/releve-metriques: No such file or directory
```

Beware of the trap: the same `203/EXEC` code covers two distinct causes. By
dropping the script without giving it the execute bit (`-rw-r--r--`), the code
does not change, but the message does:

```text
(etriques)[3720]: releve-metriques.service: Unable to locate executable '/usr/local/sbin/releve-metriques': Permission denied
```

`No such file or directory` points at the path, `Permission denied` at the mode.
The code alone is therefore not enough, it is the pair code plus message that
decides.

### Signature 2: the program refuses its configuration

Once the script is made executable, the loop continues, but the signature
changes completely:

```text
    Process: 3798 ExecStart=/usr/local/sbin/releve-metriques (code=exited, status=78)
   Main PID: 3798 (code=exited, status=78)
```

```text
releve-metriques[3795]: erreur: fichier de configuration illisible: /etc/releve-metriques.conf
systemd[1]: releve-metriques.service: Main process exited, code=exited, status=78/CONFIG
```

Here the code is **below 125**, so it comes from the program and not from
systemd. The message that comes with it is emitted by the program itself (note
the `releve-metriques[3795]` prefix instead of `systemd[1]`): it is the one that
says which file it is missing. A useful nuance: `systemctl status` displays a
raw `78`, while the journal translates `78/CONFIG`, because systemd knows the
`sysexits.h` convention.

A file that is present but incorrect gives the same code and another message.
With a misspelled key in `/etc/releve-metriques.conf`:

```text
releve-metriques[3835]: erreur: cle intervalle absente ou non numerique dans /etc/releve-metriques.conf (lu: '')
```

In other words, as soon as the code is an application code, the program's
journal is the only useful source, and you have to go and read what the program
expects (`systemctl cat <unit>` gives the path of the `ExecStart`, which you can
then open).

### Signature 3: systemd could not prepare the execution (`217/USER`, `200/CHDIR`)

Third family: the program never started, systemd failed before that. By adding
to the unit a working directory that does not exist:

```text
    Process: 3960 ExecStart=/usr/local/sbin/releve-metriques (code=exited, status=200/CHDIR)
```

```text
(etriques)[3957]: releve-metriques.service: Changing to the requested working directory failed: No such file or directory
(etriques)[3957]: releve-metriques.service: Failed at step CHDIR spawning /usr/local/sbin/releve-metriques: No such file or directory
```

By additionally adding a `User=` that does not exist on the machine:

```text
    Process: 4066 ExecStart=/usr/local/sbin/releve-metriques (code=exited, status=217/USER)
```

```text
(etriques)[4064]: releve-metriques.service: Failed to determine user credentials: No such process
(etriques)[4064]: releve-metriques.service: Failed at step USER spawning /usr/local/sbin/releve-metriques: No such process
```

Two lessons. First, the name of the step (`Failed at step USER`, `step CHDIR`,
`step EXEC`) directly designates the faulty directive: `User=`,
`WorkingDirectory=`, `ExecStart=`. Second, on the workshop machine both faults
were present at the same time and only `217/USER` came up: systemd stops at the
first step that fails. Fixing one cause can therefore reveal another, and you
have to read the status again after each fix.

Another detail to know so as not to get lost: in those lines, the sender is not
`systemd[1]` but `(etriques)[3957]`. That is the child process systemd has just
forked, whose name is truncated. It is not another program.

### Two tools that save time

**`systemctl show -p <property>` queries the effective state**, not the file on
disk. The difference is far from theoretical: a fragment dropped in
`/etc/systemd/system/<unit>.service.d/` changes the behaviour without modifying
the main file. On the workshop machine, the main file contains `RestartSec=2s`
and yet:

```bash
systemctl show releve-metriques.service -p Restart -p RestartUSec -p FragmentPath -p DropInPaths
```

```text
Restart=always
RestartUSec=1s
FragmentPath=/etc/systemd/system/releve-metriques.service
DropInPaths=/etc/systemd/system/releve-metriques.service.d/10-atelier.conf
```

Two traps in that output: the property being queried does not always carry the
name of the directive (`RestartSec=` in the file becomes `RestartUSec=` in
`show`), and `DropInPaths` is the only quick way to know that an override
exists. `systemctl cat <unit>` displays the fragments one after the other,
`show` gives the result of their merge. The `--value` option returns only the
value, which makes the call scriptable:

```bash
for p in ActiveState SubState ExecMainStatus NRestarts; do
    printf "%-15s %s\n" "$p" "$(systemctl show releve-metriques.service -p "$p" --value)"
done
```

```text
ActiveState     failed
SubState        failed
ExecMainStatus  78
NRestarts       5
```

**`journalctl -u <unit> -b --no-pager -o short-precise` timestamps to the
millisecond**, which makes the pace of the loop visible:

```text
15:47:15.696923 releve-metriques[1343]: erreur: fichier de configuration illisible: /etc/releve-metriques.conf
15:47:16.957531 releve-metriques[1345]: erreur: fichier de configuration illisible: /etc/releve-metriques.conf
15:47:18.208049 systemd[1]: releve-metriques.service: Scheduled restart job, restart counter is at 5.
15:47:18.208454 systemd[1]: releve-metriques.service: Start request repeated too quickly.
15:47:18.208506 systemd[1]: Failed to start releve-metriques.service - Releve de metriques (atelier).
```

One cycle roughly every 1.25 second, and above all an end. By default, systemd
tolerates `StartLimitBurst=5` starts per `StartLimitIntervalSec=10s` window;
beyond that, it gives up, says so explicitly (`Start request repeated too
quickly`) and switches the unit to `failed`. A service that is no longer looping
is therefore not necessarily repaired: it may simply have given up. Always check
`NRestarts` and the actual state.

> **A loop that is too slow never reaches the limit.** With the `RestartSec=2s`
> of the original file, the workshop machine counted 21 restarts without ever
> triggering the safeguard: a 2.25 second cycle just fits inside the 10 seconds
> of the window. The service then goes round in circles indefinitely, without
> ever going `failed`, and does not appear in `systemctl list-units --failed`.

### `active` is not `enabled`: proof by reboot

A fix is only finished if it survives the reboot. After putting the expected
configuration in place, the service starts again:

```bash
systemctl is-active releve-metriques.service   # active
systemctl is-enabled releve-metriques.service  # disabled
```

The two answers coexist without contradiction: `is-active` describes now,
`is-enabled` describes the next boot. The `Loaded:` line of `systemctl status`
already says it, by the way, in parentheses after the path of the unit. A
`systemctl reboot` settles the matter:

```text
$ systemctl is-active releve-metriques.service
inactive
$ systemctl is-enabled releve-metriques.service
disabled
```

The service repaired the day before is dead on waking. `enable` creates the
missing symbolic link, in the directory designated by the `[Install]` section of
the unit:

```bash
sudo systemctl enable --now releve-metriques.service
```

```text
Created symlink '/etc/systemd/system/multi-user.target.wants/releve-metriques.service' → '/etc/systemd/system/releve-metriques.service'.
```

Second reboot, same check:

```text
$ systemctl is-active releve-metriques.service
active
$ systemctl is-enabled releve-metriques.service
enabled
```

`enable --now` combines `enable` and `start`. Note finally that `is-active` and
`is-enabled` also return an exit code usable in a script: `0` when the answer is
positive, `3` for `inactive` and `1` for `disabled`.

### Troubleshooting

| What you see | What to look at |
|---|---|
| `Active: activating (auto-restart)` | the loop is running, go back up to the first journal message |
| `status=203/EXEC` + `No such file or directory` | the path of `ExecStart=` is wrong |
| `status=203/EXEC` + `Permission denied` | the execute bit is missing on the binary |
| `status=200/CHDIR` | `WorkingDirectory=` designates a directory that is absent |
| `status=217/USER` | the `User=` of the unit does not exist on the machine |
| code below 125 | the program stopped itself, read its own journal lines |
| `Start request repeated too quickly` | the start limit is reached, the service gave up |
| The journal shows nothing before the reboot | volatile journal, `/var/log/journal` is absent |
| The modified unit changes nothing | `daemon-reload` forgotten, or a drop-in wins (`systemctl show -p DropInPaths`) |

To remove a demonstration service and start from a clean machine:

```bash
sudo systemctl disable --now <unit>
sudo rm -f /etc/systemd/system/<unit>.service
sudo rm -rf /etc/systemd/system/<unit>.service.d
sudo systemctl daemon-reload
sudo systemctl reset-failed
systemctl list-units --failed        # must list 0 units
```

`reset-failed` clears the `failed` state and resets the restart counter to zero.
Without it, a unit that has been fixed can still be shown as failed.
