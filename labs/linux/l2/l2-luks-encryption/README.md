# Lab — Encrypt a disk with LUKS

## Reminder

[**Disk encryption with LUKS**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/chiffrement-luks/)

LUKS encrypts a block device: without the key, the data is unreadable. The
order is always format -> open -> mkfs on the mapping -> mount. Persistence is
declared in `/etc/crypttab` (which creates `/dev/mapper/...`) plus `/etc/fstab`.

## The course

The examples below work on a 256 MiB demonstration container
`/srv/archives.img`, opened under the name `voute` and mounted on
`/mnt/archives`: the challenge will give you another device, another mapping
name, another mount point and another filesystem. The point is to learn the
method, not to copy a line.

> **`cryptsetup luksFormat` destroys the content of the target device, with no
> way back.** Before each command in this course, identify the target with
> `lsblk` and `losetup -a`, and act only on a device you created yourself.
> Picking the wrong disk means losing its content.

### Where the machine stands

The tool is called `cryptsetup`. On a minimal AlmaLinux image it is not
installed:

```bash
cryptsetup --version          # "command not found" before installation
sudo dnf -y install cryptsetup
```

Once present, it prints its version and the compiled-in features:

```text
cryptsetup 2.8.1 flags: UDEV BLKID KEYRING FIPS KERNEL_CAPI PWQUALITY HW_OPAL
```

Remember the **`PWQUALITY`** flag: this build refuses passphrases it considers
too weak, which is checked further down.

Then look at which devices exist, and which ones are free:

```bash
lsblk
sudo losetup -a
```

### The demonstration medium: a container file

You do not need a spare disk to learn: LUKS encrypts a **file** just as well,
presented to the kernel as a block device by `losetup`.

```bash
sudo dd if=/dev/zero of=/srv/archives.img bs=1M count=256 status=none
sudo losetup --find --show /srv/archives.img
```

```text
/dev/loop1
```

`--find` takes the first free loop number, `--show` prints it. **Note that
name, it is your target for everything that follows.** Check straight away that
it points to your file, and to nothing else:

```bash
sudo losetup -a
lsblk
```

```text
/dev/loop1: [64516]:8590690 (/srv/archives.img)
```

```text
NAME    MAJ:MIN RM  SIZE RO TYPE  MOUNTPOINTS
loop1     7:1    0  256M  0 loop
```

### Encrypt the volume: `luksFormat`

The order is fixed: **format, open, create the filesystem on the mapping,
mount**. The filesystem always goes on `/dev/mapper/...`, never on the raw
encrypted device.

```bash
sudo cryptsetup luksFormat --type luks2 /dev/loop1
```

The command warns, requires a confirmation in capital letters, then asks for
the passphrase twice:

```text
WARNING!
========
This will overwrite data on /dev/loop1 irrevocably.

Are you sure? (Type 'yes' in capital letters): Enter passphrase for /srv/archives.img:
Verify passphrase:
```

Two details to read in this output. The expected word is indeed **`YES`** in
capitals, a lowercase `yes` is not accepted. And the second prompt names
`/srv/archives.img`, not `/dev/loop1`: `cryptsetup` traces back to the file
behind the loop device, which is a free confirmation that you are targeting the
right medium.

The passphrase itself is filtered. With five characters:

```text
Password quality check failed:
 The password is shorter than 8 characters
```

This is the `PWQUALITY` flag seen above: `cryptsetup` delegates to
`libpwquality` and refuses anything under 8 characters. The format does not
happen, the return code is `2`.

The device then carries a LUKS signature:

```bash
sudo blkid /dev/loop1
```

```text
/dev/loop1: UUID="ce57a15e-cd9b-463b-975c-3a1c9b7b2736" TYPE="crypto_LUKS"
```

### Read the header: `luksDump`

This is the command that proves what you created, rather than assuming it.

```bash
sudo cryptsetup luksDump /dev/loop1
```

