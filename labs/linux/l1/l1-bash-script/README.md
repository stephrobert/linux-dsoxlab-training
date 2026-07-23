# Lab — a first Bash script

## Reminder

[**Write your first script on the companion guide**](https://blog.stephane-robert.info/docs/admin-serveurs/linux/fondamentaux/efficace-shell/premier-script/)

A script starts with a shebang (`#!/usr/bin/env bash`) and must be executable
(`chmod +x`). `$1` is the first argument. A `while read` loop walks a file line
by line, variables accumulate counters, `if` tests a condition, and `exit <n>`
sets the return code the caller checks with `$?`.

## The course

The examples below work on a backup log, `backup-log.txt`, whose lines read
`date site ok` or `date site fail`, and on a demonstration script `summary.sh`:
the challenge itself will ask you for another file, other states and other
counters. The point is to learn the method, not to copy a line.

Every output reproduced here was obtained on an AlmaLinux 10 machine with
`bash 5.2.26`. The demonstration file:

```text
2026-07-19 accounting ok
2026-07-19 mail fail
2026-07-20 accounting ok
2026-07-20 mail ok
2026-07-21 accounting fail
2026-07-21 mail ok
```

### Three moves, and a script runs

A script is a plain text file. What makes it executable is a permission bit;
what makes it callable by name is a path.

```bash
cat > hello.sh <<'EOF'
#!/bin/bash
echo "Hello, $USER, on $(hostname -s)"
EOF
ls -l hello.sh
```

```text
-rw-r--r--. 1 ansible ansible 51 Jul 22 13:35 hello.sh
```

The file has no `x` at all. Running it fails:

```bash
./hello.sh
echo $?
```

```text
bash: ./hello.sh: Permission denied
126
```

`chmod +x` adds the execute permission, and the script runs:

```bash
chmod +x hello.sh
ls -l hello.sh
./hello.sh
```

```text
-rwxr-xr-x. 1 ansible ansible 51 Jul 22 13:35 hello.sh
Hello, ansible, on atelier
```

The `./` is not decorative. Without it, the shell looks the name up in the
directories of `PATH`, which does not include the current directory:

```bash
hello.sh
echo $?
```

```text
bash: hello.sh: command not found
127
```

Remember these two codes, they come back often: **126** means "found but not
executable", **127** means "not found".

### The shebang, and what really happens when it is missing

The first line of the file names the interpreter. It must be the very first
one, with no space and no blank line before it.

What happens if you forget it? The guide states that the system will not know
it is a Bash script. The machine is more nuanced. With the same content, with
no shebang:

```bash
printf 'echo "effective shell: $0"\n' > no-shebang.sh
chmod +x no-shebang.sh
./no-shebang.sh
```

```text
effective shell: ./no-shebang.sh
```

The script runs anyway. It is not the kernel that accepted it, it is the
calling shell that caught its refusal. You can see it by asking the kernel for
the execution directly, without going through a shell:

```bash
python3 -c "import os; os.execv('./no-shebang.sh', ['./no-shebang.sh'])"
```

```text
OSError: [Errno 8] Exec format error
```

The same command on a file that has a shebang goes through without complaint.
The lesson: without a shebang, your script no longer depends on itself but on
whoever runs it. Anything that calls it other than a shell (`cron`, a service,
another program) will get this error. The shebang is not a courtesy.

A shebang naming an interpreter that does not exist gives, on AlmaLinux 10:

```bash
printf '#!/bin/bsh\necho hello\n' > bad-shebang.sh
chmod +x bad-shebang.sh
./bad-shebang.sh
echo $?
```

```text
bash: ./bad-shebang.sh: cannot execute: required file not found
127
```

> **This message does not say `bad interpreter`.** Many documents announce
> `bad interpreter: No such file or directory`: that is the wording of older
> versions of Bash. With `bash 5.2`, it is
> `cannot execute: required file not found`. The diagnosis is the same: read
> the first line again.

Twin trap, and the nastiest one: a file written under Windows. Every line ends
with a `\r`, including the shebang, which then names an interpreter called
`/bin/bash\r`.

```bash
cat -A crlf.sh
```

```text
#!/bin/bash^M$
state="ok"^M$
if [ "$state" = "ok" ]; then^M$
  echo EQUAL^M$
fi^M$
```

```bash
./crlf.sh            # bash: ./crlf.sh: cannot execute: required file not found
bash crlf.sh         # crlf.sh: line 6: syntax error: unexpected end of file
sed -i 's/\r$//' crlf.sh
./crlf.sh            # EQUAL
```

The `$` at the end of the line is normal in `cat -A`, the `^M` is not. Note
that forcing `bash crlf.sh` does bypass the shebang, but fails further on: the
`fi\r` is not recognised as a `fi`.

`#!/bin/bash` and `#!/usr/bin/env bash` are both accepted. On this machine they
end up on the same binary, `/bin` being a link to `usr/bin`:

```text
lrwxrwxrwx. 1 root root 7 Apr  2  2025 /bin -> usr/bin
```

### Variables, and the two mistakes that cost the most

A variable is declared **with no space** around the `=`, and read back with
`$`. The space is not a style mistake, it is a change of meaning: the shell
then reads a command name followed by arguments.

```bash
name = "alice"
echo "[$name]"
echo $?
```

```text
bash: name: command not found
[]
0
```

Look at that last `0`: the faulty line broke nothing visible, the variable
simply stayed empty and the script carried on. This is the kind of failure you
only find after an hour.

The second mistake is missing quotes. Take a file whose name contains a space:

```bash
f="evening backup log.txt"
wc -l $f
```

```text
wc: evening: No such file or directory
wc: backup: No such file or directory
wc: log.txt: No such file or directory
0 total
```

Without quotes, the shell split the value into three words before passing them
to `wc`. With quotes, a single argument:

```bash
wc -l "$f"
```

```text
2 evening backup log.txt
```

The same trap in a test produces an error, then a **wrong answer**:

```bash
if [ -f $f ]; then echo found; else echo "not found"; fi
```

```text
bash: [: too many arguments
not found
```

```bash
if [ -f "$f" ]; then echo found; else echo "not found"; fi
```

```text
found
```

Worth noting: double brackets `[[ ]]` do not split the content of a variable,
`[[ -f $f ]]` correctly answers `found` even without quotes. That is no reason
to drop the quotes, `[ ]` is everywhere, but it explains why the same test
behaves differently depending on the syntax used.

### Arguments: `$1`, `$#`, `$0`

A script receives whatever you write after its name.

```bash
cat > args.sh <<'EOF'
#!/bin/bash
echo "\$0 = $0"
echo "\$1 = $1"
echo "\$2 = $2"
echo "\$# = $#"
echo "\$@ = $@"
EOF
chmod +x args.sh
./args.sh backup-log.txt accounting
```

```text
$0 = ./args.sh
$1 = backup-log.txt
$2 = accounting
$# = 2
$@ = backup-log.txt accounting
```

With no argument at all, `$1` is not an error: it is an empty string, and `$#`
is `0`.

```text
$0 = ./args.sh
$1 =
$2 =
$# = 0
$@ =
```

Quotes at call time group an argument that contains spaces:

```bash
./args.sh "evening backup log.txt"
```

```text
$0 = ./args.sh
$1 = evening backup log.txt
$2 =
$# = 1
$@ = evening backup log.txt
```

### Validate before acting

A serious script refuses to work on absurd input, and says so on **standard
error** (`>&2`) so as not to pollute its useful output.

```bash
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <log>" >&2
    exit 2
fi

log="$1"

if [ ! -f "$log" ]; then
    echo "Error: '$log' is not a readable file." >&2
    exit 2
fi
```

Code `2` is the convention for "wrong usage", distinct from the `1` of a
processing error. Separating the two lets the caller know whether to fix its
command line or look at the data.

### Walking a file line by line

The pattern is `while read`, fed by a **redirection** placed after the `done`:

```bash
n=0
while read -r date site state; do
    n=$((n + 1))
    echo "iteration $n: date=$date site=$site state=$state"
done < backup-log.txt
echo "total after the loop: n=$n"
```

```text
iteration 1: date=2026-07-19 site=accounting state=ok
iteration 2: date=2026-07-19 site=mail state=fail
iteration 3: date=2026-07-20 site=accounting state=ok
iteration 4: date=2026-07-20 site=mail state=ok
iteration 5: date=2026-07-21 site=accounting state=fail
iteration 6: date=2026-07-21 site=mail state=ok
total after the loop: n=6
```

`read` splits the line on spaces and fills the variables in order. `-r`
disables backslash interpretation: always use it.

Three behaviours of `read` are worth knowing.

**The last variable collects everything left.** A four-field line read with
three variables gives:

```text
date=[2026-07-19] site=[accounting] state=[ok cold-archive]
```

That is handy for a "comment" field at the end of a line, and it is a trap if
you then compare `"$state"` to an exact value.

**A last line without a trailing newline is lost.** The following file contains
three lines, but its last byte is `l`, not `\n`:

```bash
od -c no-newline.txt
```

```text
0000000   a       o   k  \n   b       o   k  \n   c       f   a   i   l
0000020
```

```text
read: a ok
read: b ok
lines read = 2  (the file contains 3)
```

The safeguard is to keep going as long as the variable is not empty:

```bash
while read -r name state || [ -n "$name" ]; do ...; done < no-newline.txt
```

```text
read: a ok
read: b ok
read: c fail
lines read = 3
```

**`IFS=` preserves leading spaces.** On an indented line:

```text
without IFS= : [indented ok]
with IFS=    : [   indented ok]
```

When you split into fields, leave `IFS` at its default. When you want the raw
line, write `while IFS= read -r line`.

### The trap that costs the most hours: the loop in a subshell

Here are two scripts that differ only in the way the loop is fed.

```bash
#!/bin/bash
n=0
while read -r date site state; do
    n=$((n + 1))
done < "$1"                   # redirection
echo "total after the loop: n=$n"
```

```text
total after the loop: n=6
```

```bash
#!/bin/bash
n=0
cat "$1" | while read -r date site state; do
    n=$((n + 1))
done                          # pipe
echo "total after the loop: n=$n"
```

```text
total after the loop: n=0
```

No error, no message: simply a counter left at zero. Every link of a pipeline
runs in a **subshell**, a child process. The loop did count, but in a copy of
the variables, which dies with the subshell. The final `echo` reads the
original, still at `0`.

Two correct ways to do it:

```bash
done < "$file"                # redirection, when the source is a file
done < <(sort "$file")        # process substitution, when a command is needed
```

The second form does give the expected result:

```text
failures counted after a sort: n=2
```

### Count, test, decide

Two counters, a `case` to sort the states, and the arithmetic increment
`$(( ))`:

```bash
passed=0
failed=0

while read -r date site state; do
    [ -z "$date" ] && continue
    case "$state" in
        ok)   passed=$((passed + 1)) ;;
        fail) failed=$((failed + 1)) ;;
    esac
done < "$log"
```

An `if` would do just as well for two cases; `case` will stay readable when
there are five. The line `[ -z "$date" ] && continue` skips blank lines.

### The return code

`exit <n>` sets the code the caller will receive, and the caller reads it in
`$?`.

```bash
if [ "$failed" -gt 0 ]; then
    exit 3
fi
exit 0
```

Four things to know, all verifiable in one line.

**`$?` does not survive the next command.** It holds the code of the **last**
command run, `echo` included:

```text
first  echo $? : 3
second echo $? : 0
```

If you have to do anything with it, save it immediately:

```bash
./summary.sh backup-log.txt > /dev/null
code=$?
```

**Codes are bounded to 0-255.** An `exit 256` is taken modulo 256 and therefore
reports a success:

```text
exit 256 -> $? = 0
exit -1  -> $? = 255
```

**A script with no `exit` returns the code of its last command.** The same
script, with a simple `echo "done"` added at the end, lies about its result:

```text
without exit                    -> $? = 1
without exit, but a final echo  -> $? = 0
```

That is why a script ends with an explicit `exit`.

**A return code is consumed without `$?`.** `if`, `&&` and `||` take the
command directly:

```bash
if ./summary.sh backup-log.txt > /dev/null; then
    echo "all backups succeeded"
else
    echo "at least one failure (code $?)"
fi

./summary.sh perfect-log.txt > /dev/null && echo "nothing to report"
./summary.sh backup-log.txt  > /dev/null || echo "look at the log"
```

```text
at least one failure (code 3)
nothing to report
look at the log
```

That is the whole point of an honest return code: it makes the script usable in
a chain (cron, CI, `&&`) without anyone having to read its output.

### The complete example

```bash
#!/bin/bash
# summary.sh: counts the successful and failed backups of a log.
# Usage: ./summary.sh <log>

if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <log>" >&2
    exit 2
fi

log="$1"

if [ ! -f "$log" ]; then
    echo "Error: '$log' is not a readable file." >&2
    exit 2
fi

passed=0
failed=0

while read -r date site state; do
    [ -z "$date" ] && continue
    case "$state" in
        ok)   passed=$((passed + 1)) ;;
        fail) failed=$((failed + 1)) ;;
    esac
done < "$log"

echo "PASSED=$passed"
echo "FAILED=$failed"

if [ "$failed" -gt 0 ]; then
    exit 3
fi
exit 0
```

The four runs, exactly as the machine produced them:

```bash
./summary.sh backup-log.txt ; echo "code: $?"
```

```text
PASSED=4
FAILED=2
code: 3
```

```bash
./summary.sh perfect-log.txt ; echo "code: $?"
```

```text
PASSED=2
FAILED=0
code: 0
```

```bash
./summary.sh ; echo "code: $?"
```

```text
Usage: ./summary.sh <log>
code: 2
```

```bash
./summary.sh /tmp/not-here.txt ; echo "code: $?"
```

```text
Error: '/tmp/not-here.txt' is not a readable file.
code: 2
```

The second case is the only one that proves anything about the logic: a script
that always exited with an error would pass the first test and fail that one.
Always test yours on a data set that must return `0`.

### Debugging: `bash -x`, then `shellcheck`

`bash -x` prints every command, variables already substituted, prefixed with a
`+`. On a log reduced to two lines:

```bash
bash -x ./summary.sh short.txt
```

```text
+ '[' 1 -ne 1 ']'
+ log=short.txt
+ '[' '!' -f short.txt ']'
+ passed=0
+ failed=0
+ read -r date site state
+ '[' -z 2026-07-22 ']'
+ case "$state" in
+ passed=1
+ read -r date site state
+ '[' -z 2026-07-22 ']'
+ case "$state" in
+ failed=1
+ read -r date site state
+ echo PASSED=1
PASSED=1
+ echo FAILED=1
FAILED=1
+ '[' 1 -gt 0 ']'
+ exit 3
```

You read the loop iteration by iteration, and above all the **actual value** of
the variables at the time of the test. `set -x` and `set +x` limit the trace to
a portion of the script.

`shellcheck` does the same job without running the script. On AlmaLinux 10 it is
not in the base repositories:

```bash
sudo dnf list --available ShellCheck
# Error: No matching Packages to list
sudo dnf -y install epel-release
sudo dnf -y install ShellCheck
```

Let us hand it a fragile version of the loop:

```bash
#!/bin/bash
file=$1
n=0
cat $file | while read line; do
    n=$((n+1))
done
echo "lines: $n"
```

```text
In fragile.sh line 4:
cat $file | while read line; do
    ^---^ SC2086 (info): Double quote to prevent globbing and word splitting.
                  ^--^ SC2162 (info): read without -r will mangle backslashes.
                       ^--^ SC2034 (warning): line appears unused.

In fragile.sh line 5:
    n=$((n+1))
    ^-- SC2030 (info): Modification of n is local (to subshell caused by pipeline).

In fragile.sh line 7:
echo "lines: $n"
             ^-- SC2031 (info): n was modified in a subshell. That change might be lost.
```

It found the four defects seen above, including the subshell, without running
anything. On `summary.sh`, only one warning is left:

```text
In summary.sh line 20:
while read -r date site state; do
                   ^--^ SC2034 (warning): site appears unused.
```

That is correct: the middle field is read but never used. The convention to say
so explicitly is to name it `_`; `shellcheck` then goes completely silent, and
the script gives the same result:

```bash
while read -r date _ state; do
```

### When `set -euo pipefail` does not catch what you think

`set -e` stops the script at the first command that fails, `set -u` forbids
undefined variables, `set -o pipefail` propagates the failure of a pipeline
link. That is the right line to put right after the shebang of a production
script. You still need to know what it does **not** do.

**`set -e` ignores what is already tested.** A command whose result you use is
not treated as a failure:

```bash
#!/bin/bash
set -e
if grep -q "nowhere" backup-log.txt; then
    echo "found"
else
    echo "1. grep failed, the script is still alive"
fi
grep -q "nowhere" backup-log.txt && echo "found"
echo "2. left of && either, the script is still alive"
grep -q "nowhere" backup-log.txt
echo "3. this line must never be printed"
```

```text
1. grep failed, the script is still alive
2. left of && either, the script is still alive
code=1
```

The third line is not printed: it is the only untested `grep` that killed the
script. The first two went through without a sound.

**`set -e` kills the script on an increment.** The most baffling trap of all,
because it hits exactly the code of a counter:

```bash
#!/bin/bash
set -e
n=0
echo "before"
((n++))
echo "after: n=$n"
```

```text
before
code=1
```

The script stopped, without a single message. `((n++))` returns the value
**before** the increment, so `0`, and a null arithmetic expression means a
non-zero return code. `set -e` concludes it is a failure. The assignment form
does not have this defect:

```bash
n=$((n + 1))
```

```text
before
after: n=1
code=0
```

**`$?` after a pipe only speaks for the last link.**

```bash
cat missing-file.txt | wc -l
echo "without pipefail: $?"
set -o pipefail
cat missing-file.txt | wc -l
echo "with pipefail: $?"
```

```text
cat: missing-file.txt: No such file or directory
0
without pipefail: 0
cat: missing-file.txt: No such file or directory
0
with pipefail: 1
```

Without `pipefail`, the pipeline declares itself a success even though `cat`
failed: `wc -l` did its job on an empty input, and it is the one that has the
last word. The detail link by link stays available in the `PIPESTATUS` array:

```text
PIPESTATUS = 1 0
```

### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `Permission denied`, code 126 | the `x` bit is missing: `chmod +x` |
| `command not found` on your own script, code 127 | the `./` is missing in front of the name |
| `cannot execute: required file not found`, code 127 | shebang pointing at an interpreter that does not exist, or CRLF line endings |
| `syntax error: unexpected end of file` with `bash script.sh` | CRLF line endings; check with `cat -A`, fix with `sed -i 's/\r$//'` |
| `name: command not found` on an assignment line | spaces around the `=` |
| `[: too many arguments` | unquoted variable containing a space: write `[ -f "$f" ]` |
| The counter is `0` after the loop | loop fed by a pipe, therefore run in a subshell: `done < file` or `done < <(command)` |
| The last line of the file is never read | no trailing newline: add `\|\| [ -n "$var" ]` to the `while` condition |
| The script stops with no message right after a `((n++))` | `set -e` plus an arithmetic expression worth `0`: write `n=$((n + 1))` |
| `$?` is `0` while the first command of the pipe failed | only the last link counts: `set -o pipefail`, or read `${PIPESTATUS[0]}` |
| The return code is `0` while the script does `exit 256` | codes are bounded to 0-255, stay within 1-255 |
| The return code is `0` while a command failed | no explicit `exit`: the code is that of the last `echo`, which succeeded |
| `shellcheck: command not found` on AlmaLinux 10 | absent from the base repositories: `sudo dnf -y install epel-release` then `sudo dnf -y install ShellCheck` |

To undo everything and start over:

```bash
rm -rf ~/script-workshop
```
