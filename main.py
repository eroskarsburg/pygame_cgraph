import pygame
import sys
import time
import random

# Inicialização
pygame.init()
TILE_SIZE = 40
ROWS, COLS = 15, 15
WIDTH, HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE
HUD_HEIGHT = 60
HEIGHT = ROWS * TILE_SIZE + HUD_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bomberman Game - Enhanced")
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
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
PINK = (255, 192, 203)
LIGHT_BLUE = (173, 216, 230)
GOLD = (255, 215, 0)

# Power-ups disponíveis
POWERUP_TYPES = ["speed", "bomb_count", "bomb_range", "life"]
POWERUP_COLORS = {
    "speed": YELLOW,
    "bomb_count": PURPLE,
    "bomb_range": GREEN,
    "life": PINK
}

def draw_heart(surface, x, y, size=16, filled=True):
    """Desenha um coração na posição especificada"""
    color = RED if filled else GRAY
    heart_points = []
    
    # Criar pontos do coração
    cx, cy = x + size//2, y + size//2
    for angle in range(0, 360, 10):
        # Fórmula paramétrica do coração
        rad = angle * 3.14159 / 180
        heart_x = 16 * (pow(sin(rad), 3))
        heart_y = -13 * cos(rad) + 5 * cos(2*rad) + 2 * cos(3*rad) + cos(4*rad)
        
        # Escalar e posicionar
        px = cx + int(heart_x * size / 32)
        py = cy + int(heart_y * size / 32)
        heart_points.append((px, py))
    
    if len(heart_points) > 2:
        pygame.draw.polygon(surface, color, heart_points)
        pygame.draw.polygon(surface, BLACK, heart_points, 2)

def sin(x):
    """Função seno simples"""
    import math
    return math.sin(x)

def cos(x):
    """Função cosseno simples"""
    import math
    return math.cos(x)

# Gerar mapa simples
def generate_map():
    level = []
    powerups = []
    
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
                    # Chance de ter power-up atrás da parede
                    if random.random() < 0.3:
                        powerups.append({
                            "pos": (col, row),
                            "type": random.choice(POWERUP_TYPES),
                            "visible": False
                        })
                else:
                    row_data.append(" ")  # Espaço vazio
        level.append("".join(row_data))
    
    # Limpa área inicial dos jogadores
    level[1] = level[1][:1] + "   " + level[1][4:]
    level[2] = level[2][:1] + "   " + level[2][4:]
    level[-2] = level[-2][:-4] + "   " + level[-2][-1:]
    level[-3] = level[-3][:-4] + "   " + level[-3][-1:]
    
    return level, powerups

level, powerups = generate_map()

# Jogadores com atributos aprimorados
class Player:
    def __init__(self, x, y, color, max_bombs=1, bomb_range=1, speed=1):
        self.rect = pygame.Rect(x, y, TILE_SIZE - 10, TILE_SIZE - 10)
        self.color = color
        self.lives = 3
        self.max_bombs = max_bombs
        self.bomb_range = bomb_range
        self.speed = speed
        self.active_bombs = 0
        self.invulnerable_time = 0
    
    def can_place_bomb(self):
        return self.active_bombs < self.max_bombs
    
    def place_bomb(self):
        if self.can_place_bomb():
            self.active_bombs += 1
    
    def bomb_exploded(self):
        self.active_bombs = max(0, self.active_bombs - 1)
    
    def take_damage(self):
        if time.time() > self.invulnerable_time:
            self.lives -= 1
            self.invulnerable_time = time.time() + 1.5  # 1.5 segundos de invulnerabilidade
            return True
        return False
    
    def is_invulnerable(self):
        return time.time() < self.invulnerable_time

player1 = Player(TILE_SIZE + 5, TILE_SIZE + HUD_HEIGHT + 5, RED)
player2 = Player((COLS - 2) * TILE_SIZE + 5, (ROWS - 2) * TILE_SIZE + HUD_HEIGHT + 5, BLUE)

# Variáveis do jogo
bombs = []
explosions = []

