# Challenge — l1-bash-script

## Mission

Write `rapport.sh` in `challenge/work/`. It reads a status file
(`name up` / `name down`) passed as an argument and turns it into a report.

## Output contract

`./rapport.sh serveurs.txt` must:

1. read the file passed in `$1`;
2. count the UP and the DOWN entries (loop + variables);
3. print exactly `UP=<n>` and `DOWN=<n>`;
4. exit with a **non-zero** code if at least one host is down, `0` otherwise.

## Constraints

- Mandatory shebang, executable script (`chmod +x rapport.sh`).
- Validation **runs** the script (output + return code) and replays it on
  an all-up file: the return code must depend on the real count.

## Validation

```bash
dsoxlab check l1-bash-script
```
