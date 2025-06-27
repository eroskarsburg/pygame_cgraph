import pygame
import sys
import time
import random

# Inicialização
pygame.init()
TILE_SIZE = 40
ROWS, COLS = 15, 15
WIDTH, HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE
HUD_HEIGHT = 40
HEIGHT = ROWS * TILE_SIZE + HUD_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bomberman Game")
clock = pygame.time.Clock()

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 150, 255)
GREEN = (0, 255, 0)

# Gerar mapa simples
def generate_map():
    level = []
    for row in range(ROWS):
        row_data = []
        for col in range(COLS):
            if row == 0 or row == ROWS - 1 or col == 0 or col == COLS - 1:
                row_data.append("W")  # Parede externa
            elif row % 2 == 0 and col % 2 == 0:
                row_data.append("W")  # Parede fixa
            else:
                if random.random() < 0.6:
                    row_data.append("B")  # Parede quebrável
                else:
                    row_data.append(" ")  # Espaço vazio
        level.append("".join(row_data))
    
    # Limpa área inicial dos jogadores
    level[1] = level[1][:1] + "   " + level[1][4:]
    level[2] = level[2][:1] + "   " + level[2][4:]
    level[-2] = level[-2][:-4] + "   " + level[-2][-1:]
    level[-3] = level[-3][:-4] + "   " + level[-3][-1:]
    
    return level

level = generate_map()

# Jogadores
player1 = pygame.Rect(TILE_SIZE + 5, TILE_SIZE + HUD_HEIGHT + 5, TILE_SIZE - 10, TILE_SIZE - 10)
player2 = pygame.Rect((COLS - 2) * TILE_SIZE + 5, (ROWS - 2) * TILE_SIZE + HUD_HEIGHT + 5, TILE_SIZE - 10, TILE_SIZE - 10)

# Variáveis do jogo
bombs = []
explosions = []
vidas1 = 3
vidas2 = 3

def draw_level():
    for y, row in enumerate(level):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE + HUD_HEIGHT, TILE_SIZE, TILE_SIZE)
            
            if cell == "W":
                pygame.draw.rect(screen, GRAY, rect)
                pygame.draw.rect(screen, BLACK, rect, 2)
            elif cell == "B":
                pygame.draw.rect(screen, BROWN, rect)
                pygame.draw.rect(screen, BLACK, rect, 2)
            else:
                pygame.draw.rect(screen, WHITE, rect)

def is_wall(pos):
    x, y = pos
    col = x // TILE_SIZE
    row = (y - HUD_HEIGHT) // TILE_SIZE
    try:
        return level[row][col] in ["W", "B"]
    except IndexError:
        return True

def is_bomb(pos):
    x, y = pos
    px = x // TILE_SIZE * TILE_SIZE
    py = (y - HUD_HEIGHT) // TILE_SIZE * TILE_SIZE + HUD_HEIGHT
    for bomb in bombs:
        if bomb["pos"] == (px, py):
            return True
    return False

def break_wall(pos):
    x, y = pos
    col = x // TILE_SIZE
    row = (y - HUD_HEIGHT) // TILE_SIZE
    try:
        if level[row][col] == "B":
            level[row] = level[row][:col] + " " + level[row][col+1:]
            return True
    except IndexError:
        pass
    return False

