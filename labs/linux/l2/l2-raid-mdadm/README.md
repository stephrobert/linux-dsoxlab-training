# Lab — Build a software RAID 1 with mdadm

> Prepare the VM: `dsoxlab run l2-raid-mdadm`

## Reminder

[**Software RAID with mdadm**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/stockage/raid-mdadm/)

RAID 1 mirrors data across disks: the array survives the loss of one disk. A
spare can rebuild automatically. The array must be declared in `mdadm.conf`
(and the initramfs) to reassemble at boot.

## Objectives

- Create a **RAID 1** array with `mdadm`.
- Format and mount it.
- Make it **persistent** (`mdadm.conf`).

## Run and validate

```bash
dsoxlab run   l2-raid-mdadm
dsoxlab check l2-raid-mdadm
```
