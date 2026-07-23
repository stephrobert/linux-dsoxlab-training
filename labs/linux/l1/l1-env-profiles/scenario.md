# Context — a per-project environment file

Real projects ship an environment file you `source` to set everything up in one
shot: a few variables, one built from another, and a project-local `bin/` put
first on `PATH` so its tools win. Write that file.

The contract, the one the tests check: `env.sh`, in the work directory, once
sourced (`source env.sh`), leaves the environment in this state:

1. `PROJET` is exported and equals `dsoxlab`;
2. `EDITOR` is exported and equals `vim`;
3. `GREETING` reuses `PROJET`: its value is `Bienvenue sur dsoxlab`;
4. `PATH` starts with `$PWD/bin`, the project's `bin/` coming first.

The point: a variable only exists for child processes if it is published to
them, and the order of `PATH` decides which binary wins when two share a name.
The tests source your file in a subshell and launch a child process to confirm
the variables are truly exported.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/efficace-shell/variables-environnement/
