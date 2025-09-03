import pygame
import random
import math
import sys

# =============================
# Futebol com a Mão - Completo com Níveis 1-100 e Contagem de Gols Correta
# =============================

WIDTH, HEIGHT = 1000, 650
FPS = 30

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Futebol com a Mão - Níveis 1-100")
clock = pygame.time.Clock()

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (60, 200, 120)
RED = (220, 70, 70)
GREY = (30, 30, 30)

FONT = pygame.font.SysFont("arial", 28, bold=True)

# Nível de dificuldade
level = 1  # Pode ser de 1 a 100

# =============================
# Utilidades
# =============================

def clamp(value, minv, maxv):
    return max(minv, min(value, maxv))

def vec_len(x, y):
    return math.sqrt(x * x + y * y)

# =============================
# Objetos do Jogo
# =============================

class Player:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.r = 22
        self.color = color
        self.speed = 5.2

    def move(self, dx, dy):
        l = vec_len(dx, dy)
        if l > 0:
            dx /= l
            dy /= l
        self.x = clamp(self.x + dx * self.speed, self.r, WIDTH - self.r)
        self.y = clamp(self.y + dy * self.speed, self.r, HEIGHT - self.r)

    def draw(self, surf, selected=False):
        pygame.draw.circle(surf, self.color, (int(self.x), int(self.y)), self.r)
        if selected:
            pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), self.r + 3, 2)

class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = WIDTH/2
        self.y = HEIGHT/2
        self.r = 12
        self.vx = 0
        self.vy = 0
        self.max_speed = 10
        self.last_touch = None

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.99
        self.vy *= 0.99
        if self.y < self.r:
            self.y = self.r
            self.vy *= -1
        if self.y > HEIGHT - self.r:
            self.y = HEIGHT - self.r
            self.vy *= -1
        sp = vec_len(self.vx, self.vy)
        if sp > self.max_speed:
            self.vx = self.vx / sp * self.max_speed
            self.vy = self.vy / sp * self.max_speed

    def collide_player(self, p: Player, team_name):
        dx = self.x - p.x
        dy = self.y - p.y
        dist = vec_len(dx, dy)
        if dist < self.r + p.r:
            if dist == 0:
                dist = 0.1
            nx, ny = dx/dist, dy/dist
            self.x = p.x + nx * (self.r + p.r)
            self.y = p.y + ny * (self.r + p.r)
            self.vx += nx * 4
            self.vy += ny * 4
            self.last_touch = team_name

    def kick_to_goal(self, left_side=True):
        gx = 40 if left_side else WIDTH - 40
        gy = HEIGHT/2
        dx = gx - self.x
        dy = gy - self.y
        l = vec_len(dx, dy)
        if l == 0:
            l = 1
        self.vx = dx / l * 9
        self.vy = dy / l * 9

    def pass_to_player(self, target: Player):
        dx = target.x - self.x
        dy = target.y - self.y
        l = vec_len(dx, dy)
        if l == 0:
            l = 1
        self.vx = dx / l * 7
        self.vy = dy / l * 7

    def draw(self, surf):
        pygame.draw.circle(surf, WHITE, (int(self.x), int(self.y)), self.r)
        pygame.draw.circle(surf, BLACK, (int(self.x), int(self.y)), self.r, 2)

# =============================
# Jogo
# =============================

