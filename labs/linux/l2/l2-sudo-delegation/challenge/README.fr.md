# Challenge — l2-sudo-delegation

## Mission

Délègue au groupe `operators` (dont `ops` est membre) un sudo restreint.

## Objectif (état attendu)

1. Un drop-in `/etc/sudoers.d/operators` existe.
2. `%operators` peut lancer **`/usr/bin/systemctl` uniquement**, en **`NOPASSWD`**.
3. La syntaxe sudoers reste **valide** (`visudo -c` retourne 0).
4. Pas de sudo total pour ops (moindre privilège).

## Contraintes

- Édite via `visudo -f /etc/sudoers.d/operators` : il valide la syntaxe à
  l'enregistrement, mais il **ne pose pas les droits attendus**. Il laisse le
  fichier en `0640`, et `visudo -c` refuse alors l'ensemble (`bad permissions,
  should be mode 0440`) alors même que la règle fonctionne. Termine donc par
  `chmod 0440 /etc/sudoers.d/operators`.
- La validation lit la **politique effective** (`sudo -l -U ops`).

## Validation

```bash
dsoxlab check l2-sudo-delegation
```
