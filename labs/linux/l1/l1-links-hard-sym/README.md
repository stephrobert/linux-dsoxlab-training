# Lab — hard and symbolic links

> Prepare the workspace: `dsoxlab run l1-links-hard-sym`

## Recap

[**Navigating files on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/se-reperer-fichiers/navigation-fichiers/)

A **hard link** (`ln target name`) is another name for the same inode: same data,
link count goes up, and it survives deleting the original. A **symbolic link**
(`ln -s target name`) stores a path to the target; it can cross filesystems and
point at directories, but breaks if the target moves. `ls -li` reveals the inode
and the link count.

## Objectives

- `copie-dure.txt` — hard link to `original.txt` (`ln`).
- `raccourci.txt` — symbolic link to `original.txt` (`ln -s`).
- `data/` directory + `lien-data` symbolic link to it.

## Validate

```bash
dsoxlab check l1-links-hard-sym
```
