# Lab — collaborative directory with set-GID

> Prepare: `dsoxlab provision` then `dsoxlab run l2-collaborative-setgid`

## Recap

[**Permissions & ownership on the companion guide**](https://blog.stephane-robert.info/docs/securiser/durcissement/permissions-ownership/)

On a directory, the **set-GID** bit (`chmod g+s` or the leading `2` in `2775`)
makes new files inherit the directory's group. Combined with the right group and
`g+w`, that's a collaborative folder: `/srv/partage` owned by `:devteam`, mode
`2775`. `ls -ld` shows an `s` in the group execute slot.

## Objectives

- `/srv/partage` is a directory, group `devteam`;
- its mode has the set-GID bit and is group-writable (`2775`);
- a file created there by a `devteam` member inherits the `devteam` group.

## Validate

```bash
dsoxlab check l2-collaborative-setgid
```
