@echo off
REM --- Script para analizar y ejecutar juegos BrickScript ---

REM Limpia la pantalla
cls

REM Verifica si se proporciono un nombre de juego
if "%1"=="" (
    echo.
    echo Uso: jugar [nombre_del_juego]
    echo Ejemplo: jugar snake
    echo Ejemplo: jugar tetris
    echo.
    goto :eof
)

set JUEGO=%1
set BRIK=%JUEGO%.brik
set AST=arbol_%JUEGO%.ast

echo.
echo Analizando el juego: %JUEGO%...
echo ----------------------------------

REM --- FASE 1: ANALIZAR EL BRICK ---
REM Redirige el nombre del archivo al analizador para evitar input manual
echo %BRIK% | C:\Python27\python.exe .\analizador.py .\games\%1.brik

REM Verifica si la compilación del AST fallo
if not exist %AST% (
    echo.
    echo !!! Error: No se genero el archivo AST !!!
    echo Revisa los mensajes de error de arriba.
    pause
    goto :eof
)

echo.
echo Analisis exitoso. Iniciando el juego...
echo ----------------------------------
pause

REM --- FASE 2: EJECUCION ---
REM Ejecuta el motor del juego con el archivo .ast resultante
C:\Python27\python.exe .\runtime.py .\games\%1.ast

echo.
echo Juego terminado. Presiona cualquier tecla para cerrar esta ventana.
pause