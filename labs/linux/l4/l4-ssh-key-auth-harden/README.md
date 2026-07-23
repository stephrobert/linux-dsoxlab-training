# Lab — hardened key-based SSH for a service user

## Reminder

[**SSH keys on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/ssh/cle-ssh/)

`sshd` enforces strict permissions on key files: `~/.ssh` must be `0700` and
owned by the user, `authorized_keys` must be `0600` and owned by the user. Too
open, or owned by someone else, and the key is **silently ignored**. Read them
with `stat -c '%a %U:%G'`.

## The course

The examples below deal with a service account named `sonde` and with keys made
for the occasion. The challenge will have you work on another account and other
files: the goal is to learn the method and the checking reflexes, not to copy a
line.

All the outputs in this course were taken on an AlmaLinux 10, OpenSSH_9.9p1,
SELinux in `Enforcing`.

> **Warning.** This course modifies the configuration of the very service you
> are connected through. Before any change to `sshd`, open a **second session**
> and keep it open until validation. It is your only safety net.

### Build a key pair

`ssh-keygen` produces two inseparable files: the **private key**, which never
leaves the client machine, and the **public key** (`.pub`), which is made to be
distributed to servers.

```bash
ssh-keygen -t ed25519 -C "sonde@atelier"
```

```text
Generating public/private ed25519 key pair.
Enter file in which to save the key (/home/ansible/.ssh/id_ed25519):
Enter passphrase for "/home/ansible/.ssh/id_ed25519" (empty for no passphrase):
Enter same passphrase again:
Your identification has been saved in /home/ansible/.ssh/id_ed25519
Your public key has been saved in /home/ansible/.ssh/id_ed25519.pub
The key fingerprint is:
SHA256:eIkhcUdYg2tDanqBuoN2taSnjSN+11IiQazjJ4P6bLw sonde@atelier
[...]
```

Three questions, three answers: the location (Enter for the default), then the
passphrase twice. The guide recommends **Ed25519** since OpenSSH 6.5: a shorter
key, faster, as safe as an RSA 4096. You keep `-t rsa -b 4096` only to talk to
systems too old for Ed25519.

`ssh-keygen` sets the right permissions itself, which can be checked:

```bash
ls -l ~/.ssh/id_ed25519 ~/.ssh/id_ed25519.pub
```

```text
-rw-------. 1 ansible ansible 399 Jul 22 16:25 /home/ansible/.ssh/id_ed25519
-rw-r--r--. 1 ansible ansible  95 Jul 22 16:25 /home/ansible/.ssh/id_ed25519.pub
```

`600` on the private key, `644` on the public one: that is the rule, and it is
respected by default. Trouble starts when a file has travelled (copy, archive,
`scp`) and lost its permissions on the way.

### Install the public key on the target account

Two methods, the same purpose: add a line in the `~/.ssh/authorized_keys` file
of the target account, **on the server**.

The manual method is the one expected in an exam, and the only possible one
when password login is already closed:

```bash
sudo install -d -o sonde -g sonde -m 700 /home/sonde/.ssh
echo 'ssh-ed25519 AAAA... sonde@atelier' | sudo tee -a /home/sonde/.ssh/authorized_keys
sudo chown sonde:sonde /home/sonde/.ssh/authorized_keys
sudo chmod 600 /home/sonde/.ssh/authorized_keys
sudo restorecon -Rv /home/sonde/.ssh
```

`install -d` sets the owner and the mode in a single go, which avoids the
window during which the directory exists with the wrong permissions.
`restorecon` restores the expected SELinux context (`ssh_home_t`) on files
created by hand: on the test machine the context was already correct and the
command printed nothing, but the reflex costs nothing.