```text
LUKS header information
Version:       	2
Epoch:         	3
Metadata area: 	16384 [bytes]
Keyslots area: 	16744448 [bytes]
UUID:          	ce57a15e-cd9b-463b-975c-3a1c9b7b2736
Label:         	(no label)

Data segments:
  0: crypt
	offset: 16777216 [bytes]
	length: (whole device)
	cipher: aes-xts-plain64
	sector: 512 [bytes]

Keyslots:
  0: luks2
	Key:        512 bits
	Cipher:     aes-xts-plain64
	Cipher key: 512 bits
	PBKDF:      argon2id
	Time cost:  54
	Memory:     136594
	Threads:    2
	AF stripes: 4000
	AF hash:    sha256
```

(excerpt: salts and digests have been removed.)

What this output establishes, without anything special being asked for:

- **`Version: 2`**: this really is LUKS2. The guide recalls that it is the
  default format since `cryptsetup` 2.1, with a header stored twice and up to
  32 key slots, against 8 for LUKS1.
- **`aes-xts-plain64`** with a **512-bit key**: XTS uses two keys, so this is
  AES-256 and not some hypothetical AES-512.
- **`argon2id`** for key derivation, designed to resist GPU cracking, where
  LUKS1 was limited to PBKDF2. The `Time cost`, `Memory` and `Threads` lines
  are calibrated at creation time according to the machine: that is what makes
  opening deliberately slow.
- **`offset: 16777216 [bytes]`**: the data starts **16 MiB** from the
  beginning. Everything before that is the header, and its size explains what
  follows.

### Open, format, mount

```bash
sudo cryptsetup open /dev/loop1 voute
```

```text
Enter passphrase for /srv/archives.img:
```

The decrypted mapping appears under `/dev/mapper/`:

```bash
lsblk
ls -l /dev/mapper/
```

```text
NAME    MAJ:MIN RM  SIZE RO TYPE  MOUNTPOINTS
loop1     7:1    0  256M  0 loop
└─voute 253:0    0  240M  0 crypt
```

```text
lrwxrwxrwx. 1 root root 7 Jul 22 12:39 voute -> ../dm-0
```

The container is 256 MiB, the mapping only **240**: the missing 16 MiB are
exactly the header spotted in `luksDump`. It is a fixed cost, negligible on a
real disk, very visible on a small container.

`cryptsetup status` gives the full view of the open mapping:

```bash
sudo cryptsetup status voute
```

```text
/dev/mapper/voute is active.
  type:    LUKS2
  cipher:  aes-xts-plain64
  keysize: 512 [bits]
  key location: keyring
  device:  /dev/loop1
  loop:    /srv/archives.img
  sector size:  512 [bytes]
  offset:  32768 [512-byte units] (16777216 [bytes])
  size:    491520 [512-byte units] (251658240 [bytes])
  mode:    read/write
```

What remains is to put a filesystem **on the mapping**, then mount it:

```bash
sudo mkfs.ext4 /dev/mapper/voute
sudo mkdir -p /mnt/archives
sudo mount /dev/mapper/voute /mnt/archives
findmnt -n /mnt/archives
```

```text
/mnt/archives /dev/mapper/voute ext4 rw,relatime,seclabel
```

Two stacked layers, which `lsblk -f` shows clearly:

```bash
lsblk -f /dev/loop1
```

```text
NAME    FSTYPE      FSVER LABEL UUID                                 FSAVAIL FSUSE% MOUNTPOINTS
loop1   crypto_LUKS 2           ce57a15e-cd9b-463b-975c-3a1c9b7b2736
└─voute ext4        1.0         ba884bb7-2159-4d7e-b126-ea2f11fc3318  202.9M     0% /mnt/archives
```

**Two different UUIDs, and the distinction matters for what follows**: the one
of the encrypted container (`crypto_LUKS`) is for `/etc/crypttab`, the one of
the filesystem is for `/etc/fstab` when mounting by UUID. Confusing them is the
classic mistake.

### Check that the encryption really protects

There is no need to take it on trust. Write a marker in the volume, then look
for it in the raw container:

```bash
echo "SECRET-DE-DEMONSTRATION-42" | sudo tee /mnt/archives/dossier.txt
sudo sync
sudo grep -c "SECRET-DE-DEMONSTRATION" /srv/archives.img
```

```text
0
```

Zero occurrences, while the volume is **still mounted** and the file is
perfectly readable with `cat`. To be sure the search method is not at fault,
the same test on an unencrypted container does return a match:

