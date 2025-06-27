import pygame
import sys
import time
import requests
import io
import math
import random

# Mapa base
level_template = [
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW",
    "W     W     W       W     W     W     W",
    "W WWW W WWW W WWWWW W WWW W WWW W WWW W",
    "W W   W   W     W   W W   W W   W W   W",
    "W W WWWWW WWWWW W WWW W WWW W WWW W W W",
    "W W     W     W W     W     W       W W",
    "W WWWWW W WWW W WWWWW   WWWWW W W W W W",
    "W     W W   W W       W       W W W W W",
    "WWWWW W WWW W WWWWWWW W WWWWW W W W W W",
    "W     W             W W     W W   W   W",
    "W WWWWW W WWW W WWW W WWWWW W WWWWWWWWW",
    "W       W     W W   W     W W         W",
    "WWWWWWW W WWWWW W WWWWWWW W WWWWW WWW W",
    "W       W     W W     W   W           W",
    "W WWWWWWW WWWWW WWWWW W WWWWWWWWW W W W",
    "W     W             W W         W W W W",
    "W WWW W WWWWWWW W W W W WWWWWWW W W W W",
    "W W   W       W W W             W     W",
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW"
]

# Função para gerar paredes quebráveis
def generate_breakable_walls(rows=15,cols=15):
    level = []
    for row in range(rows):
        row_data = []
        for col in range(cols):
            if row == 0 or row == rows - 1 or col == 0 or col == cols - 1:
                # Bordas externas do mapa
                row_data.append("W")
            elif row % 2 == 0 and col % 2 == 0:
                # Blocos fixos em grade regular
                row_data.append("W")
            else:
                # Espaços vazios ou blocos quebráveis
                if random.random() < 0.8:
                    row_data.append("B")  # Bloco quebrável
                else:
                    row_data.append(" ")  # Espaço vazio
        level.append("".join(row_data))

    # Limpa áreas iniciais para os jogadores
    level[1] = level[1][:1] + "     " + level[1][6:]
    level[2] = level[2][:1] + "     " + level[2][6:]
    level[-2] = level[-2][:-6] + "     " + level[-2][-1:]
    level[-3] = level[-3][:-6] + "     " + level[-3][-1:]

    return level

# Inicialização
pygame.init()
TILE_SIZE = 40
level = generate_breakable_walls()  # Gera o mapa com paredes quebráveis
ROWS, COLS = 15, 15
WIDTH, HEIGHT = COLS * TILE_SIZE, ROWS * TILE_SIZE
HUD_HEIGHT = 60
HEIGHT = ROWS * TILE_SIZE + HUD_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BomberRats")
clock = pygame.time.Clock()

# Cores aprimoradas para efeitos 3D
WHITE = (255, 255, 255)
FLOOR_COLOR = (240, 240, 240)
SHADOW_COLOR = (50, 50, 50)

# Cores para paredes fixas (cinza metálico)
WALL_BASE = (120, 120, 130)
WALL_LIGHT = (180, 180, 190)
WALL_DARK = (70, 70, 80)
WALL_HIGHLIGHT = (220, 220, 230)

# Cores para paredes quebráveis (marrom)
BREAKABLE_BASE = (139, 90, 43)
BREAKABLE_LIGHT = (200, 130, 70)
BREAKABLE_DARK = (90, 60, 30)
BREAKABLE_HIGHLIGHT = (240, 160, 90)

RED = (255, 0, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 150, 255)

def draw_3d_wall(surface, rect, wall_type="fixed"):
    """Desenha uma parede com efeito 3D realista"""
    x, y, w, h = rect
    
    # Define cores baseadas no tipo de parede
    if wall_type == "fixed":
        base_color = WALL_BASE
        light_color = WALL_LIGHT
        dark_color = WALL_DARK
        highlight_color = WALL_HIGHLIGHT
    else:  # breakable
        base_color = BREAKABLE_BASE
        light_color = BREAKABLE_LIGHT
        dark_color = BREAKABLE_DARK
        highlight_color = BREAKABLE_HIGHLIGHT
    
    # Tamanho do bisel (efeito 3D)
    bevel = 4
    
    # Desenha sombra (projetada no chão)
    shadow_offset = 2
    shadow_rect = pygame.Rect(x + shadow_offset, y + h - 2, w, 4)
    pygame.draw.rect(surface, SHADOW_COLOR, shadow_rect)
    
    # Face principal da parede
    main_rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, base_color, main_rect)
    
    # Face superior (iluminada)
    top_points = [
        (x, y),
        (x + bevel, y - bevel),
        (x + w + bevel, y - bevel),
        (x + w, y)
    ]
    pygame.draw.polygon(surface, light_color, top_points)
    
    # Face direita (meio iluminada)
    right_points = [
        (x + w, y),
        (x + w + bevel, y - bevel),
        (x + w + bevel, y + h - bevel),
        (x + w, y + h)
    ]
    pygame.draw.polygon(surface, dark_color, right_points)
    
    # Highlight na borda superior esquerda
    pygame.draw.line(surface, highlight_color, (x, y), (x + w - 1, y), 1)
    pygame.draw.line(surface, highlight_color, (x, y), (x, y + h - 1), 1)
    
    # Sombra interna na borda inferior direita
    shadow_inner = tuple(max(0, c - 30) for c in base_color)
    pygame.draw.line(surface, shadow_inner, (x + w - 1, y + 1), (x + w - 1, y + h - 1), 1)
    pygame.draw.line(surface, shadow_inner, (x + 1, y + h - 1), (x + w - 1, y + h - 1), 1)
    
    # Adiciona textura para paredes quebráveis
    if wall_type == "breakable":
        # Desenha algumas "rachaduras" ou detalhes
        for i in range(3):
            crack_x = x + random.randint(5, w - 5)
            crack_y = y + random.randint(5, h - 5)
            crack_color = tuple(max(0, c - 40) for c in base_color)
            pygame.draw.circle(surface, crack_color, (crack_x, crack_y), 2)
        
        # Adiciona alguns pontos de desgaste
        for i in range(5):
            wear_x = x + random.randint(2, w - 2)
            wear_y = y + random.randint(2, h - 2)
            wear_color = tuple(min(255, c + 20) for c in base_color)
            pygame.draw.rect(surface, wear_color, (wear_x, wear_y, 2, 2))

