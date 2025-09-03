import pygame
import random

# Inicialização
pygame.init()

# Tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo de Tiro Arcade Com Pausa e Botão 4")

# Clock
clock = pygame.time.Clock()
FPS = 60

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)

# Player
player_width, player_height = 50, 30
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 10
player_speed = 5
player_lives = 3

# Bullets
bullet_speed = 7
bullets = []

# Enemies
enemy_width, enemy_height = 50, 30
enemy_speed = 2
enemies = []

# Explosões
explosions = []

# Pontuação
score = 0
font = pygame.font.SysFont(None, 36)

# Detectar joystick
joystick_count = pygame.joystick.get_count()
if joystick_count > 0:
    joystick = pygame.joystick.Joystick(0)
    joystick.init()
    print(f"Joystick conectado: {joystick.get_name()}")
else:
    joystick = None
    print("Nenhum joystick detectado, usando teclado.")

# Função para desenhar texto
def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

# Função para criar bala
def shoot():
    bullets.append(pygame.Rect(player_x + player_width//2 - 5, player_y, 10, 20))

# Variável de pausa
paused = False

# Loop principal
running = True
while running:
    clock.tick(FPS)
    screen.fill(BLACK)

    # Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Pausar/Despausar teclado
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused
            elif event.key in [pygame.K_SPACE, pygame.K_RETURN] and not paused:
                shoot()

        # Pausar/Despausar joystick
        if joystick and event.type == pygame.JOYBUTTONDOWN:
            # Botão Y = 3, Botão 4 = 4
            if event.button in [3, 4]:
                paused = not paused
            elif event.button in [0, 1] and not paused:  # X = 0, O = 1
                shoot()

    if not paused:
        # Movimentação
        move_x = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            move_x = -player_speed
        if keys[pygame.K_RIGHT]:
            move_x = player_speed

        if joystick:
            axis_x = joystick.get_axis(0)
            if abs(axis_x) > 0.1:
                move_x = axis_x * player_speed

        player_x += move_x
        player_x = max(0, min(WIDTH - player_width, player_x))

        # Criar inimigos
        if random.randint(1, 50) == 1:
            enemy_x = random.randint(0, WIDTH - enemy_width)
            enemies.append(pygame.Rect(enemy_x, -enemy_height, enemy_width, enemy_height))

        # Atualizar inimigos
        for enemy in enemies[:]:
            enemy.y += enemy_speed
            if enemy.y > HEIGHT:
                enemies.remove(enemy)
                player_lives -= 1

        # Atualizar balas
        for bullet in bullets[:]:
            bullet.y -= bullet_speed
            if bullet.y < 0:
                bullets.remove(bullet)

        # Checar colisões
        for enemy in enemies[:]:
            for bullet in bullets[:]:
                if enemy.colliderect(bullet):
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    explosions.append([enemy.centerx, enemy.centery, 0])
                    score += 1

            player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
            if enemy.colliderect(player_rect):
                enemies.remove(enemy)
                explosions.append([enemy.centerx, enemy.centery, 0])
                player_lives -= 1

        # Atualizar explosões
        for exp in explosions[:]:
            x, y, frame = exp
            radius = 10 + frame*3
            pygame.draw.circle(screen, ORANGE, (x, y), radius)
            exp[2] += 1
            if exp[2] > 5:
                explosions.remove(exp)

        # Desenhar jogador
        pygame.draw.rect(screen, GREEN, (player_x, player_y, player_width, player_height))
        # Desenhar inimigos
        for enemy in enemies:
            pygame.draw.rect(screen, RED, enemy)
        # Desenhar balas
        for bullet in bullets:
            pygame.draw.rect(screen, WHITE, bullet)

        # Mostrar score e vidas
        draw_text(f"Score: {score}", font, WHITE, 10, 10)
        draw_text(f"Lives: {player_lives}", font, YELLOW, WIDTH - 120, 10)

        # Game Over
        if player_lives <= 0:
            draw_text("GAME OVER", font, RED, WIDTH//2 - 80, HEIGHT//2)
            pygame.display.flip()
            pygame.time.delay(3000)
            running = False
    else:
        # Mostrar mensagem de pausa
        draw_text("PAUSED", font, YELLOW, WIDTH//2 - 50, HEIGHT//2)

    pygame.display.flip()

pygame.quit()