def draw_level():
    for y, row in enumerate(level):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE + HUD_HEIGHT, TILE_SIZE, TILE_SIZE)
            
            if cell == "W":
                pygame.draw.rect(screen, GRAY, rect)
                pygame.draw.rect(screen, BLACK, rect, 2)
                # Adicionar textura às paredes
                for i in range(0, TILE_SIZE, 8):
                    for j in range(0, TILE_SIZE, 8):
                        if (i + j) % 16 == 0:
                            pygame.draw.rect(screen, (100, 100, 100), 
                                           (rect.x + i, rect.y + j, 4, 4))
            elif cell == "B":
                pygame.draw.rect(screen, BROWN, rect)
                pygame.draw.rect(screen, BLACK, rect, 2)
                # Textura das paredes quebráveis
                pygame.draw.rect(screen, (120, 80, 40), 
                               (rect.x + 5, rect.y + 5, TILE_SIZE - 10, TILE_SIZE - 10))
                for i in range(10, TILE_SIZE - 10, 6):
                    pygame.draw.line(screen, (100, 60, 20), 
                                   (rect.x + i, rect.y + 5), 
                                   (rect.x + i, rect.y + TILE_SIZE - 5), 2)
            else:
                pygame.draw.rect(screen, WHITE, rect)
                # Grid sutil
                pygame.draw.rect(screen, (240, 240, 240), rect, 1)

def draw_powerups():
    for powerup in powerups:
        if powerup["visible"]:
            x, y = powerup["pos"]
            rect = pygame.Rect(x * TILE_SIZE + 5, y * TILE_SIZE + HUD_HEIGHT + 5, 
                             TILE_SIZE - 10, TILE_SIZE - 10)
            
            # Desenhar power-up com efeito de brilho
            color = POWERUP_COLORS[powerup["type"]]
            pygame.draw.ellipse(screen, color, rect)
            pygame.draw.ellipse(screen, BLACK, rect, 2)
            
            # Símbolo do power-up
            font = pygame.font.SysFont(None, 20)
            symbol = ""
            if powerup["type"] == "speed":
                symbol = "S"
            elif powerup["type"] == "bomb_count":
                symbol = "B"
            elif powerup["type"] == "bomb_range":
                symbol = "R"
            elif powerup["type"] == "life":
                symbol = "♥"
            
            text = font.render(symbol, True, BLACK)
            text_rect = text.get_rect(center=rect.center)
            screen.blit(text, text_rect)

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
            # Revelar power-up se existir
            for powerup in powerups:
                if powerup["pos"] == (col, row):
                    powerup["visible"] = True
            return True
    except IndexError:
        pass
    return False

def check_powerup_collision(player):
    player_center = player.rect.center
    col = player_center[0] // TILE_SIZE
    row = (player_center[1] - HUD_HEIGHT) // TILE_SIZE
    
    for powerup in powerups[:]:
        if powerup["visible"] and powerup["pos"] == (col, row):
            # Aplicar efeito do power-up
            if powerup["type"] == "speed":
                player.speed = min(3, player.speed + 1)
            elif powerup["type"] == "bomb_count":
                player.max_bombs = min(5, player.max_bombs + 1)
            elif powerup["type"] == "bomb_range":
                player.bomb_range = min(4, player.bomb_range + 1)
            elif powerup["type"] == "life":
                player.lives = min(5, player.lives + 1)
            
            powerups.remove(powerup)
            return True
    return False

def draw_hud():
    # Fundo do HUD
    pygame.draw.rect(screen, (220, 220, 220), (0, 0, WIDTH, HUD_HEIGHT))
    pygame.draw.line(screen, BLACK, (0, HUD_HEIGHT), (WIDTH, HUD_HEIGHT), 2)
    
    font = pygame.font.SysFont(None, 24)
    small_font = pygame.font.SysFont(None, 18)
    
    # Player 1 info
    p1_text = font.render("Player 1", True, player1.color)
    screen.blit(p1_text, (10, 5))
    
    # Corações do Player 1
    for i in range(5):
        draw_heart(screen, 15 + i * 20, 25, 16, i < player1.lives)
    
    # Stats Player 1
    stats1 = f"Bombas: {player1.max_bombs} | Alcance: {player1.bomb_range} | Vel: {player1.speed}"
    stats1_text = small_font.render(stats1, True, BLACK)
    screen.blit(stats1_text, (10, 45))
    
    # Player 2 info
    p2_text = font.render("Player 2", True, player2.color)
    p2_rect = p2_text.get_rect()
    p2_rect.topright = (WIDTH - 10, 5)
    screen.blit(p2_text, p2_rect)
    
    # Corações do Player 2
    for i in range(5):
        draw_heart(screen, WIDTH - 115 + i * 20, 25, 16, i < player2.lives)
    
    # Stats Player 2
    stats2 = f"Bombas: {player2.max_bombs} | Alcance: {player2.bomb_range} | Vel: {player2.speed}"
    stats2_text = small_font.render(stats2, True, BLACK)
    stats2_rect = stats2_text.get_rect()
    stats2_rect.topright = (WIDTH - 10, 45)
    screen.blit(stats2_text, stats2_rect)

