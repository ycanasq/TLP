# runtime.py
# Motor de juego para Tetris y Snake
# Usa el documento .json generado por el analizador.py

import sys
import json
import os
import time
import random
import msvcrt

class Juego:
    def __init__(self, datos_juego):
        self.datos_juego = datos_juego
        self.nombre_juego = self.datos_juego.get('nombre_juego', 'Juego Desconocido')
        self.tipo_juego = "SNAKE" if "serpiente" in self.datos_juego else "TETRIS"

        tablero = self.datos_juego.get('tablero', {})
        self.ancho = tablero.get('ancho', 10)
        self.alto = tablero.get('alto', 20)
        self.grid = [[0 for _ in range(self.ancho)] for _ in range(self.alto)]
        self.puntuacion = 0
        self.juego_terminado = False

        if self.tipo_juego == "TETRIS":
            self.pieza_actual = None
            self.pieza_x, self.pieza_y, self.pieza_rotacion = 0, 0, 0
            self.velocidad_caida = self.datos_juego.get('velocidad_inicial', 1.0)
            self.piezas = self.datos_juego.get('piezas', {})

        elif self.tipo_juego == "SNAKE":
            self.serpiente_cuerpo = []
            self.serpiente_direccion = (1, 0)
            self.posicion_comida = None
            self.velocidad_movimiento = self.datos_juego.get('velocidad_inicial', 3.0)
            self.longitud_serpiente = self.datos_juego.get('longitud_inicial', 3)

        self.timer = 0
        self.inicializar_juego()

    def inicializar_juego(self):
        if self.tipo_juego == "TETRIS":
            self.generar_nueva_pieza()
        else:
            cx, cy = self.ancho // 2, self.alto // 2
            self.serpiente_cuerpo = [(cx - i, cy) for i in range(self.longitud_serpiente)]
            self.generar_comida()

    def run(self):
        tiempo_anterior = time.time()
        while not self.juego_terminado:
            delta = time.time() - tiempo_anterior
            tiempo_anterior = time.time()

            self.manejar_input()

            self.timer += delta
            if self.tipo_juego == "TETRIS" and self.timer > 1.0 / self.velocidad_caida:
                self.timer = 0
                self.mover_pieza_abajo()
            elif self.tipo_juego == "SNAKE" and self.timer > 1.0 / self.velocidad_movimiento:
                self.timer = 0
                self.mover_serpiente()

            self.dibujar()
            time.sleep(0.05)

        self.mostrar_game_over()

    def manejar_input(self):
        if msvcrt.kbhit():
            key = msvcrt.getch()

            if self.tipo_juego == "TETRIS":
                if key == 'a':
                    self.mover_pieza_lateral(-1)
                elif key == 'd':
                    self.mover_pieza_lateral(1)
                elif key == 's':
                    self.mover_pieza_abajo()
                elif key == 'w':
                    self.rotar_pieza()
                elif key == 'q':
                    self.juego_terminado = True

            else:
                if key == 'w' and self.serpiente_direccion != (0, 1):
                    self.serpiente_direccion = (0, -1)
                elif key == 's' and self.serpiente_direccion != (0, -1):
                    self.serpiente_direccion = (0, 1)
                elif key == 'a' and self.serpiente_direccion != (1, 0):
                    self.serpiente_direccion = (-1, 0)
                elif key == 'd' and self.serpiente_direccion != (-1, 0):
                    self.serpiente_direccion = (1, 0)
                elif key == 'q':
                    self.juego_terminado = True

    def dibujar(self):
        os.system('cls')
        grid = [list(f) for f in self.grid]

        if self.tipo_juego == "TETRIS" and self.pieza_actual:
            matriz = self.pieza_actual['rotaciones'][self.pieza_rotacion]
            for y, fila in enumerate(matriz):
                for x, c in enumerate(fila):
                    if c == 1:
                        px, py = self.pieza_x + x, self.pieza_y + y
                        if 0 <= px < self.ancho and 0 <= py < self.alto:
                            grid[py][px] = 2

        if self.tipo_juego == "SNAKE":
            for i, (x, y) in enumerate(self.serpiente_cuerpo):
                if 0 <= x < self.ancho and 0 <= y < self.alto:
                    grid[y][x] = 3 if i == 0 else 2
            if self.posicion_comida:
                x, y = self.posicion_comida
                grid[y][x] = 4

        print("#" + "-" * (self.ancho * 2) + "#")
        for fila in grid:
            linea = "|"
            for c in fila:
                linea += "  " if c == 0 else "[]"
            linea += "|"
            print(linea)
        print("#" + "-" * (self.ancho * 2) + "#")
        print("Juego: {}  Puntuacion: {}".format(self.nombre_juego, self.puntuacion))

    # ===== TETRIS =====
    def generar_nueva_pieza(self):
        if not self.piezas:
            self.piezas = {
                "I": {"rotaciones": [[[0,0,0,0],[1,1,1,1],[0,0,0,0],[0,0,0,0]]]}
            }

        nombre = random.choice(self.piezas.keys())
        self.pieza_actual = self.piezas[nombre]
        self.pieza_x = self.ancho // 2 - 2
        self.pieza_y = 0
        self.pieza_rotacion = 0

        if self.verificar_colision_tetris():
            self.juego_terminado = True

    def verificar_colision_tetris(self):
        matriz = self.pieza_actual['rotaciones'][self.pieza_rotacion]
        for y, fila in enumerate(matriz):
            for x, c in enumerate(fila):
                if c == 1:
                    px, py = self.pieza_x + x, self.pieza_y + y
                    if px < 0 or px >= self.ancho or py >= self.alto:
                        return True
                    if py >= 0 and self.grid[py][px] == 1:
                        return True
        return False

    def mover_pieza_lateral(self, dx):
        self.pieza_x += dx
        if self.verificar_colision_tetris():
            self.pieza_x -= dx

    def mover_pieza_abajo(self):
        self.pieza_y += 1
        if self.verificar_colision_tetris():
            self.pieza_y -= 1
            self.fijar_pieza()
            self.generar_nueva_pieza()

    def rotar_pieza(self):
        old = self.pieza_rotacion
        self.pieza_rotacion = (self.pieza_rotacion + 1) % len(self.pieza_actual['rotaciones'])
        if self.verificar_colision_tetris():
            self.pieza_rotacion = old

    def fijar_pieza(self):
        matriz = self.pieza_actual['rotaciones'][self.pieza_rotacion]
        for y, fila in enumerate(matriz):
            for x, c in enumerate(fila):
                if c == 1:
                    self.grid[self.pieza_y + y][self.pieza_x + x] = 1

    # ===== SNAKE =====
    def generar_comida(self):
        while True:
            pos = (random.randint(0, self.ancho-1), random.randint(0, self.alto-1))
            if pos not in self.serpiente_cuerpo:
                self.posicion_comida = pos
                return

    def mover_serpiente(self):
        x, y = self.serpiente_cuerpo[0]
        dx, dy = self.serpiente_direccion
        nueva = (x + dx, y + dy)

        if nueva in self.serpiente_cuerpo or not (0 <= nueva[0] < self.ancho and 0 <= nueva[1] < self.alto):
            self.juego_terminado = True
            return

        self.serpiente_cuerpo.insert(0, nueva)
        if nueva == self.posicion_comida:
            self.puntuacion += 10
            self.generar_comida()
        else:
            self.serpiente_cuerpo.pop()

    def mostrar_game_over(self):
        print("\nJUEGO TERMINADO")
        print("Puntuacion final:", self.puntuacion)
        msvcrt.getch()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python runtime.py <archivo_juego.ast>")
        sys.exit(1)

    try:
        datos = json.load(open(sys.argv[1], 'r'))
    except IOError:
        print("Error: archivo no encontrado")
        sys.exit(1)
    except ValueError:
        print("Error: JSON invalido")
        sys.exit(1)

    Juego(datos).run()
