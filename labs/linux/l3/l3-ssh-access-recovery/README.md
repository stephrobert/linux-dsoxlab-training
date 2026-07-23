# Lab — recover a broken sshd config

## Reminder

[**Lost SSH access on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/depanner/perte-acces-ssh/)

sshd reads `/etc/ssh/sshd_config` and the drop-ins under
`/etc/ssh/sshd_config.d/`. `sshd -t` validates the config offline — a broken
config only bites on the next reload/reboot, so **always** run `sshd -t` before
reloading. `sshd -T` dumps the effective settings. `systemctl reload sshd`
applies a valid config without dropping connections.

## The course

The examples below deal with a throwaway account named `depanne`, with a file
`60-atelier.conf` and with the `LoginGraceTime` directive: the challenge will
have you work on a different file and a different directive. What you must take
away from here is a **diagnosis method**, not a line to copy.

All the output was collected on an AlmaLinux 10.2, OpenSSH_9.9p1, SELinux in
`Enforcing`.

> **Warning.** Learning to repair SSH access assumes you break one. Two rules
> make the exercise safe, and they are not negotiable. First, open a **second
> session** before starting and keep it open: an already established session
> survives anything, it is your only door. Second, break the access of an
> **account you have just created**, never your own: every failure in this
> course was reproduced on `depanne`, without ever putting the working session
> at stake.

### Qualifying the refusal before touching the server

The client message already sorts the causes into three families, which have
neither the same culprit nor the same procedure.

| What the client says | Meaning | Likely culprit |
|---|---|---|
| `Connection refused` | the server answers, but **nothing is listening** on that port | `sshd` stopped, or listening elsewhere |
| `Connection timed out` | **no answer at all**, the packets are dropped silently | firewall, security group, machine powered off |
| `Permission denied (publickey)` | the connection **succeeds**, it is the **authentication** that fails | key, permissions of `authorized_keys`, or account |

The first two are reproduced with one command, without breaking anything:

```bash
ssh -o ConnectTimeout=5 -p 2222 depanne@127.0.0.1 true
ssh -o ConnectTimeout=5 depanne@10.255.255.1 true
```

```text
ssh: connect to host 127.0.0.1 port 2222: Connection refused
ssh: connect to host 10.255.255.1 port 22: Connection timed out
```

A refusal proves the machine is alive and reachable: the network is fine, the
problem is on the service. A timeout says nothing about the service. So first
check who is listening, and on which port:

```bash
sudo ss -tlnp | grep -E ':22\b'
```

```text
LISTEN 0      128          0.0.0.0:22        0.0.0.0:*    users:(("sshd",pid=1104,fd=7))
LISTEN 0      128             [::]:22           [::]:*    users:(("sshd",pid=1104,fd=8))
```

The rest of this course deals with the third column, the only one where the
server tells you nothing.

### Never modify the main file

`/etc/ssh/sshd_config` starts with `Include /etc/ssh/sshd_config.d/*.conf`.
Dropping a file of your own into that directory is better than editing the main
file: rolling back comes down to deleting the file, with no risk of damaging
the original. Back the directory up all the same beforehand:

```bash
sudo cp -a /etc/ssh/sshd_config.d /root/sshd_config.d.orig
```

The number at the front of the name is not decorative. For most directives,
`sshd` keeps the **first value encountered**, unlike `sudoers` where the last
one wins. As the `Include` sits at the top of the main file, the files in
`sshd_config.d/` are read before it, in the lexical order of their names.
Measured with two files dropped for the occasion:

```bash
sudo grep -r LoginGraceTime /etc/ssh/sshd_config.d/
sudo sshd -T | grep -i '^logingracetime'
```

```text
/etc/ssh/sshd_config.d/60-atelier.conf:LoginGraceTime 45
/etc/ssh/sshd_config.d/10-atelier.conf:LoginGraceTime 90
logingracetime 90
```

It is indeed `10-` that wins. So prefix your settings with a **low** number to
come ahead of those of the distribution and of cloud-init, and never conclude
without `sshd -T`.

### Validate before applying

An invalid value dropped into a drop-in breaks nothing straight away: the
running `sshd` keeps in memory the configuration it read at start-up.

```bash
sudo sshd -t; echo "code retour = $?"
systemctl is-active sshd
```

```text
/etc/ssh/sshd_config.d/60-atelier.conf line 2: invalid time value.
code retour = 255
active
```

The message names the **file** and the **line**: that is the complete
diagnosis, and it costs nothing. Note in passing that `sshd -T` fails with
exactly the same error: as long as the configuration is invalid, you can no
longer read the effective values.

The mine is armed for the next reload. `systemctl cat sshd.service` shows why:

```text
ExecReload=/bin/kill -HUP $MAINPID
```