```bash
sudo dd if=/dev/zero of=/srv/temoin.img bs=1M count=32 status=none
sudo mkfs.ext4 -q /srv/temoin.img
sudo mkdir -p /mnt/temoin && sudo mount -o loop /srv/temoin.img /mnt/temoin
echo "SECRET-DE-DEMONSTRATION-42" | sudo tee /mnt/temoin/dossier.txt >/dev/null
sudo sync && sudo umount /mnt/temoin
sudo grep -c "SECRET-DE-DEMONSTRATION" /srv/temoin.img
```

```text
1
```

The plaintext control returns the pattern, the encrypted container does not.
Now close the volume:

```bash
sudo umount /mnt/archives
sudo cryptsetup close voute
lsblk -f /dev/loop1
```

```text
NAME  FSTYPE      FSVER LABEL UUID                                 FSAVAIL FSUSE% MOUNTPOINTS
loop1 crypto_LUKS 2           ce57a15e-cd9b-463b-975c-3a1c9b7b2736
```

The filesystem has disappeared from the display, along with its UUID. It is
still there, but unreadable: without the key, the kernel only sees a
`crypto_LUKS`.

The unmount order is not negotiable. Trying to close a volume that is still
mounted fails cleanly:

```bash
sudo cryptsetup close voute
```

```text
Device voute is still in use.
```

### Add a key file and manage the slots

LUKS2 keeps several independent keys in *key slots*: enough to give personal
access to several administrators, then revoke one without touching the others.
For unlocking without typing anything, you enrol a **key file** rather than a
passphrase:

```bash
sudo dd if=/dev/urandom of=/root/archives.key bs=512 count=4
sudo chmod 0400 /root/archives.key
sudo cryptsetup luksAddKey /dev/loop1 /root/archives.key
```

```text
Enter any existing passphrase:
```

The prompt says the essential thing: to **add** a key, you must already know a
valid one. LUKS does not let you enrol a key on a volume you do not already
have access to.

The `chmod 0400` is not decorative: this file opens the volume just as well as
the passphrase. Readable by everyone, it cancels the whole benefit of the
encryption.

The occupied slots are read in `luksDump`:

```bash
sudo cryptsetup luksDump /dev/loop1 | grep -E "^  [0-9]+: luks2"
```

```text
  0: luks2
  1: luks2
```

The volume now opens without any input:

```bash
sudo cryptsetup open /dev/loop1 voute --key-file /root/archives.key
```

The other operations follow the same logic:

```bash
sudo cryptsetup luksAddKey    /dev/loop1        # add a passphrase
sudo cryptsetup luksChangeKey /dev/loop1        # replace a passphrase
sudo cryptsetup luksRemoveKey /dev/loop1        # remove the passphrase entered
sudo cryptsetup luksKillSlot  /dev/loop1 2      # remove slot number 2
```

`luksKillSlot` also requires a valid key **other** than the one in the targeted
slot, hence the `--key-file` below:

```bash
sudo cryptsetup luksKillSlot /dev/loop1 2 --key-file /root/archives.key
sudo cryptsetup luksDump /dev/loop1 | grep -E "^  [0-9]+: luks2"
```

```text
  0: luks2
  1: luks2
```

### Back up the header, and why it is vital

The header contains the encrypted keys. **If it is lost or corrupted, the data
is lost**, even with the right passphrase. An accidental write at the start of
the device is enough, and that is exactly what happens when you run a `mkfs` on
the raw encrypted device instead of the mapping.

```bash
sudo mkdir -p /root/secours
sudo cryptsetup luksHeaderBackup /dev/loop1 --header-backup-file /root/secours/archives-header.img
sudo ls -l --block-size=M /root/secours/archives-header.img
```

```text
-r--------. 1 root root 16M Jul 22 12:44 /root/secours/archives-header.img
```

Sixteen megabytes, the header size noted in `luksDump`. Note that `cryptsetup`
creates the file as `0400` itself: it knows this file is sensitive.

How sensitive? Let us check the guide's warning, which says that a header
backup remains usable with a passphrase that was **valid at backup time**, even
if it has been removed since. Remove the passphrase from slot 0:

