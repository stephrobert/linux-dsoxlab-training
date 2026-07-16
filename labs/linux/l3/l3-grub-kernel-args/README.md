# Lab — persistent kernel boot parameter

> Prepare: `dsoxlab provision` then `dsoxlab run l3-grub-kernel-args`

## Recap

[**GRUB on the companion guide**](https://blog.stephane-robert.info/docs/securiser/durcissement/grub/)

`grubby --update-kernel=ALL --args="param"` adds a kernel argument to the installed
kernels; `--remove-args` removes it; `--info=DEFAULT` shows the default kernel's
args. For **future** kernels, add the parameter to `GRUB_CMDLINE_LINUX` in
`/etc/default/grub` (the template for `grub2-mkconfig`). Both are needed for true
persistence.

## Objectives

- the default kernel's args include `panic=10` (`grubby --info=DEFAULT`);
- `/etc/default/grub` contains `panic=10`.

## Validate

```bash
dsoxlab check l3-grub-kernel-args
```
