# Context — stop wasting I/O on access times

`/srv/data` serves a read-heavy workload. By default Linux updates each file's
**access time** (atime) on reads, which turns reads into writes and hurts
performance. The standard fix is the **`noatime`** mount option. Your job is to
apply it — now and permanently.

The point: mount options tune a filesystem's behaviour; `noatime` skips atime
updates. What remains is working out how to make it effective right away **and**
persistent across a reboot: those are two distinct moves.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/performances-disques/
