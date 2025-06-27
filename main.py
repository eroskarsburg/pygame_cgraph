import pygame
import sys
import time
import random

# Inicialização
pygame.init()
TILE_SIZE = 40
ROWS, COLS = 15, 15
WIDTH, HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bomberman Simples")
clock = pygame.time.Clock()

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)
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
            elif random.random() < 0.6:
                row_data.append("B")  # Parede quebrável
            else:
                row_data.append(" ")  # Espaço vazio
        level.append(row_data)
    
    # Limpar spawn dos jogadores
    for i in range(2):
        for j in range(2):
            level[1 + i][1 + j] = " "
            level[ROWS - 2 - i][COLS - 2 - j] = " "
    
    return level

# Variáveis do jogo
level = generate_map()
player1 = pygame.Rect(TILE_SIZE + 5, TILE_SIZE + 5, TILE_SIZE - 10, TILE_SIZE - 10)
player2 = pygame.Rect((COLS - 2) * TILE_SIZE + 5, (ROWS - 2) * TILE_SIZE + 5, TILE_SIZE - 10, TILE_SIZE - 10)
bombs = []
explosions = []
vidas1 = 3
vidas2 = 3

# Funções auxiliares
def draw_map():
    for row in range(ROWS):
        for col in range(COLS):
            rect = pygame.Rect(col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            cell = level[row][col]
            
            if cell == "W":
                pygame.draw.rect(screen, GRAY, rect)
            elif cell == "B":
                pygame.draw.rect(screen, BROWN, rect)
            else:
                pygame.draw.rect(screen, WHITE, rect)
            
            pygame.draw.rect(screen, BLACK, rect, 1)

def is_wall(x, y):
    col = x // TILE_SIZE
    row = y // TILE_SIZE
    if 0 <= row < ROWS and 0 <= col < COLS:
        return level[row][col] in ["W", "B"]
    return True

def place_bomb(player_rect, owner):
    bomb_x = (player_rect.x // TILE_SIZE) * TILE_SIZE
    bomb_y = (player_rect.y // TILE_SIZE) * TILE_SIZE
    
    # Verificar se já existe bomba na posição
    for bomb in bombs:
        if bomb["x"] == bomb_x and bomb["y"] == bomb_y:
            return
    
    bombs.append({
        "x": bomb_x,
        "y": bomb_y,
        "time": time.time(),
        "owner": owner
    })

def explode_bomb(bomb):
    bomb_row = bomb["y"] // TILE_SIZE
    bomb_col = bomb["x"] // TILE_SIZE
    
    explosion_cells = [(bomb_col, bomb_row)]
    
    # Explosão nas 4 direções
    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    for dx, dy in directions:
        for i in range(1, 3):  # Alcance de 2 tiles
            new_col = bomb_col + dx * i
            new_row = bomb_row + dy * i
            
            if 0 <= new_row < ROWS and 0 <= new_col < COLS:
                if level[new_row][new_col] == "W":
                    break  # Parede fixa para explosão
                
                explosion_cells.append((new_col, new_row))
                
                if level[new_row][new_col] == "B":
                    level[new_row][new_col] = " "  # Quebra parede
                    break
            else:
                break
    
    # Criar explosões
    for col, row in explosion_cells:
        explosions.append({
            "x": col * TILE_SIZE,
            "y": row * TILE_SIZE,
            "time": time.time()
        })

# Loop principal
running = True
while running:
    screen.fill(WHITE)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                place_bomb(player1, "p1")
            if event.key == pygame.K_RETURN:
                place_bomb(player2, "p2")
    
    # Movimento
    keys = pygame.key.get_pressed()
    
    # Player 1 (WASD)
    new_x, new_y = player1.x, player1.y
    if keys[pygame.K_a]: new_x -= TILE_SIZE
    if keys[pygame.K_d]: new_x += TILE_SIZE
    if keys[pygame.K_w]: new_y -= TILE_SIZE
    if keys[pygame.K_s]: new_y += TILE_SIZE
    
    if not is_wall(new_x + TILE_SIZE//2, new_y + TILE_SIZE//2):
        player1.x, player1.y = new_x, new_y
    
    # Player 2 (Arrow keys)
    new_x, new_y = player2.x, player2.y
    if keys[pygame.K_LEFT]: new_x -= TILE_SIZE
    if keys[pygame.K_RIGHT]: new_x += TILE_SIZE
    if keys[pygame.K_UP]: new_y -= TILE_SIZE
    if keys[pygame.K_DOWN]: new_y += TILE_SIZE
    
    if not is_wall(new_x + TILE_SIZE//2, new_y + TILE_SIZE//2):
        player2.x, player2.y = new_x, new_y
    
    # Atualizar bombas
    for bomb in bombs[:]:
        if time.time() - bomb["time"] > 3:
            explode_bomb(bomb)
            bombs.remove(bomb)
    
    # Atualizar explosões
    for explosion in explosions[:]:
        if time.time() - explosion["time"] > 0.5:
            explosions.remove(explosion)
    
    # Verificar colisões com explosões
    for explosion in explosions:
        exp_rect = pygame.Rect(explosion["x"], explosion["y"], TILE_SIZE, TILE_SIZE)
        if player1.colliderect(exp_rect):
            vidas1 -= 1
        if player2.colliderect(exp_rect):
            vidas2 -= 1
    
    # Verificar fim de jogo
    if vidas1 <= 0 or vidas2 <= 0:
        font = pygame.font.Font(None, 74)
        winner = "Player 2" if vidas1 <= 0 else "Player 1"
        text = font.render(f"{winner} Wins!", True, BLUE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2))
        pygame.display.flip()
        pygame.time.wait(3000)
        running = False
    
    # Desenhar tudo
    draw_map()
    
    # Desenhar bombas
    for bomb in bombs:
        pygame.draw.circle(screen, BLACK, (bomb["x"] + TILE_SIZE//2, bomb["y"] + TILE_SIZE//2), TILE_SIZE//3)
    
    # Desenhar explosões
    for explosion in explosions:
        pygame.draw.rect(screen, ORANGE, (explosion["x"], explosion["y"], TILE_SIZE, TILE_SIZE))
    
    # Desenhar jogadores
    pygame.draw.rect(screen, RED, player1)
    pygame.draw.rect(screen, BLUE, player2)
    
    pygame.display.flip()
    clock.tick(5)

pygame.quit()
sys.exit()