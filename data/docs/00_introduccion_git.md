# Introducción a Git

## ¿Qué es Git?

Git es un sistema de control de versiones distribuido (VCS) de código abierto. Fue creado por Linus Torvalds en 2005 para el desarrollo del kernel de Linux.

Git permite a los desarrolladores:
- Registrar el historial completo de cambios de un proyecto.
- Trabajar de forma concurrente en el mismo código sin sobrescribir el trabajo de otros.
- Recuperar versiones anteriores del código en cualquier momento.
- Crear ramas (branches) para desarrollar funcionalidades de forma aislada.
- Fusionar (merge) cambios de diferentes ramas de manera controlada.

A diferencia de sistemas centralizados (como SVN o CVS), Git es **distribuido**: cada desarrollador tiene una copia completa del repositorio (incluyendo todo el historial) en su máquina local.

## Conceptos fundamentales

### Repositorio (repository)
Es el contenedor principal donde se almacena todo el historial del proyecto. Puede ser:
- **Local**: la carpeta `.git` que se crea en tu máquina.
- **Remoto**: una copia alojada en un servidor (GitHub, GitLab, Bitbucket, etc.).

### Commit
Un commit es una "foto" o snapshot del estado del proyecto en un momento determinado. Cada commit tiene:
- Un identificador único (hash SHA-1).
- Un mensaje descriptivo.
- Autor y fecha.
- Referencia al commit padre.

### Staging area (área de preparación)
Zona intermedia entre los archivos modificados y el commit. Permite seleccionar exactamente qué cambios se incluirán en el próximo commit con `git add`.

### Rama (branch)
Una rama es una línea independiente de desarrollo. La rama principal suele llamarse `main` o `master`.

## Diferencia entre Git y GitHub

- **Git**: la herramienta de control de versiones (software que se instala localmente).
- **GitHub**: una plataforma web que aloja repositorios Git y añade funcionalidades de colaboración (pull requests, issues, etc.).