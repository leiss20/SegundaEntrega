# Manual Git - Comandos básicos

Este manual cubre los comandos fundamentales de Git para el control de versiones.

## Inicializar un repositorio
Para crear un nuevo repositorio Git en el directorio actual:
```
git init
```
Esto crea una carpeta oculta .git que almacena todo el historial.

## Añadir archivos al área de preparación (staging)
Para preparar archivos para el próximo commit:
```
git add <archivo>
git add .   # añade todos los archivos modificados
```

## Crear un commit
Para guardar los cambios preparados en el historial:
```
git commit -m "Mensaje descriptivo del cambio"
```

## Ver el estado del repositorio
```
git status
```
Muestra archivos modificados, preparados y no rastreados.

## Ver el historial de commits
```
git log
git log --oneline
git log --graph --oneline --all
```

## Trabajar con ramas
Crear una nueva rama:
```
git branch <nombre-rama>
```

Cambiar a una rama existente:
```
git checkout <nombre-rama>
```

Crear y cambiar a una nueva rama en un solo comando:
```
git checkout -b <nombre-rama>
```
o con Git moderno:
```
git switch -c <nombre-rama>
```

Listar ramas:
```
git branch
git branch -a   # incluye ramas remotas
```

## Fusionar ramas (merge)
Para integrar los cambios de una rama en la rama actual:
```
git merge <rama-origen>
```

Si hay conflictos, Git marca los archivos. Debes resolverlos manualmente, luego:
```
git add <archivo-resuelto>
git commit
```

## Subir cambios al remoto (push)
```
git push origin <nombre-rama>
```

La primera vez que se sube una rama:
```
git push -u origin <nombre-rama>
```

## Clonar un repositorio existente
```
git clone <url-del-repositorio>
```

Este manual no cubre integraciones con herramientas de CI/CD como Jenkins, GitHub Actions o Travis CI.