class SoccerGame:
    def __init__(self, level):
        self.level = level
        self.reset()

    def reset(self):
        self.ball = Ball()
        self.players_team = [Player(200, HEIGHT//2 - 80, GREEN), Player(200, HEIGHT//2 + 80, GREEN)]
        self.players_enemy = [Player(WIDTH-200, HEIGHT//2 - 80, RED), Player(WIDTH-200, HEIGHT//2 + 80, RED)]
        self.selected_index = 0
        self.score_team = 0
        self.score_enemy = 0
        self.max_score = 5
        self.game_over = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
        self.players_team[self.selected_index].move(dx, dy)

    def update(self):
        if self.game_over:
            return
        self.handle_input()
        # Bots inimigos com velocidade conforme nível
        for e in self.players_enemy:
            dx = self.ball.x - e.x
            dy = self.ball.y - e.y
            l = vec_len(dx, dy)
            if l > 0:
                dx /= l
                dy /= l
            speed_multiplier = 1 + self.level / 50
            e.move(dx * speed_multiplier, dy * speed_multiplier)
        # Colisões
        for p in self.players_team:
            self.ball.collide_player(p, 'team')
        for p in self.players_enemy:
            self.ball.collide_player(p, 'enemy')
        self.ball.update()

        # Verificar gol e lateral corretamente
        scored = False
        if self.ball.x < self.ball.r:
            if HEIGHT/2 - 90 < self.ball.y < HEIGHT/2 + 90:
                self.score_enemy += 1
                scored = True
            else:
                self.ball.reset()
        elif self.ball.x > WIDTH - self.ball.r:
            if HEIGHT/2 - 90 < self.ball.y < HEIGHT/2 + 90:
                self.score_team += 1
                scored = True
            else:
                self.ball.reset()
        if scored:
            self.ball.reset()

        if self.score_team >= self.max_score or self.score_enemy >= self.max_score:
            self.game_over = True

    def draw_field(self, surf):
        surf.fill((7, 100, 40))
        pygame.draw.rect(surf, WHITE, (30, 30, WIDTH-60, HEIGHT-60), 2)
        pygame.draw.line(surf, WHITE, (WIDTH//2, 30), (WIDTH//2, HEIGHT-30), 2)
        pygame.draw.circle(surf, WHITE, (WIDTH//2, HEIGHT//2), 80, 2)
        pygame.draw.circle(surf, WHITE, (WIDTH//2, HEIGHT//2), 6)
        pygame.draw.rect(surf, WHITE, (0, HEIGHT//2 - 90, 18, 180))
        pygame.draw.rect(surf, WHITE, (WIDTH-18, HEIGHT//2 - 90, 18, 180))
        pygame.draw.circle(surf, WHITE, (30, 30), 8, 2)
        pygame.draw.circle(surf, WHITE, (WIDTH-30, 30), 8, 2)
        pygame.draw.circle(surf, WHITE, (30, HEIGHT-30), 8, 2)
        pygame.draw.circle(surf, WHITE, (WIDTH-30, HEIGHT-30), 8, 2)

    def draw(self, surf):
        self.draw_field(surf)
        for i, p in enumerate(self.players_team):
            p.draw(surf, selected=(i == self.selected_index))
        for p in self.players_enemy:
            p.draw(surf)
        self.ball.draw(surf)
        score_text = f"Você {self.score_team} - {self.score_enemy} Inimigo | Nível {self.level}"
        surf.blit(FONT.render(score_text, True, WHITE), (WIDTH//2 - 180, 20))
        if self.game_over:
            msg = "VOCÊ VENCEU!" if self.score_team > self.score_enemy else "VOCÊ PERDEU"
            surf.blit(FONT.render(msg, True, RED if self.score_enemy > self.score_team else GREEN), (WIDTH//2 - 100, HEIGHT//2))

# =============================
# Loop Principal
# =============================

game = SoccerGame(level)
running = True

while running:
    dt = clock.tick(FPS)/1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                game.selected_index = (game.selected_index + 1) % len(game.players_team)
            if event.key == pygame.K_r:
                game.reset()
            if event.key == pygame.K_SPACE:
                dx = game.ball.x - game.players_team[game.selected_index].x
                dy = game.ball.y - game.players_team[game.selected_index].y
                l = vec_len(dx, dy)
                if l < 60:
                    game.ball.vx = dx/l * 12
                    game.ball.vy = dy/l * 12
            if event.key == pygame.K_LSHIFT:
                mates = [p for i, p in enumerate(game.players_team) if i != game.selected_index]
                if mates:
                    game.ball.pass_to_player(mates[0])
            if event.key == pygame.K_LCTRL:
                game.ball.kick_to_goal(left_side=False)

    game.update()
    game.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
