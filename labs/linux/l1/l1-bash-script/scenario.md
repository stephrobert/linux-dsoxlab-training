# Context — a first real Bash script

A monitoring file lists hosts and their status, one per line: `name up` or
`name down`. Write a script that turns it into a verdict: how many are up, how
many down, and an exit code a pipeline can act on.

The contract, the one the tests check: `rapport.sh`, in the work directory,
called as `./rapport.sh serveurs.txt`, must

1. read the file **passed as the first argument**;
2. print exactly two lines: `UP=<n>` and `DOWN=<n>`;
3. **exit non-zero** when at least one host is down, `0` otherwise.

It must start with a shebang and be executable. The tests run the script and
read its output and exit code; they even re-run it on an all-up file, so the
exit code must reflect the real count, not a hard-coded value.

Method in the companion guide:
https://blog.stephane-robert.info/docs/admin-serveurs/linux/exploiter/scripts-bash/premier-script/
