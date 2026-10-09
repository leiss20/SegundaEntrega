# Manual Git - Sincronización de ramas

Este manual explica cómo mantener sincronizadas las ramas locales y remotas.

## El problema de push rechazado
Si el remoto tiene commits que tu rama local no tiene, el comando `git push` es rechazado con un mensaje similar a:
```
! [rejected]        main -> main (fetch first)
error: failed to push some refs to 'origin'
hint: Updates were rejected because the remote contains work that you do not have locally.
```

## Solución recomendada: pull con rebase
La forma preferida de actualizar tu rama local antes de hacer push es:
```
git pull --rebase origin <rama>
```

Esto:
1. Descarga los commits remotos.
2. Reaplica tus commits locales encima de los remotos.
3. Mantiene un historial lineal más limpio.

Si aparecen conflictos durante el rebase:
1. Resuelve los conflictos en los archivos marcados.
2. Marca como resueltos: `git add <archivo>`
3. Continúa el rebase: `git rebase --continue`
4. Si quieres abortar: `git rebase --abort`

Después del rebase exitoso:
```
git push origin <rama>
```

## Alternativa: merge
También se puede hacer:
```
git pull origin <rama>   # equivale a fetch + merge
```
Esto crea un commit de merge, lo cual puede ensuciar el historial.

## Fetch vs Pull
- `git fetch origin`: solo descarga los cambios remotos sin integrarlos.
- `git pull origin <rama>`: fetch + merge (o rebase si se usa --rebase).

## Ver diferencias con el remoto
```
git fetch origin
git log HEAD..origin/<rama>   # commits que tiene el remoto y tú no
git log origin/<rama>..HEAD   # commits que tienes tú y el remoto no
```