A `reload` sends a `SIGHUP`, on which `sshd` restarts itself by re-reading its
configuration. If that configuration is invalid, the process that carried the
listening socket stops: nothing left on port 22, and every new connection gets
a `Connection refused`. A reboot produces the same result. Your current
session, on the other hand, survives: it is carried by an already forked
process.

Hence the sequence, in this order, on every change:

```bash
sudo sshd -t                          # 1. syntax, silence = success
sudo sshd -T | grep -i '<directive>'  # 2. value actually in effect
sudo systemctl reload sshd            # 3. reload, never restart
ssh user@server                       # 4. NEW test session
```

`reload` re-reads the configuration without dropping established sessions,
`restart` kills them. To check an isolated file before dropping it in,
`sshd -t -f` accepts a path:

```bash
sudo sshd -t -f /tmp/essai.conf; echo "code retour = $?"
```

```text
/tmp/essai.conf line 2: invalid time value.
code retour = 255
```

One last warning: `sshd -t` only validates the **grammar**, never the access
logic. An `AllowUsers` that forgets you passes `sshd -t` with exit code 0.

### One single client message, three server reasons

This is the heart of the matter. Four unrelated failures were provoked on the
`depanne` account, and the client almost always says the same thing. The
server, for its part, knows exactly why:

| Failure provoked | What the client sees | What `journalctl -u sshd` says |
|---|---|---|
| `~/.ssh` in `770` | `Permission denied (publickey,...)` | `Authentication refused: bad ownership or modes for directory /home/depanne/.ssh` |
| non-existent shell for the account | `Permission denied (publickey,...)` | `User depanne not allowed because shell /sbin/pas-de-shell does not exist` |
| account outside `AllowUsers` | `Permission denied (publickey,...)` | `User depanne from 127.0.0.1 not allowed because not listed in AllowUsers` |
| `authorized_keys` missing | `Permission denied (publickey,...)` | *(no explicit line)* `Connection closed by authenticating user depanne` |
| expired account (`chage -E`) | `Connection closed by 127.0.0.1 port 22` | `fatal: Access denied for user depanne by PAM account configuration` |

Three lessons. The first: **the client message is not a diagnosis**, it is an
acknowledgement of refusal. The server stays deliberately vague so as to teach
nothing to whoever would probe the accounts. The second: the last line is the
exception that confirms the rule, a **PAM** refusal happens after the key has
been validated and produces a different message. The third: a key that is
simply missing leaves **no** explicit trace, it is deduced from the silence.

Hence the order of diagnosis, from the most talkative to the most detailed:

**1. The server journal**, always first, it is the one that has the answer:

```bash
sudo journalctl -u sshd --since '-2min' --no-pager
```

```text
Jul 22 17:15:19 atelier.lab sshd-session[3448]: Authentication refused: bad ownership or modes for directory /home/depanne/.ssh
Jul 22 17:15:19 atelier.lab sshd-session[3448]: Connection closed by authenticating user depanne 127.0.0.1 port 54018 [preauth]
```

Note the name of the process: `sshd-session`, and not `sshd`. Since OpenSSH 9.8
the session is carried by a separate binary. Filtering on the string `sshd`
would miss the line; `journalctl -u sshd` follows the unit, child processes
included.

**2. `ssh -vvv` on the client side**, when the journal is not enough. On the
same failure:

```bash
ssh -vvv -i ~/.ssh/depanne_key depanne@127.0.0.1 true 2>&1 | grep -iE 'Offering|continue|denied'
```

```text
debug1: Authentications that can continue: publickey,gssapi-keyex,gssapi-with-mic
debug1: Offering public key: /home/ansible/.ssh/depanne_key ED25519 SHA256:ZXi+Vtuh7NQzQ2ZPpg4jg6JqQxUHjhuBFeqQ5fBuEVc explicit
depanne@127.0.0.1: Permission denied (publickey,gssapi-keyex,gssapi-with-mic).
```

The client says **which** key it offered and in which order, never why it was
rejected. That is useful when you suspect the wrong key is being sent, useless
for everything else.

**3. `sshd -T`** last, to confront what you think you configured with what
`sshd` really applies. Example on the allow list:

```bash
sudo sshd -T | grep -iE '^(allowusers|strictmodes)'
```

```text
allowusers ansible
allowusers student
strictmodes yes
```

An allow list is written by putting in it **first** the accounts you depend on,
and it is tested on a throwaway account. Once reloaded, `depanne` is refused
even though its key and its permissions are perfect.

> **A trap in OpenSSH 9.8 and later.** After a few authentication failures close
> together, the source is put under penalty and the following connections are
> cut before authentication even happens, with a misleading message:
> `kex_exchange_identification: read: Connection reset by peer`. The journal
> says `drop connection ... penalty: failed authentication`. In the middle of a
> diagnosis session, you believe you have made the failure worse. The settings
> are visible with `sshd -T | grep -i persource`; on the test machine the
> penalty had lapsed in less than twenty seconds.

