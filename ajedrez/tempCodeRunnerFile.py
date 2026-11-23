import os
import random
import sys
import chess
import pygame

# =====================================================================
# CONFIGURACIÓN DE CARPETA Y PIEZAS (LÍNEAS 10 A 26)
# =====================================================================
CARPETA_BASE = os.path.dirname(os.path.abspath(__file__))
CARPETA_FICHAS = os.path.join(CARPETA_BASE, "fichas")  # <-- Nombre de tu carpeta

RUTAS_PIEZAS = {
    # --- PIEZAS BLANCAS ---
    "P": os.path.join(CARPETA_FICHAS, "image.jpg"),
    "R": "",
    "N": "",
    "B": "",
    "Q": "",
    "K": "",
    # --- PIEZAS NEGRAS ---
    "p": os.path.join(CARPETA_FICHAS, "eijklrubgh.png"),
    "r": os.path.join(CARPETA_FICHAS, "idfijkhn.png"),
    "n": "",
    "b": "",
    "q": "",
    "k": "",
}

ANCHO, ALTO = 640, 640
DIMENSION = 8
TAMANO_CASILLA = ANCHO // DIMENSION
FPS = 60
PROFUNDIDAD_IA = 3

COLOR_CLARO = (238, 238, 210)
COLOR_OSCURO = (118, 150, 86)
COLOR_SELECCION = (246, 246, 105)
COLOR_MOVIMIENTO = (186, 202, 68)

PIEZAS_UNICODE = {
    "R": "♖", "N": "♘", "B": "♗", "Q": "♕", "K": "♔",
    "r": "♜", "n": "♞", "b": "♝", "q": "♛", "k": "♚",
    "P": "♙", "p": "♟",
}

VALOR_PIEZAS = {
    chess.PAWN: 10, chess.KNIGHT: 30, chess.BISHOP: 30,
    chess.ROOK: 50, chess.QUEEN: 90, chess.KING: 900,
}


def cargar_todas_las_imagenes(rutas_dict):
    """Carga, recorta fondo blanco y escala todas las imágenes configuradas."""
    imagenes_cargadas = {}
    for simbolo, ruta in rutas_dict.items():
        if not ruta or not os.path.isfile(ruta):
            if ruta:
                print(f"AVISO: No se encontró '{ruta}'")
            imagenes_cargadas[simbolo] = None
            continue
        try:
            img = pygame.image.load(ruta).convert_alpha()
            ancho_orig, alto_orig = img.get_size()
            for x in range(ancho_orig):
                for y in range(alto_orig):
                    r, g, b, a = img.get_at((x, y))
                    if r > 240 and g > 240 and b > 240:
                        img.set_at((x, y), (255, 255, 255, 0))

            ratio = min((TAMANO_CASILLA * 0.92) / ancho_orig, (TAMANO_CASILLA * 0.92) / alto_orig)
            nuevo_tamano = (int(ancho_orig * ratio), int(alto_orig * ratio))
            imagenes_cargadas[simbolo] = pygame.transform.smoothscale(img, nuevo_tamano)
        except Exception as e:
            print(f"Error al cargar '{simbolo}' desde '{ruta}': {e}")
            imagenes_cargadas[simbolo] = None
    return imagenes_cargadas


def evaluar_tablero(tablero):
    if tablero.is_checkmate():
        return -9999 if tablero.turn == chess.WHITE else 9999
    if tablero.is_stalemate() or tablero.is_insufficient_material() or tablero.can_claim_draw():
        return 0
    puntuacion = 0
    for tipo_pieza, valor in VALOR_PIEZAS.items():
        puntuacion += len(tablero.pieces(tipo_pieza, chess.WHITE)) * valor
        puntuacion -= len(tablero.pieces(tipo_pieza, chess.BLACK)) * valor
    return puntuacion


def minimax(tablero, profundidad, alfa, beta, maximizando):
    if profundidad == 0 or tablero.is_game_over():
        return evaluar_tablero(tablero)
    movimientos = list(tablero.legal_moves)
    random.shuffle(movimientos)
    if maximizando:
        max_eval = -float("inf")
        for mov in movimientos:
            tablero.push(mov)
            evaluacion = minimax(tablero, profundidad - 1, alfa, beta, False)
            tablero.pop()
            max_eval = max(max_eval, evaluacion)
            alfa = max(alfa, evaluacion)
            if beta <= alfa:
                break
        return max_eval
    else:
        min_eval = float("inf")
        for mov in movimientos:
            tablero.push(mov)
            evaluacion = minimax(tablero, profundidad - 1, alfa, beta, True)
            tablero.pop()
            min_eval = min(min_eval, evaluacion)
            beta = min(beta, evaluacion)
            if beta <= alfa:
                break
        return min_eval


def obtener_mejor_movimiento_ia(tablero, profundidad):
    mejor_movimiento = None
    mejor_valor = float("inf")
    movimientos = list(tablero.legal_moves)
    random.shuffle(movimientos)
    for mov in movimientos:
        tablero.push(mov)
        valor = minimax(tablero, profundidad - 1, -float("inf"), float("inf"), True)
        tablero.pop()
        if valor < mejor_valor:
            mejor_valor = valor
            mejor_movimiento = mov
    return mejor_movimiento