def mostrar_vencedor(vencedor):
    font = pygame.font.SysFont(None, 60)
    msg = font.render(f"{vencedor} Venceu!", True, BLUE)
    restart_msg = pygame.font.SysFont(None, 30).render("Pressione R para reiniciar", True, BLACK)

    screen.fill(WHITE)
    screen.blit(msg, ((WIDTH - msg.get_width()) // 2, HEIGHT // 2 - 30))
    screen.blit(restart_msg, ((WIDTH - restart_msg.get_width()) // 2, HEIGHT // 2 + 20))
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True

# Loop principal
while True:
    screen.fill(WHITE)
    
    # HUD
    pygame.draw.rect(screen, (200, 200, 200), (0, 0, WIDTH, HUD_HEIGHT))
    font = pygame.font.SysFont(None, 24)
    
    # Vidas
    vida1_text = font.render(f"P1 Vidas: {vidas1}", True, BLACK)
    vida2_text = font.render(f"P2 Vidas: {vidas2}", True, BLACK)
    screen.blit(vida1_text, (10, 10))
    screen.blit(vida2_text, (WIDTH - 120, 10))

    draw_level()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # Player 1 bomba (E)
            if event.key == pygame.K_e:
                bx = player1.x // TILE_SIZE * TILE_SIZE
                by = (player1.y - HUD_HEIGHT) // TILE_SIZE * TILE_SIZE + HUD_HEIGHT
                bomb_pos = (bx, by)
                if all(bomb["pos"] != bomb_pos for bomb in bombs):
                    bombs.append({
                        "rect": pygame.Rect(bx, by, TILE_SIZE, TILE_SIZE),
                        "time": time.time(),
                        "pos": bomb_pos
                    })

            # Player 2 bomba (ESPAÇO)
            if event.key == pygame.K_SPACE:
                bx = player2.x // TILE_SIZE * TILE_SIZE
                by = (player2.y - HUD_HEIGHT) // TILE_SIZE * TILE_SIZE + HUD_HEIGHT
                bomb_pos = (bx, by)
                if all(bomb["pos"] != bomb_pos for bomb in bombs):
                    bombs.append({
                        "rect": pygame.Rect(bx, by, TILE_SIZE, TILE_SIZE),
                        "time": time.time(),
                        "pos": bomb_pos
                    })

    # Movimento Player 1 (WASD)
    keys = pygame.key.get_pressed()
    move_x = move_y = 0
    if keys[pygame.K_a]: move_x = -TILE_SIZE
    if keys[pygame.K_d]: move_x = TILE_SIZE
    if keys[pygame.K_w]: move_y = -TILE_SIZE
    if keys[pygame.K_s]: move_y = TILE_SIZE

    new_pos1 = player1.move(move_x, move_y)
    new_center1 = (new_pos1.x + player1.width // 2, new_pos1.y + player1.height // 2)
    if not is_wall(new_center1) and not is_bomb(new_center1):
        player1 = new_pos1

    # Movimento Player 2 (Setas)
    move2_x = move2_y = 0
    if keys[pygame.K_LEFT]: move2_x = -TILE_SIZE
    if keys[pygame.K_RIGHT]: move2_x = TILE_SIZE
    if keys[pygame.K_UP]: move2_y = -TILE_SIZE
    if keys[pygame.K_DOWN]: move2_y = TILE_SIZE

    new_pos2 = player2.move(move2_x, move2_y)
    new_center2 = (new_pos2.x + player2.width // 2, new_pos2.y + player2.height // 2)
    if not is_wall(new_center2) and not is_bomb(new_center2):
        player2 = new_pos2

    # Processar bombas
    for bomb in bombs[:]:
        if time.time() - bomb["time"] > 2:  # Explode após 2 segundos
            bx, by = bomb["pos"]
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

            # Explosão central
            explosions.append({
                "rect": pygame.Rect(bx, by, TILE_SIZE, TILE_SIZE),
                "time": time.time()
            })

            # Explosão nas 4 direções
            for dx, dy in directions:
                nx = bx + dx * TILE_SIZE
                ny = by + dy * TILE_SIZE
                
                if is_wall((nx + TILE_SIZE // 2, ny + TILE_SIZE // 2)):
                    break_wall((nx + TILE_SIZE // 2, ny + TILE_SIZE // 2))
                else:
                    explosions.append({
                        "rect": pygame.Rect(nx, ny, TILE_SIZE, TILE_SIZE),
                        "time": time.time()
                    })

            bombs.remove(bomb)
        else:
            # Desenhar bomba
            pygame.draw.circle(screen, BLACK, bomb["rect"].center, TILE_SIZE // 3)

    # Processar explosões
    for explosion in explosions[:]:
        if time.time() - explosion["time"] > 0.5:
            explosions.remove(explosion)
        else:
            pygame.draw.rect(screen, ORANGE, explosion["rect"])
            
            # Verificar dano nos jogadores
            if explosion["rect"].colliderect(player1):
                vidas1 -= 1
            if explosion["rect"].colliderect(player2):
                vidas2 -= 1

    # Verificar fim de jogo
    if vidas1 <= 0:
        if mostrar_vencedor("Player 2"):
            # Reiniciar jogo
            level = generate_map()
            player1 = pygame.Rect(TILE_SIZE + 5, TILE_SIZE + HUD_HEIGHT + 5, TILE_SIZE - 10, TILE_SIZE - 10)
            player2 = pygame.Rect((COLS - 2) * TILE_SIZE + 5, (ROWS - 2) * TILE_SIZE + HUD_HEIGHT + 5, TILE_SIZE - 10, TILE_SIZE - 10)
            bombs.clear()
            explosions.clear()
            vidas1 = vidas2 = 3
    
    if vidas2 <= 0:
        if mostrar_vencedor("Player 1"):
            # Reiniciar jogo
            level = generate_map()
            player1 = pygame.Rect(TILE_SIZE + 5, TILE_SIZE + HUD_HEIGHT + 5, TILE_SIZE - 10, TILE_SIZE - 10)
            player2 = pygame.Rect((COLS - 2) * TILE_SIZE + 5, (ROWS - 2) * TILE_SIZE + HUD_HEIGHT + 5, TILE_SIZE - 10, TILE_SIZE - 10)
            bombs.clear()
            explosions.clear()
            vidas1 = vidas2 = 3

    # Desenhar jogadores
    pygame.draw.rect(screen, RED, player1)
    pygame.draw.rect(screen, BLUE, player2)
    
    pygame.display.flip()
    clock.tick(10)
