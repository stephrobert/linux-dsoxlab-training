# Challenge — l3-process-signals-priority

## Mission

Abaisse la priorité du service `labworker` à nice 10, durablement.

## Objectif (état attendu)

1. Le service `labworker` tourne.
2. Son processus tourne à **nice 10** (`ps -o ni= -p <MainPID>`).
3. `Nice=10` figure dans l'unit ou un drop-in (persistance).

## Contraintes

- Idéalement `systemctl edit labworker` (drop-in), puis `daemon-reload` + restart.
  La validation lit la **priorité live** du processus, pas la commande.

## Validation

```bash
dsoxlab check l3-process-signals-priority
```
