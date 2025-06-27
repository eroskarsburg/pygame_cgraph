import pygame
import sys
import time

# Inicialização
pygame.init()
TILE_SIZE = 40
ROWS, COLS = 11, 11
WIDTH, HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Mapa fixo simples
level = [
    "WWWWWWWWWWW",
    "W  W  W  W",
    "W WBW WBW W",
    "W  W  W  W",
    "W WBWBWBW W",
    "W  W W W  W",
    "W WBWBWBW W",
    "W  W  W  W",
    "W WBW WBW W",
    "W  W  W  W",
    "WWWWWWWWWWW"
]

# Jogadores
player1 = [1, 1]  # [col, row]
player2 = [9, 9]
bombs = []
explosions = []

# Funções
def draw_map():
    for row in range(ROWS):
        for col in range(COLS):
            x, y = col * TILE_SIZE, row * TILE_SIZE
            cell = level[row][col]
            
            if cell == "W":
                pygame.draw.rect(screen, GRAY, (x, y, TILE_SIZE, TILE_SIZE))
            elif cell == "B":
                pygame.draw.rect(screen, (139, 69, 19), (x, y, TILE_SIZE, TILE_SIZE))
            else:
                pygame.draw.rect(screen, WHITE, (x, y, TILE_SIZE, TILE_SIZE))
            
            pygame.draw.rect(screen, BLACK, (x, y, TILE_SIZE, TILE_SIZE), 1)

def can_move(col, row):
    return 0 <= col < COLS and 0 <= row < ROWS and level[row][col] == " "

def place_bomb(player_pos):
    col, row = player_pos
    for bomb in bombs:
        if bomb["pos"] == [col, row]:
            return
    bombs.append({"pos": [col, row], "time": time.time()})

def explode_bomb(bomb_pos):
    col, row = bomb_pos
    explosion_positions = [[col, row]]
    
    # Explosão nas 4 direções
    for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
        new_col, new_row = col + dx, row + dy
        if 0 <= new_col < COLS and 0 <= new_row < ROWS:
            if level[new_row][new_col] == "B":
                level[new_row] = level[new_row][:new_col] + " " + level[new_row][new_col+1:]
            if level[new_row][new_col] != "W":
                explosion_positions.append([new_col, new_row])
    
    for pos in explosion_positions:
        explosions.append({"pos": pos, "time": time.time()})

# Loop principal
while True:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    # Movimento
    keys = pygame.key.get_pressed()
    
    # Player 1 (WASD)
    if keys[pygame.K_a] and can_move(player1[0]-1, player1[1]): player1[0] -= 1
    if keys[pygame.K_d] and can_move(player1[0]+1, player1[1]): player1[0] += 1
    if keys[pygame.K_w] and can_move(player1[0], player1[1]-1): player1[1] -= 1
    if keys[pygame.K_s] and can_move(player1[0], player1[1]+1): player1[1] += 1
    if keys[pygame.K_SPACE]: place_bomb(player1)
    
    # Player 2 (Arrow keys)
    if keys[pygame.K_LEFT] and can_move(player2[0]-1, player2[1]): player2[0] -= 1
    if keys[pygame.K_RIGHT] and can_move(player2[0]+1, player2[1]): player2[0] += 1
    if keys[pygame.K_UP] and can_move(player2[0], player2[1]-1): player2[1] -= 1
    if keys[pygame.K_DOWN] and can_move(player2[0], player2[1]+1): player2[1] += 1
    if keys[pygame.K_RETURN]: place_bomb(player2)
    
    # Atualizar bombas
    for bomb in bombs[:]:
        if time.time() - bomb["time"] > 2:
            explode_bomb(bomb["pos"])
            bombs.remove(bomb)
    
    # Atualizar explosões
    for explosion in explosions[:]:
        if time.time() - explosion["time"] > 0.3:
            explosions.remove(explosion)
    
    # Verificar colisões
    for explosion in explosions:
        if explosion["pos"] == player1:
            print("Player 2 Wins!")
            pygame.quit()
            sys.exit()
        if explosion["pos"] == player2:
            print("Player 1 Wins!")
            pygame.quit()
            sys.exit()
    
    # Desenhar
    draw_map()
    
    for bomb in bombs:
        x, y = bomb["pos"][0] * TILE_SIZE, bomb["pos"][1] * TILE_SIZE
        pygame.draw.circle(screen, BLACK, (x + TILE_SIZE//2, y + TILE_SIZE//2), 15)
    
    for explosion in explosions:
        x, y = explosion["pos"][0] * TILE_SIZE, explosion["pos"][1] * TILE_SIZE
        pygame.draw.rect(screen, ORANGE, (x, y, TILE_SIZE, TILE_SIZE))
    
    # Jogadores
    x1, y1 = player1[0] * TILE_SIZE + 5, player1[1] * TILE_SIZE + 5
    x2, y2 = player2[0] * TILE_SIZE + 5, player2[1] * TILE_SIZE + 5
    pygame.draw.rect(screen, RED, (x1, y1, TILE_SIZE-10, TILE_SIZE-10))
    pygame.draw.rect(screen, BLUE, (x2, y2, TILE_SIZE-10, TILE_SIZE-10))
    
    pygame.display.flip()
    clock.tick(10)