```bash
sudo cryptsetup luksRemoveKey /dev/loop1
sudo cryptsetup luksDump /dev/loop1 | grep -E "^  [0-9]+: luks2"
sudo cryptsetup open --test-passphrase /dev/loop1
```

```text
  1: luks2
```

```text
No key available with this passphrase.
```

Slot 0 has indeed disappeared and the passphrase is now useless. Now restore
the backup taken before the removal:

```bash
sudo cryptsetup luksHeaderRestore /dev/loop1 --header-backup-file /root/secours/archives-header.img
sudo cryptsetup luksDump /dev/loop1 | grep -E "^  [0-9]+: luks2"
sudo cryptsetup open --test-passphrase /dev/loop1 ; echo "rc=$?"
```

```text
  0: luks2
  1: luks2
```

```text
rc=0
```

The "revoked" passphrase reopens the volume. **A `luksRemoveKey` therefore
protects in no way against an old header backup.** Treat these backups like the
data itself: encrypted, offline, and destroyed once they are out of date.

`--test-passphrase` is worth remembering along the way: it checks a key without
creating any mapping, it is the safest diagnostic tool.

### Unlock at boot: `crypttab` then `fstab`

Two files, two distinct roles. **`/etc/crypttab` creates the mapping**,
**`/etc/fstab` mounts that mapping**. You never put the raw encrypted device in
`fstab`.

The `crypttab` line has four fields: mapping name, device, key, options.

```bash
sudo cryptsetup luksUUID /dev/loop1
```

```text
ce57a15e-cd9b-463b-975c-3a1c9b7b2736
```

```text title="/etc/crypttab"
voute UUID=ce57a15e-cd9b-463b-975c-3a1c9b7b2736 /root/archives.key luks
```

The third field is the path to the key file. The word **`none`** in its place
asks for the passphrase interactively at boot.

```text title="/etc/fstab"
/dev/mapper/voute /mnt/archives ext4 defaults,nofail 0 2
```

The **`nofail`** option prevents an absent or unlocked volume from blocking the
boot: on removable media, it is indispensable.

You do not need to reboot to test. `systemd` generates one unit per `crypttab`
line, which you can start by hand:

```bash
sudo systemctl daemon-reload
sudo systemctl start systemd-cryptsetup@voute.service
sudo systemctl is-active systemd-cryptsetup@voute.service
ls -l /dev/mapper/voute
```

```text
active
lrwxrwxrwx. 1 root root 7 Jul 22 12:44 /dev/mapper/voute -> ../dm-0
```

The mapping is created without anyone typing `cryptsetup open`: it really is
the `crypttab` line doing the work. The mount is then tested by giving only the
mount point, which forces `mount` to read `fstab`:

```bash
sudo mount /mnt/archives
findmnt -n /mnt/archives
```

```text
/mnt/archives /dev/mapper/voute ext4 rw,relatime,seclabel
```

The generated unit is instructive, and can be read without installing
anything:

```bash
sudo systemctl cat systemd-cryptsetup@voute.service
```

```text
# /run/systemd/generator/systemd-cryptsetup@voute.service
# Automatically generated by systemd-cryptsetup-generator
...
SourcePath=/etc/crypttab
RequiresMountsFor=/root/archives.key
BindsTo=dev-disk-by\x2duuid-ce57a15e\x2dcd9b\x2d463b\x2d975c\x2d3a1c9b7b2736.device
```

Three lessons. The unit lives in `/run/`, it is **regenerated at every
`daemon-reload`**: do not edit it, fix `crypttab` instead. The
`RequiresMountsFor` on the key file requires it to be on a filesystem that is
**already mounted** when unlocking happens, which rules out putting it on the
volume it is meant to open. And the `BindsTo` shows that the `crypttab` UUID is
resolved through `/dev/disk/by-uuid/`: a typo in that UUID gives a unit that
will wait for a device that never arrives.

The guide adds one step this lab cannot verify: after a change, **regenerate
the initramfs** so that unlocking works early at boot, with `sudo dracut
--force` on RHEL and AlmaLinux, or `sudo update-initramfs -u` on Debian and
Ubuntu. It is indispensable as soon as the volume must be opened before the
root filesystem is mounted.

