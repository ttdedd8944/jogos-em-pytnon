# Aura 8.0 – Mobile Pygame (sem Kivy)
# Feito para rodar no Pydroid 3 (Android)
# Autor: ChatGPT

import pygame, random, sys

# Inicialização
pygame.init()
LARGURA, ALTURA = 800, 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Aura 8.0 – Mobile")
FPS = 60
clock = pygame.time.Clock()

# Cores
PRETO   = (0, 0, 0)
AZUL    = (50, 150, 255)
BRANCO  = (255, 255, 255)
VERMELHO= (255, 50, 50)
LARANJA = (255, 150, 50)
AMARELO = (255, 255, 0)
CINZA   = (80, 80, 80)

# Jogador
player_w, player_h = 64, 36
player_x = LARGURA//2 - player_w//2
player_y = ALTURA - player_h - 80
player_speed = 7

# Balas
bullets = []
bullet_speed = 10

# Inimigos
enemies = []
enemy_speed = 3
enemy_spawn_chance = 0.02

# Explosões
explosions = []

# HUD
score = 0
lives = 3
font = pygame.font.SysFont("Arial", 28)

# Botões touch (retângulos)
btn_left  = pygame.Rect(30, ALTURA-100, 100, 80)
btn_right = pygame.Rect(150, ALTURA-100, 100, 80)
btn_fire  = pygame.Rect(LARGURA-130, ALTURA-100, 100, 80)

# Estados dos botões
move_left = False
move_right = False
shooting = False

# Funções
def desenhar_jogador():
    pygame.draw.rect(TELA, AZUL, (player_x, player_y, player_w, player_h))

def desenhar_balas():
    for bx, by in bullets:
        pygame.draw.rect(TELA, BRANCO, (bx, by, 6, 16))

def desenhar_inimigos():
    for ex, ey in enemies:
        pygame.draw.rect(TELA, VERMELHO, (ex, ey, 40, 24))

def desenhar_explosoes():
    for ex, ey, t in explosions:
        r = 10 + t*3
        pygame.draw.circle(TELA, LARANJA, (ex, ey), r, 2)

def desenhar_hud():
    hud = font.render(f"Score: {score}   Lives: {lives}", True, BRANCO)
    TELA.blit(hud, (20, 20))

def desenhar_botoes():
    pygame.draw.rect(TELA, CINZA, btn_left) 
    pygame.draw.rect(TELA, CINZA, btn_right)
    pygame.draw.rect(TELA, CINZA, btn_fire)
    TELA.blit(font.render("◀", True, BRANCO), (btn_left.x+35, btn_left.y+20))
    TELA.blit(font.render("▶", True, BRANCO), (btn_right.x+35, btn_right.y+20))
    TELA.blit(font.render("FIRE", True, AMARELO), (btn_fire.x+15, btn_fire.y+20))

# Loop principal
rodando = True
while rodando:
    clock.tick(FPS)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            rodando = False

        elif e.type == pygame.MOUSEBUTTONDOWN:
            mx, my = e.pos
            if btn_left.collidepoint(mx, my):
                move_left = True
            if btn_right.collidepoint(mx, my):
                move_right = True
            if btn_fire.collidepoint(mx, my):
                shooting = True

        elif e.type == pygame.MOUSEBUTTONUP:
            mx, my = e.pos
            move_left = move_right = shooting = False

    # Movimento
    if move_left and player_x > 0:
        player_x -= player_speed
    if move_right and player_x < LARGURA - player_w:
        player_x += player_speed
    if shooting:
        if len(bullets) == 0 or pygame.time.get_ticks() % 8 == 0:
            bullets.append([player_x + player_w//2 - 3, player_y])

    # Atualiza balas
    for b in bullets[:]:
        b[1] -= bullet_speed
        if b[1] < -20:
            bullets.remove(b)

    # Spawna inimigos
    if random.random() < enemy_spawn_chance:
        ex = random.randint(0, LARGURA-40)
        enemies.append([ex, -24])

    # Atualiza inimigos
    for en in enemies[:]:
        en[1] += enemy_speed
        if en[1] > ALTURA:
            enemies.remove(en)
            lives -= 1

    # Colisões
    for en in enemies[:]:
        ex, ey = en
        rect_enemy = pygame.Rect(ex, ey, 40, 24)
        hit = False
        for b in bullets[:]:
            rect_bullet = pygame.Rect(b[0], b[1], 6, 16)
            if rect_enemy.colliderect(rect_bullet):
                bullets.remove(b)
                enemies.remove(en)
                explosions.append([ex+20, ey+12, 0])
                score += 1
                hit = True
                break
        if not hit:
            rect_player = pygame.Rect(player_x, player_y, player_w, player_h)
            if rect_enemy.colliderect(rect_player):
                enemies.remove(en)
                explosions.append([ex+20, ey+12, 0])
                lives -= 1

    # Atualiza explosões
    for ex in explosions[:]:
        ex[2] += 1
        if ex[2] > 15:
            explosions.remove(ex)

    # Desenho
    TELA.fill(PRETO)
    desenhar_jogador()
    desenhar_balas()
    desenhar_inimigos()
    desenhar_explosoes()
    desenhar_hud()
    desenhar_botoes()

    if lives <= 0:
        gameover = font.render("GAME OVER", True, AMARELO)
        TELA.blit(gameover, (LARGURA//2-100, ALTURA//2))
        pygame.display.flip()
        pygame.time.wait(3000)
        rodando = False

    pygame.display.flip()

pygame.quit()
sys.exit()

