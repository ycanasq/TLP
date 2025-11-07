# TLP - 2025
Este repositorio recopila las entregas del proyecto práctico del curso Teoría de Lenguajes de Programación (TLP).

# Intérprete y motor de ejecución para juegos definidos en lenguaje BRIK

Desarrollo de un analizador léxico, sintáctico y un intérprete en Python capaces de ejecutar dos juegos clásicos: Snake y Tetris, definidos a través de un lenguaje propio (.brik) y su árbol sintáctico (.ast). El proyecto demuestra la aplicación de conceptos de compiladores, estructuras de datos y procesamiento de archivos JSON en un entorno lúdico interactivo.

## Getting Started

### Dependencies

* python

### Installing

Asegúrate de tener todos los siguientes archivos en la misma carpeta:
runtime.py
analizador.py
snake.brik
tetris.brik

### Executing program

1. Generar el árbol sintáctico (.ast)
Ejecuta el analizador:
```
python analizador.py
```
Cuando se solicite, proporciona el nombre del archivo .brik que deseas procesar (tetris.brik o snake.brik):
```
tetris.brik
```
Esto generará un archivo llamado:
```
arbol_tetris.ast
```
2. Ejecutar el intérprete del juego
Usa el archivo .ast generado para correr el juego:
```
python runtime.py arbol_tetris.ast
```

## Authors

Yuricik Cañas Quintero

## Version History

* Entrega2
    * Correcciones en el analizador y tetris.brik
    * Creación del runtime.py
* Entrega1
    * Entraga inicial: analizador.py, snake.brik, tetris.brik

## License

Este proyecto practico se elaboro para el curso de Teoria de Lenguaje de programación
