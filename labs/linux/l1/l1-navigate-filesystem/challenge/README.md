# Building a directory tree by hand

## The situation

A project that starts is first of all a directory structure: sources on one side,
tests, documentation, configuration. Nobody builds it by clicking. You lay it
down at the keyboard, in a handful of commands, then check that it matches
exactly what was asked for.

This lab gives you the target tree and lets you build it in your work directory,
with the shell alone. Validation checks every path: a file with the right name in
the wrong place does not count, and neither does an extra file.

Method in the companion guide:
https://www.stephane-robert.info/en/docs/linux/fundamentals/navigate-filesystem/manage-files/

## Build a directory tree

### Mission

Build the following structure inside `challenge/work/` using only shell commands
(`mkdir`, `touch`, `cp`, `mv`):

```
projet/
├── src/
│   ├── app.py
│   └── utils.py
├── tests/
│   └── test_app.py
├── docs/
│   └── README.txt
└── config/
    └── settings.conf
```

### Constraints

- Work only inside `challenge/work/`.
- All five files must exist at their exact paths.
- All four directories must exist.
- Do not add extra files — only the required ones.

### Validation

```bash
dsoxlab check l1-navigate-filesystem
```