### What LUKS does not protect

LUKS protects **at rest**. Once the volume is unlocked and mounted, the files
are in plaintext for any authorised process, as the simple `cat` above shows on
a volume whose raw content is nevertheless unreadable. LUKS answers disk theft,
not intrusion on a running system.

Encryption is also a matter of granularity: LUKS encrypts **the whole volume**,
which suits a disk, a partition or swap. To encrypt a subfolder synchronised to
a cloud, the guide points to a per-file tool such as `gocryptfs`, and advises
against `eCryptfs`, which is deprecated.

On the cost side, AES-NI acceleration makes the overhead negligible compared to
the speed of a disk. The measurement takes one command, without touching
storage:

```bash
cryptsetup benchmark
```

```text
argon2id     52 iterations, 127546 memory, 4 parallel threads (CPUs) for 256-bit key (requested 2000 ms time)
#     Algorithm |       Key |      Encryption |      Decryption
        aes-cbc        256b      1298.5 MiB/s      5603.4 MiB/s
        aes-xts        256b      8087.8 MiB/s      8237.9 MiB/s
        aes-xts        512b      7439.7 MiB/s      7696.7 MiB/s
    serpent-xts        512b       778.5 MiB/s       789.7 MiB/s
```

(excerpt, on this lab's VM.) `aes-xts` with a 512-bit key, the mode chosen by
default, holds several gigabytes per second where `serpent-xts` tops out ten
times lower. The default is not only safe, it is also the fastest.

One last setting to know: **TRIM** is disabled by default on an encrypted
volume, and `cryptsetup status` indeed shows no `discards` flag. Enabling it
(`cryptsetup open --allow-discards`, or the `discard` option in `crypttab`)
improves the performance of an SSD, but reveals at the physical level which
blocks are in use. On a sensitive system, leave it disabled.

The guide finally describes **NBDE** (Clevis and Tang), which automatically
unlocks a volume as long as the machine can reach a Tang server, without ever
transmitting the key, as well as the TPM2-bound variant. The `clevis` and
`tang` packages are not present on this VM: this is reading, not a hands-on
part of this lab.

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `Password quality check failed: The password is shorter than 8 characters` | `cryptsetup` is built with `PWQUALITY`: at least 8 characters are required |
| `No key available with this passphrase` | wrong passphrase, or deleted slot: check with `luksDump` and `open --test-passphrase` |
| `Device voute already exists` | the mapping is already open: `cryptsetup close voute` before reopening |
| `Device voute is still in use` | the volume is still mounted: `umount` first, `close` afterwards |
| `luksAddKey` does not complete | you must supply an **already valid** key to enrol a new one |
| The mapping is smaller than the device | normal: the LUKS2 header takes the first 16 MiB |
| `mkfs` destroyed the volume | the filesystem was put on the raw device, not on `/dev/mapper/...` |
| The volume is not unlocked at boot | missing or faulty `crypttab` line, or initramfs not regenerated (`dracut --force`) |
| The `systemd-cryptsetup@…` unit stays pending | the `crypttab` UUID matches no device: compare with `cryptsetup luksUUID` |
| The key file is not found at boot | it is on a filesystem not yet mounted at that stage |
| Data unreadable after a header incident | restore with `cryptsetup luksHeaderRestore` |
| Opening is slow | `argon2id` deliberately consumes RAM and CPU, this is the brute-force protection |

To undo everything and start from scratch:

```bash
sudo umount /mnt/archives
sudo systemctl stop systemd-cryptsetup@voute.service   # or: sudo cryptsetup close voute
sudo sed -i '/^voute /d' /etc/crypttab
sudo sed -i '\|^/dev/mapper/voute |d' /etc/fstab
sudo systemctl daemon-reload
sudo losetup -d /dev/loop1
sudo rm -f /srv/archives.img /root/archives.key /root/secours/archives-header.img
sudo rmdir /root/secours /mnt/archives
```

The `losetup -d` is not a detail: without it, the loop stays attached to a
deleted file and occupies a device number until reboot. Check the return to the
starting point with `lsblk`, `sudo losetup -a` and `sudo dmsetup ls`.
