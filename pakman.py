import pygame
import random
import sys

# Inicialização do Pygame
pygame.init()

# Configurações da tela
WIDTH, HEIGHT = 800, 400
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Jogo do Dinossauro")

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Dinossauro
dino_width, dino_height = 50, 50
dino_x, dino_y = 50, HEIGHT - dino_height - 50
dino_vel_y = 0
gravity = 1
is_jumping = False

# Obstáculos
obstacle_width, obstacle_height = 20, 50
obstacles = []
obstacle_vel = 7
spawn_timer = 0

# Estado do jogo
clock = pygame.time.Clock()
FPS = 60
paused = False
score = 0
font = pygame.font.SysFont("comicsans", 30)

# Inicializar joystick
joysticks = []
for i in range(pygame.joystick.get_count()):
    joystick = pygame.joystick.Joystick(i)
    joystick.init()
    joysticks.append(joystick)

def draw_window():
    WIN.fill(WHITE)
    pygame.draw.rect(WIN, BLACK, (dino_x, dino_y, dino_width, dino_height))
    for obs in obstacles:
        pygame.draw.rect(WIN, BLACK, obs)
    score_text = font.render(f"Score: {score}", True, BLACK)
    WIN.blit(score_text, (WIDTH - 150, 10))
    if paused:
        pause_text = font.render("PAUSADO", True, BLACK)
        WIN.blit(pause_text, (WIDTH//2 - 50, HEIGHT//2 - 20))
    pygame.display.update()

def main():
    global dino_y, dino_vel_y, is_jumping, paused, score, spawn_timer

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                sys.exit()

            # Teclado
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not is_jumping and not paused:
                    dino_vel_y = -15
                    is_jumping = True
                if event.key == pygame.K_r or event.key == pygame.K_3:
                    paused = not paused

            # Joystick
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 2:  # botão 3 no joystick (índice começa em 0)
                    paused = not paused
                if event.button == 0 and not is_jumping and not paused:  # botão A como pulo
                    dino_vel_y = -15
                    is_jumping = True

        if not paused:
            # Movimento do dinossauro
            dino_y += dino_vel_y
            dino_vel_y += gravity
            if dino_y >= HEIGHT - dino_height - 50:
                dino_y = HEIGHT - dino_height - 50
                is_jumping = False
                dino_vel_y = 0

            # Obstáculos
            spawn_timer += 1
            if spawn_timer > 90:
                obstacle_x = WIDTH
                obstacle_y = HEIGHT - obstacle_height - 50
                obstacles.append(pygame.Rect(obstacle_x, obstacle_y, obstacle_width, obstacle_height))
                spawn_timer = 0

            for obs in obstacles[:]:
                obs.x -= obstacle_vel
                if obs.x + obstacle_width < 0:
                    obstacles.remove(obs)
                    score += 1

            # Colisão
            dino_rect = pygame.Rect(dino_x, dino_y, dino_width, dino_height)
            for obs in obstacles:
                if dino_rect.colliderect(obs):
                    print("Fim de jogo! Score:", score)
                    run = False

        draw_window()

if __name__ == "__main__":
    main()
