# Manual Git - Descartar cambios

Este manual describe cómo descartar cambios locales de forma segura e irreversible.

## Descartar cambios en archivos no preparados (untracked o modified)
Para descartar modificaciones en un archivo que aún no está en staging:
```
git checkout -- <archivo>
```
o con Git moderno:
```
git restore <archivo>
```

Para todos los archivos:
```
git restore .
```

## Descartar cambios del área de staging
Si ya hiciste `git add` y quieres quitar del staging (pero mantener los cambios en el working directory):
```
git reset HEAD <archivo>
```
o:
```
git restore --staged <archivo>
```

## Descartar TODOS los cambios no confirmados (irreversible)
El comando:
```
git reset --hard HEAD
```
Descarta **todos** los cambios no confirmados (tanto en working directory como en staging) de forma **irreversible**. Se pierden los cambios no confirmados.

**ADVERTENCIA CRÍTICA**: Esta acción es irreversible. No hay forma de recuperar los cambios descartados con este comando a menos que estén en el reflog y se actúe muy rápido.

## Volver a un commit anterior descartando commits posteriores
```
git reset --hard <hash-commit>
```
Mueve HEAD y la rama actual a ese commit, eliminando los commits posteriores del historial de la rama (aunque pueden recuperarse temporalmente vía reflog).

## Limpiar archivos no rastreados
Para eliminar archivos y carpetas no rastreados por Git:
```
git clean -fd
```
- `-f`: force
- `-d`: directorios

Primero se puede hacer un dry-run:
```
git clean -fdn
```

## Recuperar cambios descartados (limitado)
Si se usó `git reset --hard` recientemente, a veces se puede recuperar con:
```
git reflog
git checkout <hash-del-reflog>
```
Pero no es garantizado y depende del tiempo y garbage collection.
