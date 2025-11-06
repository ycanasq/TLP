# runtime.py
# Motor de juego para Tetris y Snake
#Usa el documento .json generado por el analizador.py

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
        
        # Configuración específica por tipo de juego
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
            self.controles = self.datos_juego.get('controles', {})
        
        self.timer = 0
        self.inicializar_juego()

    def inicializar_juego(self):
        """Inicializa el juego según el tipo"""
        if self.tipo_juego == "TETRIS":
            self.generar_nueva_pieza()
        
        elif self.tipo_juego == "SNAKE":
            # Posicionar serpiente en el centro
            centro_x, centro_y = self.ancho // 2, self.alto // 2
            self.serpiente_cuerpo = [(centro_x, centro_y)]
            for i in range(1, self.longitud_serpiente):
                self.serpiente_cuerpo.append((centro_x - i, centro_y))
            
            self.generar_comida()

    def run(self):
        """Bucle principal del juego"""
        tiempo_anterior = time.time()
        
        while not self.juego_terminado:
            delta_tiempo = time.time() - tiempo_anterior
            tiempo_anterior = time.time()
            
            self.manejar_input()
            
            # Actualizar según el tipo de juego
            if self.tipo_juego == "TETRIS":
                self.timer += delta_tiempo
                if self.timer > 1.0 / self.velocidad_caida:
                    self.timer = 0
                    self.mover_pieza_abajo()
            
            elif self.tipo_juego == "SNAKE":
                self.timer += delta_tiempo
                if self.timer > 1.0 / self.velocidad_movimiento:
                    self.timer = 0
                    self.mover_serpiente()
            
            self.dibujar()
            time.sleep(0.05)
        
        self.mostrar_game_over()

    def manejar_input(self):
        """Maneja las entradas del teclado"""
        if msvcrt.kbhit():
            key = msvcrt.getch()
            
            if self.tipo_juego == "TETRIS":
                if key == b'a':  # Mover izquierda
                    self.mover_pieza_lateral(-1)
                elif key == b'd':  # Mover derecha
                    self.mover_pieza_lateral(1)
                elif key == b's':  # Acelerar caída
                    self.mover_pieza_abajo()
                elif key == b'w':  # Rotar
                    self.rotar_pieza()
                elif key == b'p':  # Pausa
                    self.pausar()
                elif key == b'q':  # Salir
                    self.juego_terminado = True
            
            elif self.tipo_juego == "SNAKE":
                if key == b'w' and self.serpiente_direccion != (0, 1):  # Arriba
                    self.serpiente_direccion = (0, -1)
                elif key == b's' and self.serpiente_direccion != (0, -1):  # Abajo
                    self.serpiente_direccion = (0, 1)
                elif key == b'a' and self.serpiente_direccion != (1, 0):  # Izquierda
                    self.serpiente_direccion = (-1, 0)
                elif key == b'd' and self.serpiente_direccion != (-1, 0):  # Derecha
                    self.serpiente_direccion = (1, 0)
                elif key == b'p':  # Pausa
                    self.pausar()
                elif key == b'q':  # Salir
                    self.juego_terminado = True

    def dibujar(self):
        """Renderiza el juego en pantalla"""
        os.system('cls')
        grid_display = [list(fila) for fila in self.grid]
        
        if self.tipo_juego == "TETRIS" and self.pieza_actual:
            # Dibujar pieza actual
            matriz_pieza = self.pieza_actual['rotaciones'][self.pieza_rotacion]
            for y_offset, fila in enumerate(matriz_pieza):
                for x_offset, celda in enumerate(fila):
                    if celda == 1:
                        pos_x, pos_y = self.pieza_x + x_offset, self.pieza_y + y_offset
                        if 0 <= pos_y < self.alto and 0 <= pos_x < self.ancho:
                            grid_display[pos_y][pos_x] = 2
        
        elif self.tipo_juego == "SNAKE":
            # Dibujar serpiente
            for i, (x, y) in enumerate(self.serpiente_cuerpo):
                if 0 <= y < self.alto and 0 <= x < self.ancho:
                    grid_display[y][x] = 3 if i == 0 else 2  # Cabeza diferente
            
            # Dibujar comida
            if self.posicion_comida:
                x, y = self.posicion_comida
                if 0 <= y < self.alto and 0 <= x < self.ancho:
                    grid_display[y][x] = 4

        # Construir pantalla
        buffer_pantalla = ["#" + "-" * (self.ancho * 2) + "#"]
        
        for y in range(self.alto):
            linea = "|"
            for x in range(self.ancho):
                celda = grid_display[y][x]
                if celda == 0: 
                    linea += "  "  # Vacío
                elif celda == 1: 
                    linea += "[]"  # Bloque fijo (Tetris)
                elif celda == 2: 
                    linea += "[]"  # Bloque móvil/Serpiente cuerpo
                elif celda == 3: 
                    linea += "()"  # Cabeza serpiente
                elif celda == 4: 
                    linea += "**"  # Comida
            linea += "|"
            
            # Información lateral
            if y == 1:
                linea += f"  {self.nombre_juego}"
            elif y == 3:
                linea += f"  PUNTUACION: {self.puntuacion}"
            elif y == 5:
                linea += "  CONTROLES:"
            elif y == 6:
                if self.tipo_juego == "TETRIS":
                    linea += "  A: Izquierda"
                else:
                    linea += "  WASD: Mover"
            elif y == 7:
                if self.tipo_juego == "TETRIS":
                    linea += "  D: Derecha"
                else:
                    linea += "  P: Pausa"
            elif y == 8:
                if self.tipo_juego == "TETRIS":
                    linea += "  W: Rotar"
                else:
                    linea += "  Q: Salir"
            elif y == 9:
                if self.tipo_juego == "TETRIS":
                    linea += "  S: Bajar"
            
            buffer_pantalla.append(linea)
        
        buffer_pantalla.append("#" + "-" * (self.ancho * 2) + "#")
        print("\n".join(buffer_pantalla))

    # ===== LÓGICA TETRIS =====
    def generar_nueva_pieza(self):
        """Genera una nueva pieza para Tetris"""
        if not self.piezas:
            # Piezas por defecto si no hay definidas
            self.piezas = {
                "I": {"rotaciones": [[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]]}
            }
        
        nombre_pieza = random.choice(list(self.piezas.keys()))
        self.pieza_actual = self.piezas[nombre_pieza]
        self.pieza_x = self.ancho // 2 - 2
        self.pieza_y = 0
        self.pieza_rotacion = 0
        
        # Verificar game over
        if self.verificar_colision_tetris():
            self.juego_terminado = True

    def verificar_colision_tetris(self):
        """Verifica colisiones en Tetris"""
        if not self.pieza_actual:
            return False
            
        matriz = self.pieza_actual['rotaciones'][self.pieza_rotacion]
        for y_offset, fila in enumerate(matriz):
            for x_offset, celda in enumerate(fila):
                if celda == 1:
                    x, y = self.pieza_x + x_offset, self.pieza_y + y_offset
                    if (x < 0 or x >= self.ancho or y >= self.alto or 
                        (y >= 0 and self.grid[y][x] == 1)):
                        return True
        return False

    def mover_pieza_lateral(self, dx):
        """Mueve la pieza lateralmente en Tetris"""
        if not self.pieza_actual:
            return
            
        self.pieza_x += dx
        if self.verificar_colision_tetris():
            self.pieza_x -= dx

    def mover_pieza_abajo(self):
        """Mueve la pieza hacia abajo en Tetris"""
        if not self.pieza_actual:
            return
            
        self.pieza_y += 1
        if self.verificar_colision_tetris():
            self.pieza_y -= 1
            self.fijar_pieza()
            self.verificar_lineas_completas()
            self.generar_nueva_pieza()

    def rotar_pieza(self):
        """Rota la pieza actual en Tetris"""
        if not self.pieza_actual:
            return
            
        rotacion_original = self.pieza_rotacion
        self.pieza_rotacion = (self.pieza_rotacion + 1) % len(self.pieza_actual['rotaciones'])
        
        if self.verificar_colision_tetris():
            self.pieza_rotacion = rotacion_original

    def fijar_pieza(self):
        """Fija la pieza actual en el grid de Tetris"""
        if not self.pieza_actual:
            return
            
        matriz = self.pieza_actual['rotaciones'][self.pieza_rotacion]
        for y_offset, fila in enumerate(matriz):
            for x_offset, celda in enumerate(fila):
                if celda == 1:
                    x, y = self.pieza_x + x_offset, self.pieza_y + y_offset
                    if 0 <= y < self.alto and 0 <= x < self.ancho:
                        self.grid[y][x] = 1

    def verificar_lineas_completas(self):
        """Verifica y elimina líneas completas en Tetris"""
        lineas_completas = []
        for y in range(self.alto):
            if all(self.grid[y]):
                lineas_completas.append(y)
        
        for linea in lineas_completas:
            del self.grid[linea]
            self.grid.insert(0, [0] * self.ancho)
            self.puntuacion += 100

    # ===== LÓGICA SNAKE =====
    def generar_comida(self):
        """Genera comida en una posición aleatoria para Snake"""
        while True:
            x = random.randint(0, self.ancho - 1)
            y = random.randint(0, self.alto - 1)
            if (x, y) not in self.serpiente_cuerpo:
                self.posicion_comida = (x, y)
                break

    def mover_serpiente(self):
        """Mueve la serpiente en la dirección actual"""
        if not self.serpiente_cuerpo:
            return
            
        cabeza_x, cabeza_y = self.serpiente_cuerpo[0]
        dir_x, dir_y = self.serpiente_direccion
        nueva_cabeza = (cabeza_x + dir_x, cabeza_y + dir_y)
        
        # Verificar colisiones con paredes
        if (nueva_cabeza[0] < 0 or nueva_cabeza[0] >= self.ancho or 
            nueva_cabeza[1] < 0 or nueva_cabeza[1] >= self.alto):
            self.juego_terminado = True
            return
        
        # Verificar colisión consigo misma
        if nueva_cabeza in self.serpiente_cuerpo:
            self.juego_terminado = True
            return
        
        # Mover serpiente
        self.serpiente_cuerpo.insert(0, nueva_cabeza)
        
        # Verificar si come comida
        if nueva_cabeza == self.posicion_comida:
            self.puntuacion += 10
            self.generar_comida()
            # Aumentar velocidad cada 50 puntos
            if self.puntuacion % 50 == 0:
                self.velocidad_movimiento *= 1.2
        else:
            self.serpiente_cuerpo.pop()

    def pausar(self):
        """Pausa el juego"""
        print("\nJUEGO EN PAUSA - Presiona cualquier tecla para continuar...")
        msvcrt.getch()

    def mostrar_game_over(self):
        """Muestra pantalla de game over"""
        os.system('cls')
        print("\n" + "=" * 40)
        print("         JUEGO TERMINADO")
        print("=" * 40)
        print(f"    Juego: {self.nombre_juego}")
        print(f"    Puntuación Final: {self.puntuacion}")
        print("\n" + " " * 10 + "Presiona cualquier tecla para salir...")
        msvcrt.getch()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python runtime.py <archivo_juego.ast>")
        sys.exit(1)
    
    archivo_juego = sys.argv[1]
    
    try:
        with open(archivo_juego, 'r', encoding='utf-8') as f:
            datos_juego = json.load(f)
    except IOError:
        print(f"Error: No se pudo encontrar el archivo {archivo_juego}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: El archivo {archivo_juego} no tiene formato JSON válido")
        sys.exit(1)
    
    juego = Juego(datos_juego)
    juego.run()
