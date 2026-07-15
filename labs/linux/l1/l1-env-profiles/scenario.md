# Context — a per-project environment file

Real projects ship an environment file you `source` to set everything up in one
shot: a few variables, one built from another, and a project-local `bin/` put
first on `PATH` so its tools win. Write that file.

Your mission — write `env.sh` in the work directory so that, once sourced
(`source env.sh`):

1. `PROJET` is exported and equals `dsoxlab`;
2. `EDITOR` is exported and equals `vim`;
3. `GREETING` reuses `PROJET`: its value is `Bienvenue sur dsoxlab`;
4. `PATH` starts with `$PWD/bin` (the project's `bin/` comes first).

The point: `export NAME=value` publishes a variable to child processes, a
variable can be built from another (`"...$PROJET"`), and prepending to `PATH`
(`export PATH="$PWD/bin:$PATH"`) makes local tools take precedence. The tests
source your file in a subshell and even launch a child process to confirm the
variables are truly exported.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/efficace-shell/variables-environnement/