def dibujar_tablero(pantalla, tablero, casilla_seleccionada, movimientos_validos, imagenes_piezas, fuente):
    for fila in range(DIMENSION):
        for col in range(DIMENSION):
            color = COLOR_CLARO if (fila + col) % 2 == 0 else COLOR_OSCURO
            rect = pygame.Rect(col * TAMANO_CASILLA, fila * TAMANO_CASILLA, TAMANO_CASILLA, TAMANO_CASILLA)
            pygame.draw.rect(pantalla, color, rect)

            casilla_actual = chess.square(col, 7 - fila)

            if casilla_seleccionada == casilla_actual:
                pygame.draw.rect(pantalla, COLOR_SELECCION, rect)

            if casilla_actual in movimientos_validos:
                centro = (col * TAMANO_CASILLA + TAMANO_CASILLA // 2, fila * TAMANO_CASILLA + TAMANO_CASILLA // 2)
                pygame.draw.circle(pantalla, COLOR_MOVIMIENTO, centro, 12)

            pieza = tablero.piece_at(casilla_actual)
            if pieza:
                simbolo = pieza.symbol()
                img_personalizada = imagenes_piezas.get(simbolo)

                if img_personalizada is not None:
                    pantalla.blit(img_personalizada, img_personalizada.get_rect(center=rect.center))
                else:
                    char = PIEZAS_UNICODE.get(simbolo, "♙")
                    color_texto = (255, 255, 255) if pieza.color == chess.WHITE else (0, 0, 0)
                    if pieza.color == chess.WHITE:
                        sombra = fuente.render(char, True, (0, 0, 0))
                        pantalla.blit(sombra, sombra.get_rect(center=(rect.centerx + 2, rect.centery + 2)))
                    texto = fuente.render(char, True, color_texto)
                    pantalla.blit(texto, texto.get_rect(center=rect.center))


def dibujar_fin_partida(pantalla, tablero):
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 170))
    pantalla.blit(overlay, (0, 0))
    fuente_grande = pygame.font.SysFont("arial", 38, bold=True)
    fuente_pequena = pygame.font.SysFont("arial", 22)
    if tablero.is_checkmate():
        ganador = "¡Ganaste! (Blancas)" if tablero.turn == chess.BLACK else "¡Gana la IA! (Negras)"
        mensaje = f"JAQUE MATE - {ganador}"
    else:
        mensaje = "EMPATE / TABLAS"
    texto1 = fuente_grande.render(mensaje, True, (255, 255, 255))
    texto2 = fuente_pequena.render("Pulsa la tecla 'R' para volver a jugar", True, (220, 220, 220))
    pantalla.blit(texto1, texto1.get_rect(center=(ANCHO // 2, ALTO // 2 - 25)))
    pantalla.blit(texto2, texto2.get_rect(center=(ANCHO // 2, ALTO // 2 + 25)))


def main():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Ajedrez vs IA")
    reloj = pygame.time.Clock()

    fuente = pygame.font.SysFont("segoeuisymbol,dejavusans,arialunicode", int(TAMANO_CASILLA * 0.75))
    imagenes_piezas = cargar_todas_las_imagenes(RUTAS_PIEZAS)
    tablero = chess.Board()

    casilla_seleccionada = None
    movimientos_validos = []

    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_r:
                tablero.reset()
                casilla_seleccionada = None
                movimientos_validos = []

            if evento.type == pygame.MOUSEBUTTONDOWN and not tablero.is_game_over() and tablero.turn == chess.WHITE:
                x, y = pygame.mouse.get_pos()
                col = x // TAMANO_CASILLA
                fila = y // TAMANO_CASILLA
                casilla_clic = chess.square(col, 7 - fila)

                if casilla_seleccionada is None:
                    pieza = tablero.piece_at(casilla_clic)
                    if pieza and pieza.color == chess.WHITE:
                        casilla_seleccionada = casilla_clic
                        movimientos_validos = [m.to_square for m in tablero.legal_moves if m.from_square == casilla_clic]
                else:
                    movimiento = chess.Move(casilla_seleccionada, casilla_clic)
                    if tablero.piece_at(casilla_seleccionada).piece_type == chess.PAWN and chess.square_rank(casilla_clic) == 7:
                        movimiento = chess.Move(casilla_seleccionada, casilla_clic, promotion=chess.QUEEN)
                    if movimiento in tablero.legal_moves:
                        tablero.push(movimiento)
                    casilla_seleccionada = None
                    movimientos_validos = []

        dibujar_tablero(pantalla, tablero, casilla_seleccionada, movimientos_validos, imagenes_piezas, fuente)
        if tablero.is_game_over():
            dibujar_fin_partida(pantalla, tablero)

        pygame.display.flip()

        if not tablero.is_game_over() and tablero.turn == chess.BLACK:
            pygame.time.delay(250)
            mov_ia = obtener_mejor_movimiento_ia(tablero, PROFUNDIDAD_IA)
            if mov_ia:
                tablero.push(mov_ia)

        reloj.tick(FPS)


if __name__ == "__main__":
    main()