def mostrar_vencedor(vencedor):
    # Efeito de fade
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.set_alpha(180)
    fade_surface.fill(BLACK)
    screen.blit(fade_surface, (0, 0))
    
    font = pygame.font.SysFont(None, 80)
    msg = font.render(f"{vencedor} Venceu!", True, GOLD)
    msg_rect = msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
    screen.blit(msg, msg_rect)
    
    # Borda dourada no texto
    pygame.draw.rect(screen, GOLD, msg_rect.inflate(20, 10), 3)
    
    restart_font = pygame.font.SysFont(None, 36)
    restart_msg = restart_font.render("Pressione R para reiniciar", True, WHITE)
    restart_rect = restart_msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 40))
    screen.blit(restart_msg, restart_rect)
    
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True

def reset_game():
    global level, powerups, bombs, explosions, player1, player2
    level, powerups = generate_map()
    player1 = Player(TILE_SIZE + 5, TILE_SIZE + HUD_HEIGHT + 5, RED)
    player2 = Player((COLS - 2) * TILE_SIZE + 5, (ROWS - 2) * TILE_SIZE + HUD_HEIGHT + 5, BLUE)
    bombs.clear()
    explosions.clear()

# Loop principal
while True:
    screen.fill(WHITE)
    
    draw_hud()
    draw_level()
    draw_powerups()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # Player 1 bomba (E)
            if event.key == pygame.K_e and player1.can_place_bomb():
                bx = player1.rect.x // TILE_SIZE * TILE_SIZE
                by = (player1.rect.y - HUD_HEIGHT) // TILE_SIZE * TILE_SIZE + HUD_HEIGHT
                bomb_pos = (bx, by)
                if all(bomb["pos"] != bomb_pos for bomb in bombs):
                    player1.place_bomb()
                    bombs.append({
                        "rect": pygame.Rect(bx, by, TILE_SIZE, TILE_SIZE),
                        "time": time.time(),
                        "pos": bomb_pos,
                        "range": player1.bomb_range,
                        "owner": player1
                    })

            # Player 2 bomba (ESPAÇO)
            if event.key == pygame.K_SPACE and player2.can_place_bomb():
                bx = player2.rect.x // TILE_SIZE * TILE_SIZE
                by = (player2.rect.y - HUD_HEIGHT) // TILE_SIZE * TILE_SIZE + HUD_HEIGHT
                bomb_pos = (bx, by)
                if all(bomb["pos"] != bomb_pos for bomb in bombs):
                    player2.place_bomb()
                    bombs.append({
                        "rect": pygame.Rect(bx, by, TILE_SIZE, TILE_SIZE),
                        "time": time.time(),
                        "pos": bomb_pos,
                        "range": player2.bomb_range,
                        "owner": player2
                    })

    # Movimento Player 1 (WASD)
    keys = pygame.key.get_pressed()
    move_x = move_y = 0
    move_speed = player1.speed * 5
    
    if keys[pygame.K_a]: move_x = -move_speed
    if keys[pygame.K_d]: move_x = move_speed
    if keys[pygame.K_w]: move_y = -move_speed
    if keys[pygame.K_s]: move_y = move_speed

    new_pos1 = player1.rect.move(move_x, move_y)
    new_center1 = (new_pos1.x + player1.rect.width // 2, new_pos1.y + player1.rect.height // 2)
    if not is_wall(new_center1) and not is_bomb(new_center1):
        player1.rect = new_pos1
        check_powerup_collision(player1)

    # Movimento Player 2 (Setas)
    move2_x = move2_y = 0
    move2_speed = player2.speed * 5
    
    if keys[pygame.K_LEFT]: move2_x = -move2_speed
    if keys[pygame.K_RIGHT]: move2_x = move2_speed
    if keys[pygame.K_UP]: move2_y = -move2_speed
    if keys[pygame.K_DOWN]: move2_y = move2_speed

    new_pos2 = player2.rect.move(move2_x, move2_y)
    new_center2 = (new_pos2.x + player2.rect.width // 2, new_pos2.y + player2.rect.height // 2)
    if not is_wall(new_center2) and not is_bomb(new_center2):
        player2.rect = new_pos2
        check_powerup_collision(player2)

    # Processar bombas
    for bomb in bombs[:]:
        if time.time() - bomb["time"] > 2.5:  # Explode após 2.5 segundos
            bx, by = bomb["pos"]
            bomb_range = bomb["range"]
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

            # Explosão central
            explosions.append({
                "rect": pygame.Rect(bx, by, TILE_SIZE, TILE_SIZE),
                "time": time.time()
            })

            # Explosão nas 4 direções
            for dx, dy in directions:
                for i in range(1, bomb_range + 1):
                    nx = bx + dx * TILE_SIZE * i
                    ny = by + dy * TILE_SIZE * i
                    
                    if is_wall((nx + TILE_SIZE // 2, ny + TILE_SIZE // 2)):
                        break_wall((nx + TILE_SIZE // 2, ny + TILE_SIZE // 2))
                        break
                    else:
                        explosions.append({
                            "rect": pygame.Rect(nx, ny, TILE_SIZE, TILE_SIZE),
                            "time": time.time()
                        })

            bomb["owner"].bomb_exploded()
            bombs.remove(bomb)
        else:
            # Desenhar bomba com animação
            bomb_time = time.time() - bomb["time"]
            if bomb_time > 1.5:  # Piscar nos últimos momentos
                if int(bomb_time * 10) % 2:
                    pygame.draw.circle(screen, RED, bomb["rect"].center, TILE_SIZE // 3)
                else:
                    pygame.draw.circle(screen, ORANGE, bomb["rect"].center, TILE_SIZE // 3)
            else:
                pygame.draw.circle(screen, BLACK, bomb["rect"].center, TILE_SIZE // 3)
            
            # Fusível da bomba
            pygame.draw.circle(screen, WHITE, 
                             (bomb["rect"].centerx, bomb["rect"].centery - TILE_SIZE // 4), 3)

    # Processar explosões
    for explosion in explosions[:]:
        if time.time() - explosion["time"] > 0.5:
            explosions.remove(explosion)
        else:
            # Efeito de explosão mais elaborado
            explosion_time = time.time() - explosion["time"]
            if explosion_time < 0.2:
                pygame.draw.rect(screen, YELLOW, explosion["rect"])
            else:
                pygame.draw.rect(screen, ORANGE, explosion["rect"])
            
            pygame.draw.rect(screen, RED, explosion["rect"], 3)
            
            # Verificar dano nos jogadores
            if explosion["rect"].colliderect(player1.rect):
                player1.take_damage()
            if explosion["rect"].colliderect(player2.rect):
                player2.take_damage()

    # Verificar fim de jogo
    if player1.lives <= 0:
        if mostrar_vencedor("Player 2"):
            reset_game()
    
    if player2.lives <= 0:
        if mostrar_vencedor("Player 1"):
            reset_game()

    # Desenhar jogadores com efeito de invulnerabilidade
    if player1.is_invulnerable() and int(time.time() * 10) % 2:
        pygame.draw.rect(screen, (255, 100, 100), player1.rect)
    else:
        pygame.draw.rect(screen, player1.color, player1.rect)
    pygame.draw.rect(screen, BLACK, player1.rect, 2)
    
    if player2.is_invulnerable() and int(time.time() * 10) % 2:
        pygame.draw.rect(screen, (100, 150, 255), player2.rect)
    else:
        pygame.draw.rect(screen, player2.color, player2.rect)
    pygame.draw.rect(screen, BLACK, player2.rect, 2)
    
    pygame.display.flip()
    clock.tick(60)  # Aumentei para 60 FPS para movimento mais suave