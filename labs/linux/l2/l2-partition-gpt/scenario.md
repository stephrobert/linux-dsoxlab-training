# Context — carve a disk with GPT

The machine has a spare, blank disk. Before it can hold a filesystem, LVM member
or RAID device, it needs a **partition table**. Modern systems use **GPT** (no
4-partition / 2 TiB limits of the old MBR). Your job is to lay down GPT and cut
two partitions.

Your mission, on the VM:

1. Put a **GPT** label on the spare disk (`parted ... mklabel gpt`).
2. Create partition 1 of **512 MiB**.
3. Create partition 2 of **1 GiB**.
4. Make the kernel re-read the table (`partprobe`) so the new `…1` / `…2`
   devices appear.

The point: `parted` writes the table, and the kernel only sees the new
partitions once `partprobe` (or a reboot) refreshes it. `lsblk` shows the result.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/partitions/
