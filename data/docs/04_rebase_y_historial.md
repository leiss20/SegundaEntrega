# Manual Git - Rebase y manipulación del historial

## Qué es el rebase
El rebase permite reaplicar commits de una rama sobre otra, reescribiendo el historial para mantenerlo lineal.

Comando básico:
```
git rebase <rama-base>
```

Ejemplo típico: estás en feature y quieres actualizarla con main:
```
git checkout feature
git rebase main
```

## Rebase interactivo
Para editar, reordenar, combinar (squash) o eliminar commits:
```
git rebase -i HEAD~3
```
o
```
git rebase -i <hash>
```

En el editor se pueden cambiar comandos:
- pick: mantener el commit
- reword: cambiar el mensaje
- edit: detenerse para modificar el commit
- squash: combinar con el anterior
- drop: eliminar el commit

## Regla de oro del rebase
**Nunca hagas rebase de commits que ya fueron publicados (pusheados) y que otras personas puedan estar usando.**

Si ya se hizo push y se hace rebase, se reescribe el historial y se necesitará:
```
git push --force
```
o de forma más segura:
```
git push --force-with-lease
```

**ADVERTENCIA**: `git push --force` puede sobrescribir trabajo de otros colaboradores. Úsalo solo en ramas personales o con coordinación del equipo.

## Cherry-pick
Para aplicar un commit específico de otra rama:
```
git cherry-pick <hash-commit>
```

## Reflog
El reflog registra todos los movimientos de HEAD:
```
git reflog
```
Es útil para recuperar commits "perdidos" después de un reset o rebase.