The other method, `ssh-copy-id`, does the same job from the client:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub sonde@127.0.0.1
```

It has the advantage of never getting the permissions wrong, as reading the
script itself confirms (`ssh-copy-id` is a shell script):

```bash
grep -nE "mkdir|chmod" /usr/bin/ssh-copy-id | head -4
```

```text
333:	-mkdir "$AUTH_KEY_DIR"
334:	chmod 700 "$AUTH_KEY_DIR"
336:	chmod 600 "$AUTH_KEY_FILE"
```

Always check the result, then the connection:

```bash
sudo stat -c '%a %U:%G %n' /home/sonde/.ssh /home/sonde/.ssh/authorized_keys
ssh -i ~/.ssh/id_ed25519 sonde@127.0.0.1 'id -un'
```

```text
700 sonde:sonde /home/sonde/.ssh
600 sonde:sonde /home/sonde/.ssh/authorized_keys
sonde
```

### Permissions: failure number one

On the **client** side, a private key readable by others is refused by `ssh`
itself, before the server is even contacted. The message leaves no doubt:

```bash
chmod 644 ~/.ssh/id_ed25519
ssh -i ~/.ssh/id_ed25519 sonde@127.0.0.1
```

```text
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
@         WARNING: UNPROTECTED PRIVATE KEY FILE!          @
@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
Permissions 0644 for '/home/ansible/.ssh/id_ed25519' are too open.
It is required that your private key files are NOT accessible by others.
This private key will be ignored.
Load key "/home/ansible/.ssh/id_ed25519": bad permissions
sonde@127.0.0.1: Permission denied (publickey,gssapi-keyex,gssapi-with-mic).
```

Fix: `chmod 600` on the private key.

On the **server** side, `sshd` applies the same kind of check, but **without
telling the client anything**. Here is what was measured, case by case, on the
test account:

| State of `~sonde/.ssh` and of `authorized_keys` | Result |
|---|---|
| `700 sonde:sonde` / `600 sonde:sonde` | connection accepted |
| directory `770 sonde:sonde` (group-writable) | **refused** |
| directory `755 root:root` (wrong owner) | **refused** |
| `authorized_keys` at `660` (group-writable) | **refused** |
| `authorized_keys` at `644`, directory `700 sonde:sonde` | accepted |

What this table teaches: `sshd` refuses as soon as **an account other than the
owner can write** in the directory or in the file, or as soon as the directory
does not belong to the right user. An `authorized_keys` that is merely
**readable** by everyone still gets through. That is no reason to leave it that
way: `700` and `600` remain the target, because that is what every audit checks
and because there is no margin for error. But when you are diagnosing, look
first for a **write permission** or a wrong **owner**.

The server log names the culprit precisely:

```text
Authentication refused: bad ownership or modes for directory /home/sonde/.ssh
Authentication refused: bad ownership or modes for file /home/sonde/.ssh/authorized_keys
```

### Read the effective configuration with `sshd -T`

This is the most important point of hardening, and the same principle as
`systemctl show` for systemd: **the file does not tell the truth, the command
does**. `sshd -T` prints the configuration as `sshd` understands it, with all
includes resolved.

The demonstration takes two commands on an AlmaLinux 10 fresh out of its
installation:

```bash
sudo grep -n -iE '^#?PasswordAuthentication' /etc/ssh/sshd_config
sudo sshd -T | grep -i '^passwordauthentication'
```

```text
65:#PasswordAuthentication yes
passwordauthentication no
```

The main file seems to announce `yes` (commented line, so the OpenSSH default).
The value actually applied is `no`. It comes from elsewhere:

```bash
sudo grep -r . /etc/ssh/sshd_config.d/ | grep -i password
```

```text
/etc/ssh/sshd_config.d/50-cloud-init.conf:PasswordAuthentication no
```

Anyone auditing this server by reading `/etc/ssh/sshd_config` would have been
wrong. `sshd -T` requires root privileges, because it also reads the host keys.

### The first occurrence wins

On RHEL, AlmaLinux, Debian and Ubuntu, `/etc/ssh/sshd_config` starts with:

```text
Include /etc/ssh/sshd_config.d/*.conf
```

Now `sshd` keeps, for most directives, the **first value encountered**, unlike
`sudoers` where the last one wins. Since the `Include` comes first, the files in
`sshd_config.d/` are read **before** the body of the main file, and in the
lexical order of their names.

Verification, with two files dropped in for the occasion:

```bash
sudo grep -r MaxAuthTries /etc/ssh/sshd_config.d/
sudo sshd -T | grep -i '^maxauthtries'
```

```text
/etc/ssh/sshd_config.d/00-demo-atelier.conf:MaxAuthTries 4
/etc/ssh/sshd_config.d/99-demo-atelier.conf:MaxAuthTries 2
maxauthtries 4
```

It really is `00-` that wins. Hence two working rules: prefix your settings
with a **low** number (`00-hardening.conf`) to come ahead of the files dropped
by the distribution or by cloud-init, and never conclude without `sshd -T`.

Working in a file of your own under `sshd_config.d/` rather than in
`sshd_config` has another merit: reverting comes down to deleting that file,
with no risk of damaging the original file.

### Harden without locking yourself out

The order of the steps is not negotiable. `sshd -t` validates the **syntax**
and returns 255 with the name of the file and the offending line:

```bash
sudo sshd -t; echo "return code = $?"
```

```text
/etc/ssh/sshd_config.d/99-demo-atelier.conf: line 2: Bad configuration option: PermitRootLogn
/etc/ssh/sshd_config.d/99-demo-atelier.conf: terminating, 1 bad configuration options
return code = 255
```

One undetected typo and the service refuses to restart: you stay outside as
soon as the current session drops. Once fixed, `sshd -t` says nothing more and
returns 0: silence is success.

The full sequence, in four steps:

```bash
sudo sshd -t                                       # 1. syntax
sudo sshd -T | grep -iE 'allowusers|passwordauth'  # 2. effective values
sudo systemctl reload sshd                         # 3. reload, not restart
ssh user@server                                    # 4. NEW test session
```

`reload` re-reads the configuration **without cutting established sessions**;
`restart` kills them. On RHEL and AlmaLinux the service is called `sshd`, on
Debian and Ubuntu historically `ssh`.

Careful: `sshd -t` only validates the grammar, never the access logic. An
`AllowUsers` that forgets you passes `sshd -t` without flinching. That
directive is the whitelist of the accounts allowed to connect, the most
effective hardening setting, and therefore also the most dangerous:

```bash
# /etc/ssh/sshd_config.d/00-demo-atelier.conf
AllowUsers ansible student
```

```bash
sudo sshd -T | grep -i '^allowusers'
```

```text
allowusers ansible
allowusers student
```

Once reloaded, the `sonde` account, absent from the list, is refused even
though its key and its permissions are perfect. Always test this kind of rule
on a test account, never on the one you use to administer the machine, and
check above all that the accounts you depend on do appear in the list.

### Diagnosing a refusal: the log against `ssh -vvv`

A refusal is read on both sides, and the two sides do not say the same thing.

On the **client** side, on the refusal caused by `AllowUsers`:

```bash
ssh -vvv -i ~/.ssh/id_ed25519 sonde@127.0.0.1 2>&1 | grep -iE 'Offering|continue|denied'
```

```text
debug1: Offering public key: /home/ansible/.ssh/id_ed25519 ED25519 SHA256:E8nYXqP... explicit
debug1: Authentications that can continue: publickey,gssapi-keyex,gssapi-with-mic
sonde@127.0.0.1: Permission denied (publickey,gssapi-keyex,gssapi-with-mic).
```

The client only learns that its key was offered and that the server did not
want it. **This message is exactly the same** as the one obtained above with a
badly protected `.ssh` directory: two unrelated causes, one single message. The
server stays deliberately vague, so as to teach nothing to an attacker probing
accounts.

On the **server** side, the log gives the exact reason:

```bash
sudo journalctl -u sshd --no-pager --since '-1min'
```

```text
sshd-session[4844]: User sonde from 127.0.0.1 not allowed because not listed in AllowUsers
sshd-session[4844]: Connection closed by invalid user sonde 127.0.0.1 port 58660 [preauth]
```

Note the process name: `sshd-session`, and not `sshd`. Since OpenSSH 9.8 the
session is carried by a separate binary. A filter too strict on the `sshd` name
would miss the line; `journalctl -u sshd` remains the right way in, since it
follows the unit, child processes included.

These two views are complementary: `ssh -vvv` says **which key** was offered
and in what order, the log says **why** it was rejected.

| Symptom | Likely cause | Check |
|---|---|---|
| `UNPROTECTED PRIVATE KEY FILE!` | private key too permissive on the client side | `chmod 600` on the private key |
| `Permission denied (publickey)`, log: `bad ownership or modes` | permissions or owner of `~/.ssh` or of `authorized_keys` | `stat -c '%a %U:%G'` on both |
| `Permission denied (publickey)`, log: `not listed in AllowUsers` | whitelist on the server side | `sshd -T \| grep -i allowusers` |
| setting with no effect | another occurrence, read earlier, wins | `sshd -T`, then `grep -r` in `sshd_config.d/` |
| `sshd -t` green but `restart` failing | port, host key, SELinux | `journalctl -u sshd -n 20` |

One last reflex: `sshd -t` checks the grammar, not the ability of the service
to start, and `sshd -T` says what `sshd` believes, not what the system does.
Only a **successful new connection** proves that the hardening is right.