def draw_floor_tile(surface, rect):
    """Desenha um tile do chão com textura sutil"""
    x, y, w, h = rect
    
    # Cor base do chão
    pygame.draw.rect(surface, FLOOR_COLOR, rect)
    
    # Adiciona uma grade sutil
    grid_color = (220, 220, 220)
    pygame.draw.line(surface, grid_color, (x, y), (x + w, y), 1)
    pygame.draw.line(surface, grid_color, (x, y), (x, y + h), 1)
    
    # Adiciona pontos aleatórios para textura
    for i in range(2):
        dot_x = x + random.randint(5, w - 5)
        dot_y = y + random.randint(5, h - 5)
        dot_color = (230, 230, 230)
        pygame.draw.circle(surface, dot_color, (dot_x, dot_y), 1)

# Função para encontrar a última posição válida no mapa
def find_last_valid_position():
    # Procura de trás para frente e de baixo para cima por um espaço vazio
    for row in range(len(level) - 1, -1, -1):
        for col in range(len(level[row]) - 1, -1, -1):
            if level[row][col] == ' ':  # espaço vazio
                x = col * TILE_SIZE + 5  # adiciona um pequeno offset
                y = row * TILE_SIZE + HUD_HEIGHT + 5
                return x, y
    # Se não encontrar, usa uma posição padrão segura
    return TILE_SIZE + 5, TILE_SIZE + HUD_HEIGHT + 5

# Personagem
player = pygame.Rect(45, 45 + HUD_HEIGHT, TILE_SIZE - 10, TILE_SIZE - 10)

# Encontra a posição correta para o player2
player2_x, player2_y = find_last_valid_position()
player2 = pygame.Rect(player2_x, player2_y, TILE_SIZE - 10, TILE_SIZE - 10)

# Imagem da bomba
bomb_url = "https://cdn-icons-png.flaticon.com/512/112/112683.png"
response = requests.get(bomb_url)
bomb_file = io.BytesIO(response.content)
bomb_img = pygame.image.load(bomb_file).convert_alpha()
bomb_img = pygame.transform.scale(bomb_img, (TILE_SIZE, TILE_SIZE))

# Imagem de coração (vida)
heart_url = "https://cdn-icons-png.flaticon.com/512/833/833472.png"
response = requests.get(heart_url)
heart_file = io.BytesIO(response.content)
heart_img = pygame.image.load(heart_file).convert_alpha()
heart_img = pygame.transform.scale(heart_img, (30, 30))