### The exact rule on permissions, measured

Permission failures are the most frequent, and the common approximation ("600
and 700, otherwise it does not work") is wrong. Here is what was measured, case
by case, on the test account:

| State of `~depanne/.ssh` and of `authorized_keys` | Result |
|---|---|
| directory `700 depanne` / file `600 depanne` | accepted |
| directory `750 depanne` / file `600` | accepted |
| directory `755 depanne` / file `600` | accepted |
| directory `770 depanne` (group writable) | **refused** |
| directory `700 root:root` | **refused** |
| file `644 depanne` | accepted |
| file `664 depanne` (group writable) | **refused** |
| file `606 depanne` (world writable) | **refused** |
| file `600 root:root` | **refused** |
| **home** `/home/depanne` in `770` | **refused** |

What this table establishes: `sshd` refuses as soon as an **account other than
the owner can write**, or as soon as the owner is not the right one. A file
merely **readable** by everyone still passes, and the check goes all the way up
to the **home directory**, which is almost always forgotten. That is no reason
to leave a `644`: `700` on the directory and `600` on the file remain the
target, because that is what every audit checks. But when you are diagnosing,
look first for a **write permission** or an **owner** out of place.

The journal in fact distinguishes two situations that the client conflates:

```text
Authentication refused: bad ownership or modes for directory /home/depanne/.ssh
Could not open user 'depanne' authorized keys '/home/depanne/.ssh/authorized_keys': Permission denied
```

The first line is the refusal by `StrictModes` on permissions that are too
wide. The second appears when the file or its directory belongs to **root**:
`sshd` drops its privileges to read the file on behalf of the user, and can no
longer do it. The fix, in both cases:

```bash
sudo chown -R depanne:depanne /home/depanne/.ssh
sudo chmod 700 /home/depanne/.ssh
sudo chmod 600 /home/depanne/.ssh/authorized_keys
sudo restorecon -Rv /home/depanne/.ssh
```

### When no session gets through any more

If the service is down and you have no session open any more, none of the
commands in this course are available: you need a console, that is, an access
that does not depend on `sshd`.

- **The console of the hypervisor or of the provider.** On a libvirt machine,
  `virsh list --all` then `virsh console <domain>` give a serial terminal. At a
  hosting provider, it is the "VNC console" or "serial console" of the
  administration interface.
- **Emergency mode**, when the machine does not even get as far as the login: at
  the GRUB menu, `e` then `systemd.unit=emergency.target` on the kernel line.
  The targets do exist (`systemctl list-units --type=target --all` lists
  `rescue.target` and `emergency.target`).
- **Mounting the disk from another machine**, as a last resort: you attach the
  disk to a healthy system, you fix `/etc/ssh/sshd_config.d/`, you detach it.

These three routes were not executed to write this course: the test machine
stayed reachable from beginning to end, precisely because the failures were
provoked on a third-party account. Above all, remember that the best console is
the one you do not need: a second session left open during the operation costs
three seconds and saves you the trip.

### Troubleshooting

| Symptom | Likely cause | Check |
|---|---|---|
| `Connection refused` | `sshd` stopped, or invalid config re-read at the last reload | `systemctl is-active sshd`, `sudo sshd -t` |
| `Connection timed out` | firewall, or machine powered off | `firewall-cmd --list-all` from the console |
| `Permission denied (publickey)`, journal `bad ownership or modes` | permissions too wide on `~/.ssh`, the file or the home | `stat -c '%a %U:%G' ~/.ssh ~/.ssh/authorized_keys` |
| `Permission denied (publickey)`, journal `Could not open ... Permission denied` | root owner on the file or the directory | `chown -R <user>:<user> ~<user>/.ssh` |
| `Permission denied (publickey)`, journal `not listed in AllowUsers` | allow list on the server side | `sudo sshd -T \| grep -i allowusers` |
| `Access denied ... by PAM account configuration` | expired or locked account | `chage -l <user>`, `passwd -S <user>` |
| a setting has no effect | another occurrence, read earlier, wins | `sudo sshd -T`, then `grep -r` in `sshd_config.d/` |
| `Connection reset by peer` in bursts | `PerSourcePenalties` penalty after failures | `sudo sshd -T \| grep -i persource`, wait |
| `sshd -t` green but the service refuses to start | non-standard port, SELinux, host key | `journalctl -u sshd -n 20`, `ausearch -m avc -ts recent` |

The case of the non-standard port blocked by SELinux, a RHCSA classic, is
covered in detail in the companion guide linked above.

To undo everything after an exercise of this kind:

```bash
sudo rm -f /etc/ssh/sshd_config.d/60-atelier.conf
sudo sshd -t && sudo systemctl reload sshd
sudo userdel -r depanne
ssh user@server          # a NEW session, the only proof that counts
```
