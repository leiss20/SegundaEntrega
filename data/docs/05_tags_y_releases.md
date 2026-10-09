# Manual Git - Tags y Releases

Los tags se usan para marcar puntos específicos en el historial, normalmente versiones de release.

## Crear un tag ligero (lightweight)
```
git tag v1.0.0
```

## Crear un tag anotado (recomendado para releases)
```
git tag -a v1.0.0 -m "Versión 1.0.0 - Primera release estable"
```

## Listar tags
```
git tag
git tag -l "v1.*"
```

## Ver información de un tag
```
git show v1.0.0
```

## Subir tags al remoto
```
git push origin v1.0.0
```
o todos los tags:
```
git push origin --tags
```

## Eliminar un tag local
```
git tag -d v1.0.0
```

## Eliminar un tag remoto
```
git push origin --delete v1.0.0
```

## Checkout de un tag
```
git checkout v1.0.0
```
Esto pone el repositorio en estado "detached HEAD". Para trabajar se recomienda crear una rama:
```
git checkout -b hotfix-from-v1 v1.0.0
```

Este manual no cubre la integración con sistemas de release automáticos ni CI/CD.