# Bomba Powerup
def create_powerup_image(size=(30, 30)):
    """Cria uma imagem de power-up de bomba como fallback"""
    surf = pygame.Surface(size, pygame.SRCALPHA)
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # Desenha o corpo da bomba (círculo preto)
    pygame.draw.circle(surf, (40, 40, 40), (center_x, center_y), size[0] // 3)
    pygame.draw.circle(surf, (20, 20, 20), (center_x, center_y), size[0] // 3, 2)
    
    # Desenha o pavio (linha laranja/vermelha)
    pygame.draw.line(surf, (255, 165, 0), 
                    (center_x - 2, center_y - size[1] // 3), 
                    (center_x - 8, center_y - size[1] // 2), 3)
    
    # Adiciona brilho
    pygame.draw.circle(surf, (80, 80, 80), (center_x - 4, center_y - 4), 4)
    
    # Adiciona símbolo + para indicar power-up
    plus_color = (255, 255, 0)  # Amarelo
    plus_size = 8
    pygame.draw.line(surf, plus_color, 
                    (center_x - plus_size//2, center_y + size[1]//4), 
                    (center_x + plus_size//2, center_y + size[1]//4), 2)
    pygame.draw.line(surf, plus_color, 
                    (center_x, center_y + size[1]//4 - plus_size//2), 
                    (center_x, center_y + size[1]//4 + plus_size//2), 2)
    
    return surf
    
powerup_img = create_powerup_image((30, 30))

powerups = []  # Lista de power-ups no mapa
POWERUP_SIZE = TILE_SIZE
player_speed = TILE_SIZE
bombs = []
explosions = []
vidas = 3
vidas2 = 3
max_bombas_p1 = 1
max_bombas_p2 = 1

clock = pygame.time.Clock()

# ADICIONE ESTAS FUNÇÕES DEPOIS DA LINHA 'clock = pygame.time.Clock()'

def draw_button(surface, rect, text, font, bg_color, text_color, border_color=None):
    """Desenha um botão com texto"""
    pygame.draw.rect(surface, bg_color, rect)
    if border_color:
        pygame.draw.rect(surface, border_color, rect, 3)
    
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=rect.center)
    surface.blit(text_surface, text_rect)
    
    return rect

def menu_principal():
    """Tela do menu principal"""
    font_title = pygame.font.SysFont(None, 72)
    font_button = pygame.font.SysFont(None, 48)
    
    # Cores
    bg_color = (30, 30, 50)
    button_color = (70, 130, 180)
    button_hover = (100, 160, 210)
    text_color = (255, 255, 255)
    title_color = (255, 215, 0)
    
    # Posições dos botões
    button_width, button_height = 300, 80
    button_x = (WIDTH - button_width) // 2
    
    iniciar_btn = pygame.Rect(button_x, HEIGHT // 2 - 60, button_width, button_height)
    sair_btn = pygame.Rect(button_x, HEIGHT // 2 + 40, button_width, button_height)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if iniciar_btn.collidepoint(mouse_pos):
                    return "iniciar"
                elif sair_btn.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()
        
        # Desenha fundo
        screen.fill(bg_color)
        
        # Título
        title_text = font_title.render("BOMBERRATS", True, title_color)
        title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))
        screen.blit(title_text, title_rect)

        # Texto de boas-vindas personalizado
        welcome_font = pygame.font.Font(None, 28)
        welcome_text1 = welcome_font.render("Bem-vindo, Jogador!", True, (255, 255, 255))
        welcome_text2 = welcome_font.render("Prepare-se para um duelo explosivo!", True, (200, 200, 200))
        welcome_text3 = welcome_font.render("Use bem suas bombas para garantir a vitória!", True, (180, 180, 180))

        # Posicionamento do texto de boas-vindas
        welcome_y = title_rect.bottom + 30
        welcome_rect1 = welcome_text1.get_rect(center=(WIDTH // 2, welcome_y))
        welcome_rect2 = welcome_text2.get_rect(center=(WIDTH // 2, welcome_y + 35))
        welcome_rect3 = welcome_text3.get_rect(center=(WIDTH // 2, welcome_y + 65))

        screen.blit(welcome_text1, welcome_rect1)
        screen.blit(welcome_text2, welcome_rect2)
        screen.blit(welcome_text3, welcome_rect3)

        # Desenhar bomba decorativa (lado esquerdo do título)
        bomb_size = 40
        bomb_x = title_rect.left - bomb_size - 20
        bomb_y = title_rect.centery - bomb_size // 2

        # Corpo da bomba (círculo preto)
        pygame.draw.circle(screen, (50, 50, 50), (bomb_x + bomb_size // 2, bomb_y + bomb_size // 2), bomb_size // 2)
        pygame.draw.circle(screen, (0, 0, 0), (bomb_x + bomb_size // 2, bomb_y + bomb_size // 2), bomb_size // 2, 3)

        # Pavio da bomba
        fuse_start_x = bomb_x + bomb_size // 2 + 5
        fuse_start_y = bomb_y + 5
        fuse_points = [
            (fuse_start_x, fuse_start_y),
            (fuse_start_x + 8, fuse_start_y - 8),
            (fuse_start_x + 15, fuse_start_y - 5),
            (fuse_start_x + 20, fuse_start_y - 12)
        ]
        pygame.draw.lines(screen, (139, 69, 19), False, fuse_points, 3)

        # Fagulha no final do pavio
        spark_x, spark_y = fuse_points[-1]
        pygame.draw.circle(screen, (255, 165, 0), (spark_x, spark_y), 3)
        pygame.draw.circle(screen, (255, 255, 0), (spark_x, spark_y), 2)

        # Bomba decorativa do lado direito (espelhada)
        bomb_x_right = title_rect.right + 20
        pygame.draw.circle(screen, (50, 50, 50), (bomb_x_right + bomb_size // 2, bomb_y + bomb_size // 2), bomb_size // 2)
        pygame.draw.circle(screen, (0, 0, 0), (bomb_x_right + bomb_size // 2, bomb_y + bomb_size // 2), bomb_size // 2, 3)

        # Pavio da bomba direita
        fuse_start_x_right = bomb_x_right + bomb_size // 2 - 5
        fuse_points_right = [
            (fuse_start_x_right, fuse_start_y),
            (fuse_start_x_right - 8, fuse_start_y - 8),
            (fuse_start_x_right - 15, fuse_start_y - 5),
            (fuse_start_x_right - 20, fuse_start_y - 12)
        ]
        pygame.draw.lines(screen, (139, 69, 19), False, fuse_points_right, 3)

        # Fagulha da bomba direita
        spark_x_right, spark_y_right = fuse_points_right[-1]
        pygame.draw.circle(screen, (255, 165, 0), (spark_x_right, spark_y_right), 3)
        pygame.draw.circle(screen, (255, 255, 0), (spark_x_right, spark_y_right), 2)

        # Reposicionar os botões para ficarem abaixo do texto de boas-vindas
        button_y_start = welcome_rect3.bottom + 50
        iniciar_btn = pygame.Rect(WIDTH // 2 - 100, button_y_start, 200, 50)
        sair_btn = pygame.Rect(WIDTH // 2 - 100, button_y_start + 70, 200, 50)

        # Botões com efeito hover
        iniciar_color = button_hover if iniciar_btn.collidepoint(mouse_pos) else button_color
        sair_color = button_hover if sair_btn.collidepoint(mouse_pos) else button_color

        draw_button(screen, iniciar_btn, "INICIAR", font_button, iniciar_color, text_color)
        draw_button(screen, sair_btn, "SAIR", font_button, sair_color, text_color)
        
        pygame.display.flip()
        clock.tick(60)

def tela_instrucoes():
    """Tela de instruções dos comandos"""
    font_title = pygame.font.SysFont(None, 60)
    font_subtitle = pygame.font.SysFont(None, 42)
    font_text = pygame.font.SysFont(None, 36)
    font_button = pygame.font.SysFont(None, 48)
    
    # Cores
    bg_color = (30, 30, 50)
    button_color = (70, 130, 180)
    button_hover = (100, 160, 210)
    text_color = (255, 255, 255)
    title_color = (255, 215, 0)
    p1_color = (255, 100, 100)  # Vermelho claro
    p2_color = (100, 150, 255)  # Azul claro
    
    # Botão continuar
    button_width, button_height = 200, 60
    continuar_btn = pygame.Rect((WIDTH - button_width) // 2, HEIGHT - 100, button_width, button_height)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if continuar_btn.collidepoint(mouse_pos):
                    return "continuar"
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return "continuar"
        
        # Desenha fundo
        screen.fill(bg_color)
        
        # Título
        title_text = font_title.render("INSTRUÇÕES", True, title_color)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 80))
        screen.blit(title_text, title_rect)
        
        # Divisão vertical
        linha_y = 150
        
        # JOGADOR 1 (lado esquerdo)
        p1_title = font_subtitle.render("JOGADOR 1", True, p1_color)
        p1_title_rect = p1_title.get_rect(center=(WIDTH // 4, linha_y))
        screen.blit(p1_title, p1_title_rect)
        
        # Comandos P1
        comandos_p1 = [
            "W A S D - Mover",
            "E - Colocar Bomba"
        ]
        
        y_offset = 200
        for comando in comandos_p1:
            cmd_text = font_text.render(comando, True, text_color)
            cmd_rect = cmd_text.get_rect(center=(WIDTH // 4, y_offset))
            screen.blit(cmd_text, cmd_rect)
            y_offset += 50
        
        # JOGADOR 2 (lado direito)
        p2_title = font_subtitle.render("JOGADOR 2", True, p2_color)
        p2_title_rect = p2_title.get_rect(center=(3 * WIDTH // 4, linha_y))
        screen.blit(p2_title, p2_title_rect)
        
        # Comandos P2
        comandos_p2 = [
            "SETAS - Mover",
            "ESPAÇO - Colocar Bomba"
        ]
        
        y_offset = 200
        for comando in comandos_p2:
            cmd_text = font_text.render(comando, True, text_color)
            cmd_rect = cmd_text.get_rect(center=(3 * WIDTH // 4, y_offset))
            screen.blit(cmd_text, cmd_rect)
            y_offset += 50
        
        # Linha divisória vertical
        pygame.draw.line(screen, (100, 100, 100), (WIDTH // 2, 140), (WIDTH // 2, HEIGHT - 120), 2)
        
        # Dica adicional
        dica_text = font_text.render("Colete power-ups para mais bombas!", True, (200, 200, 200))
        dica_rect = dica_text.get_rect(center=(WIDTH // 2, HEIGHT - 160))
        screen.blit(dica_text, dica_rect)
        
        # Botão continuar com efeito hover
        continuar_color = button_hover if continuar_btn.collidepoint(mouse_pos) else button_color
        draw_button(screen, continuar_btn, "CONTINUAR", font_button, continuar_color, text_color)
        
        # Instrução adicional
        enter_text = pygame.font.SysFont(None, 24).render("ENTER ou ESPAÇO para continuar", True, (150, 150, 150))
        enter_rect = enter_text.get_rect(center=(WIDTH // 2, HEIGHT - 30))
        screen.blit(enter_text, enter_rect)
        
        pygame.display.flip()
        clock.tick(60)

def selecao_personagens():
    """Tela de seleção de personagens"""
    font_title = pygame.font.SysFont(None, 48)
    font_text = pygame.font.SysFont(None, 36)
    font_small = pygame.font.SysFont(None, 24)
    
    # Lista de caminhos das imagens locais dos personagens
    personagens = [
        "players/Bamboo.png",
        "players/Chuck.png",
        "players/Hank.png",
        "players/Jilly.png",
        "players/Moo.png",
        "players/Rocky.png",
    ]
    
    # Carrega as imagens dos personagens
    char_images = []
    for caminho in personagens:
        try:
            img = pygame.image.load(caminho).convert_alpha()
            img = pygame.transform.scale(img, (80, 80))
            char_images.append(img)
        except:
            # Cria uma imagem placeholder se não conseguir carregar
            placeholder = pygame.Surface((80, 80))
            placeholder.fill((100, 100, 100))
            # Adiciona texto indicando qual personagem não foi encontrado
            font = pygame.font.SysFont(None, 24)
            text = font.render(f"Char {len(char_images)+1}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(40, 40))
            placeholder.blit(text, text_rect)
            char_images.append(placeholder)
    
    # Cores
    bg_color = (30, 30, 50)
    button_color = (70, 130, 180)
    button_hover = (100, 160, 210)
    selected_color = (255, 215, 0)
    text_color = (255, 255, 255)
    
    # Estados de seleção
    selected_p1 = 0
    selected_p2 = 1
    selecting_player = 1  # 1 ou 2
    
    # Posições
    char_size = 100
    chars_per_row = 3
    start_x = (WIDTH - (chars_per_row * char_size + (chars_per_row - 1) * 20)) // 2
    start_y = HEIGHT // 2 - 60
    
    # Botão de iniciar
    iniciar_btn = pygame.Rect(WIDTH // 2 - 100, HEIGHT - 100, 200, 50)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    selecting_player = 2 if selecting_player == 1 else 1
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Verifica clique nos personagens
                for i, char_img in enumerate(char_images):
                    row = i // chars_per_row
                    col = i % chars_per_row
                    char_x = start_x + col * (char_size + 20)
                    char_y = start_y + row * (char_size + 20)
                    char_rect = pygame.Rect(char_x, char_y, char_size, char_size)
                    
                    if char_rect.collidepoint(mouse_pos):
                        if selecting_player == 1:
                            selected_p1 = i
                        else:
                            selected_p2 = i
                
                # Verifica clique no botão iniciar
                if iniciar_btn.collidepoint(mouse_pos):
                    return personagens[selected_p1], personagens[selected_p2]
        
        # Desenha fundo
        screen.fill(bg_color)
        
        # Título
        title_text = font_title.render("ESCOLHA OS PERSONAGENS", True, text_color)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 60))
        screen.blit(title_text, title_rect)
        
        # Instruções
        inst_text = font_small.render("TAB para alternar entre jogadores", True, text_color)
        inst_rect = inst_text.get_rect(center=(WIDTH // 2, 90))
        screen.blit(inst_text, inst_rect)
        
        # Indicador do jogador atual
        player_text = font_text.render(f"Selecionando: JOGADOR {selecting_player}", True, selected_color)
        player_rect = player_text.get_rect(center=(WIDTH // 2, 130))
        screen.blit(player_text, player_rect)
        
        # Desenha os personagens
        for i, char_img in enumerate(char_images):
            row = i // chars_per_row
            col = i % chars_per_row
            char_x = start_x + col * (char_size + 20)
            char_y = start_y + row * (char_size + 20)
            char_rect = pygame.Rect(char_x, char_y, char_size, char_size)
            
            # Cor da borda baseada na seleção
            border_color = None
            border_width = 0
            
            if i == selected_p1:
                border_color = (255, 0, 0)  # Vermelho para P1
                border_width = 4
            elif i == selected_p2:
                border_color = (0, 0, 255)  # Azul para P2
                border_width = 4
            elif char_rect.collidepoint(mouse_pos):
                border_color = selected_color
                border_width = 2
            
            # Desenha o fundo do personagem
            pygame.draw.rect(screen, (60, 60, 60), char_rect)
            
            # Desenha a imagem do personagem
            img_rect = char_img.get_rect(center=char_rect.center)
            screen.blit(char_img, img_rect)
            
            # Desenha a borda
            if border_color and border_width:
                pygame.draw.rect(screen, border_color, char_rect, border_width)
        
        # Indicadores dos jogadores selecionados
        p1_text = font_small.render("P1", True, (255, 0, 0))
        p2_text = font_small.render("P2", True, (0, 0, 255))
        
        # P1
        p1_row = selected_p1 // chars_per_row
        p1_col = selected_p1 % chars_per_row
        p1_x = start_x + p1_col * (char_size + 20)
        p1_y = start_y + p1_row * (char_size + 20) - 25
        screen.blit(p1_text, (p1_x, p1_y))
        
        # P2
        p2_row = selected_p2 // chars_per_row
        p2_col = selected_p2 % chars_per_row
        p2_x = start_x + p2_col * (char_size + 20)
        p2_y = start_y + p2_row * (char_size + 20) - 25
        screen.blit(p2_text, (p2_x + 30, p2_y))
        
        # Botão iniciar
        iniciar_color = button_hover if iniciar_btn.collidepoint(mouse_pos) else button_color
        draw_button(screen, iniciar_btn, "INICIAR", font_text, iniciar_color, text_color)
        
        pygame.display.flip()
        clock.tick(60)

# SUBSTITUA AS LINHAS DE CARREGAMENTO DAS IMAGENS DOS JOGADORES POR ESTA FUNÇÃO:
def carregar_imagens_jogadores(caminho1, caminho2):
    """Carrega as imagens dos jogadores baseado nos caminhos locais selecionados"""
    # Jogador 1
    try:
        player_img = pygame.image.load(caminho1).convert_alpha()
        player_img = pygame.transform.scale(player_img, (player.width, player.height))
    except:
        # Fallback se não conseguir carregar
        player_img = pygame.Surface((player.width, player.height))
        player_img.fill((255, 0, 0))
    
    # Jogador 2
    try:
        player2_img = pygame.image.load(caminho2).convert_alpha()
        player2_img = pygame.transform.scale(player2_img, (player2.width, player2.height))
    except:
        # Fallback se não conseguir carregar
        player2_img = pygame.Surface((player2.width, player2.height))
        player2_img.fill((0, 0, 255))
    
    return player_img, player2_img

# Funções
def draw_level():
    """Desenha o nível com paredes 3D realistas"""
    # Primeiro, desenha todas as sombras
    for y, row in enumerate(level):
        for x, cell in enumerate(row):
            if cell in ["W", "B"]:
                rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE + HUD_HEIGHT, TILE_SIZE, TILE_SIZE)
                # Desenha sombra projetada
                shadow_rect = pygame.Rect(x * TILE_SIZE + 2, y * TILE_SIZE + HUD_HEIGHT + TILE_SIZE - 2, TILE_SIZE, 4)
                pygame.draw.rect(screen, SHADOW_COLOR, shadow_rect)
    
    # Depois, desenha o chão e as paredes
    for y, row in enumerate(level):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE + HUD_HEIGHT, TILE_SIZE, TILE_SIZE)
            
            if cell == "W":
                draw_3d_wall(screen, rect, "fixed")
            elif cell == "B":
                draw_3d_wall(screen, rect, "breakable")
            else:
                draw_floor_tile(screen, rect)

def is_bomb(pos):
    x, y = pos
    px = x // TILE_SIZE * TILE_SIZE
    py = (y - HUD_HEIGHT) // TILE_SIZE * TILE_SIZE + HUD_HEIGHT
    for bomb in bombs:
        if bomb["pos"] == (px, py):
            return True
    return False

def is_wall(pos):
    x, y = pos
    col = x // TILE_SIZE
    row = (y - HUD_HEIGHT) // TILE_SIZE  # subtrai a altura da HUD para alinhar com o mapa
    try:
        return level[row][col] in ["W", "B"]  # Tanto paredes fixas quanto quebráveis bloqueiam movimento
    except IndexError:
        return True

def is_breakable_wall(pos):
    x, y = pos
    col = x // TILE_SIZE
    row = (y - HUD_HEIGHT) // TILE_SIZE
    try:
        return level[row][col] == "B"
    except IndexError:
        return False

def break_wall(pos):
    x, y = pos
    col = x // TILE_SIZE
    row = (y - HUD_HEIGHT) // TILE_SIZE
    try:
        if level[row][col] == "B":
            # Modifica o mapa para remover a parede quebrável
            level[row] = level[row][:col] + " " + level[row][col+1:]
            return True
    except IndexError:
        pass
    return False

def mostrar_vencedor(vencedor):
    """Tela de fim de jogo com opções de recomeçar ou voltar ao menu"""
    font_title = pygame.font.SysFont(None, 60)
    font_button = pygame.font.SysFont(None, 40)
    font_instruction = pygame.font.SysFont(None, 32)
    
    # Cores
    bg_color = (30, 30, 50)
    button_color = (70, 130, 180)
    button_hover = (100, 160, 210)
    text_color = (255, 255, 255)
    winner_color = (255, 215, 0)
    
    # Posições dos botões
    button_width, button_height = 250, 60
    button_x = (WIDTH - button_width) // 2
    
    recomecar_btn = pygame.Rect(button_x, HEIGHT // 2 + 20, button_width, button_height)
    menu_btn = pygame.Rect(button_x, HEIGHT // 2 + 100, button_width, button_height)
    
    while True:
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "recomecar"
                elif event.key == pygame.K_m:
                    return "menu"
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if recomecar_btn.collidepoint(mouse_pos):
                    return "recomecar"
                elif menu_btn.collidepoint(mouse_pos):
                    return "menu"
        
        # Desenha fundo
        screen.fill(bg_color)
        
        # Título do vencedor
        winner_text = font_title.render(f"{vencedor} VENCEU!", True, winner_color)
        winner_rect = winner_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 80))
        screen.blit(winner_text, winner_rect)
        
        # Instruções
        inst_text = font_instruction.render("R - Recomeçar | M - Menu", True, text_color)
        inst_rect = inst_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        screen.blit(inst_text, inst_rect)
        
        # Botões com efeito hover
        recomecar_color = button_hover if recomecar_btn.collidepoint(mouse_pos) else button_color
        menu_color = button_hover if menu_btn.collidepoint(mouse_pos) else button_color
        
        draw_button(screen, recomecar_btn, "RECOMEÇAR", font_button, recomecar_color, text_color)
        draw_button(screen, menu_btn, "VOLTAR AO MENU", font_button, menu_color, text_color)
        
        pygame.display.flip()
        clock.tick(60)

# Sistema de menu
opcao_menu = menu_principal()
if opcao_menu == "iniciar":
    tela_instrucoes()
    caminho_p1, caminho_p2 = selecao_personagens()  # Agora retorna caminhos locais
    player_img, player2_img = carregar_imagens_jogadores(caminho_p1, caminho_p2)

# Loop principal
while True:
    screen.fill(WHITE)
    # HUD
    pygame.draw.rect(screen, (200, 200, 200), (0, 0, WIDTH, HUD_HEIGHT))  # fundo cinza

    # Mostrar vidas do player 1
    for i in range(vidas):
        screen.blit(heart_img, (10 + i * 40, 15))

    # Mostrar vidas do player 2
    for i in range(vidas2):
        screen.blit(heart_img, (WIDTH - (i + 1) * 40 - 10, 15))

    draw_level()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            # Jogador 1 coloca bomba com ESPAÇO
            if event.key == pygame.K_e:
                bombas_ativas_p1 = sum(1 for bomb in bombs if bomb["owner"] == "p1")
                if bombas_ativas_p1 < max_bombas_p1:
                    bx = player.x // TILE_SIZE * TILE_SIZE
                    by = (player.y - HUD_HEIGHT) // TILE_SIZE * TILE_SIZE + HUD_HEIGHT
                    bomb_pos = (bx, by)
                    if all(bomb["pos"] != bomb_pos for bomb in bombs):
                        bombs.append({
                            "rect": pygame.Rect(bx, by, TILE_SIZE, TILE_SIZE),
                            "time": time.time(),
                            "pos": bomb_pos,
                            "owner": "p1"
                        })

            # Jogador 2 coloca bomba com tecla ESPAÇO
            if event.key == pygame.K_SPACE:
                bombas_ativas_p2 = sum(1 for bomb in bombs if bomb["owner"] == "p2")
                if bombas_ativas_p2 < max_bombas_p2:
                    bx = player2.x // TILE_SIZE * TILE_SIZE
                    by = (player2.y - HUD_HEIGHT) // TILE_SIZE * TILE_SIZE + HUD_HEIGHT
                    bomb_pos = (bx, by)
                    if all(bomb["pos"] != bomb_pos for bomb in bombs):
                        bombs.append({
                            "rect": pygame.Rect(bx, by, TILE_SIZE, TILE_SIZE),
                            "time": time.time(),
                            "pos": bomb_pos,
                            "owner": "p2"
                        })

     # Movimento do player 1
    keys = pygame.key.get_pressed()
    move_x = move_y = 0
    if keys[pygame.K_a]: move_x = -player_speed
    if keys[pygame.K_d]: move_x = player_speed
    if keys[pygame.K_w]: move_y = -player_speed
    if keys[pygame.K_s]: move_y = player_speed

    new_pos = player.move(move_x, move_y)
    new_center = (new_pos.x + player.width // 2, new_pos.y + player.height // 2)
    if not is_wall(new_center) and not is_bomb(new_center):
        player = new_pos

    # Movimento do player 2 (WASD)
    move2_x = move2_y = 0
    if keys[pygame.K_LEFT]: move2_x = -player_speed
    if keys[pygame.K_RIGHT]: move2_x = player_speed
    if keys[pygame.K_UP]: move2_y = -player_speed
    if keys[pygame.K_DOWN]: move2_y = player_speed

    new_pos2 = player2.move(move2_x, move2_y)
    new_center2 = (new_pos2.x + player2.width // 2, new_pos2.y + player2.height // 2)
    if not is_wall(new_center2) and not is_bomb(new_center2):
        player2 = new_pos2

    for bomb in bombs[:]:
        elapsed = time.time() - bomb["time"]

        if elapsed > 3:
            # Gera explosão
            bx, by = bomb["pos"]
            directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

            # Explosão no centro da bomba
            explosions.append({
                "rect": pygame.Rect(bx, by, TILE_SIZE, TILE_SIZE),
                "time": time.time(),
                "damaged": False
            })

            # Explosão nas 4 direções
            for dx, dy in directions:
                for i in range(1, 2):
                    nx = bx + dx * TILE_SIZE * i
                    ny = by + dy * TILE_SIZE * i

                    # Verifica se há uma parede quebrável nesta posição
                    if is_breakable_wall((nx + TILE_SIZE // 2, ny + TILE_SIZE // 2)):
                        # Quebra a parede e adiciona explosão nela
                        break_wall((nx + TILE_SIZE // 2, ny + TILE_SIZE // 2))
                        if random.random() < 0.2:
                            powerups.append({
                                "rect": pygame.Rect(nx, ny, POWERUP_SIZE, POWERUP_SIZE),
                                "type": "bomb_plus"
                            })

                        explosions.append({
                            "rect": pygame.Rect(nx, ny, TILE_SIZE, TILE_SIZE),
                            "time": time.time(),
                            "damaged": False
                        })
                        break  # Para a propagação da explosão nesta direção

                    # Se é uma parede fixa, para a explosão
                    if is_wall((nx + TILE_SIZE // 2, ny + TILE_SIZE // 2)):
                        break

                    # Adiciona explosão em espaço vazio
                    explosions.append({
                        "rect": pygame.Rect(nx, ny, TILE_SIZE, TILE_SIZE),
                        "time": time.time(),
                        "damaged": False
                    })

            bombs.remove(bomb)
            continue

        # Animação de escala usando seno
        scale_factor = 1 + 0.1 * math.sin(elapsed * 5)
        scaled_size = int(TILE_SIZE * scale_factor)
        scaled_bomb = pygame.transform.scale(bomb_img, (scaled_size, scaled_size))

        bx, by = bomb["rect"].topleft
        offset_x = (TILE_SIZE - scaled_size) // 2
        offset_y = (TILE_SIZE - scaled_size) // 2
        screen.blit(scaled_bomb, (bx + offset_x, by + offset_y))

    for powerup in powerups[:]:
        if player.colliderect(powerup["rect"]):
            if powerup["type"] == "bomb_plus":
                max_bombas_p1 += 1
            powerups.remove(powerup)
        elif player2.colliderect(powerup["rect"]):
            if powerup["type"] == "bomb_plus":
                max_bombas_p2 += 1
            powerups.remove(powerup)

    for powerup in powerups:
        screen.blit(powerup_img, powerup["rect"].topleft)

    for explosion in explosions[:]:
        if time.time() - explosion["time"] > 0.3:
            explosions.remove(explosion)
            continue
        pygame.draw.rect(screen, ORANGE, explosion["rect"])

    for explosion in explosions:
        if not explosion["damaged"]:
            if explosion["rect"].colliderect(player):
                vidas -= 1
                explosion["damaged"] = True
            elif explosion["rect"].colliderect(player2):
                vidas2 -= 1
                explosion["damaged"] = True

    if vidas <= 0:
        resultado = mostrar_vencedor("Jogador 2")
        if resultado == "recomecar":
            # Recomeça o jogo com os mesmos personagens
            vidas = vidas2 = 3
            max_bombas_p1 = max_bombas_p2 = 1
            level = generate_breakable_walls()
            player.x, player.y = 45, 45 + HUD_HEIGHT
            player2_x, player2_y = find_last_valid_position()
            player2.x, player2.y = player2_x, player2_y
            bombs.clear()
            explosions.clear()
            powerups.clear()
            continue
        elif resultado == "menu":
            # Volta ao menu principal
            opcao_menu = menu_principal()
            if opcao_menu == "iniciar":
                tela_instrucoes()
                caminho_p1, caminho_p2 = selecao_personagens()
                player_img, player2_img = carregar_imagens_jogadores(caminho_p1, caminho_p2)
                vidas = vidas2 = 3
                max_bombas_p1 = max_bombas_p2 = 1
                level = generate_breakable_walls()
                player.x, player.y = 45, 45 + HUD_HEIGHT
                player2_x, player2_y = find_last_valid_position()
                player2.x, player2.y = player2_x, player2_y
                bombs.clear()
                explosions.clear()
                powerups.clear()
                continue
            else:
                pygame.quit()
                sys.exit()

    if vidas2 <= 0:
        resultado = mostrar_vencedor("Jogador 2")
        if resultado == "recomecar":
            # Recomeça o jogo com os mesmos personagens
            vidas = vidas2 = 3
            max_bombas_p1 = max_bombas_p2 = 1
            level = generate_breakable_walls()
            player.x, player.y = 45, 45 + HUD_HEIGHT
            player2_x, player2_y = find_last_valid_position()
            player2.x, player2.y = player2_x, player2_y
            bombs.clear()
            explosions.clear()
            powerups.clear()
            continue
        elif resultado == "menu":
            # Volta ao menu principal
            opcao_menu = menu_principal()
            if opcao_menu == "iniciar":
                caminho_p1, caminho_p2 = selecao_personagens()
                player_img, player2_img = carregar_imagens_jogadores(caminho_p1, caminho_p2)
                vidas = vidas2 = 3
                max_bombas_p1 = max_bombas_p2 = 1
                level = generate_breakable_walls()
                player.x, player.y = 45, 45 + HUD_HEIGHT
                player2_x, player2_y = find_last_valid_position()
                player2.x, player2.y = player2_x, player2_y
                bombs.clear()
                explosions.clear()
                powerups.clear()
                continue
            else:
                pygame.quit()
                sys.exit()

    # Bombas disponíveis
    fonte = pygame.font.SysFont(None, 24)
    bombas_ativas_p1 = sum(1 for bomb in bombs if bomb["owner"] == "p1")
    bombas_ativas_p2 = sum(1 for bomb in bombs if bomb["owner"] == "p2")

    texto_bombas1 = fonte.render(f"Bombas: {max_bombas_p1 - bombas_ativas_p1}", True, (0, 0, 0))
    texto_bombas2 = fonte.render(f"Bombas: {max_bombas_p2 - bombas_ativas_p2}", True, (0, 0, 0))

    screen.blit(texto_bombas1, (10, 45))
    screen.blit(texto_bombas2, (WIDTH - texto_bombas2.get_width() - 10, 45))

    screen.blit(player_img, player.topleft)
    screen.blit(player2_img, player2.topleft)
    pygame.display.flip()
    clock.tick(10)