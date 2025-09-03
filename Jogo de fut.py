import pygame
import math
import sys
import random

# =============================
# Futebol com a Mão - Funcional
# =============================

WIDTH, HEIGHT = 1000, 650
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Futebol com a Mão - Funcional")
clock = pygame.time.Clock()

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (60, 200, 120)
RED = (220, 70, 70)

FONT = pygame.font.SysFont("arial", 28, bold=True)
level = 1

# =============================
# Joystick
# =============================
pygame.joystick.init()
joystick = pygame.joystick.Joystick(0) if pygame.joystick.get_count() > 0 else None
if joystick:
    joystick.init()

# =============================
# Funções úteis
# =============================
def clamp(value, minv, maxv):
    return max(minv, min(value, maxv))

def vec_len(x, y):
    return math.sqrt(x * x + y * y)

# =============================
# Classes do jogo
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
# Classe do Jogo
# =============================
class SoccerGame:
    def __init__(self, level, mode='1x1'):
        self.level = level
        self.mode = mode
        self.reset()
        self.paused = False

    def reset(self):
        self.ball = Ball()
        if self.mode == '1x1':
            self.players_team = [Player(200, HEIGHT//2, GREEN)]
            self.players_enemy = [Player(WIDTH-200, HEIGHT//2, RED)]
        else:  # 2x2
            self.players_team = [Player(200, HEIGHT//2 - 80, GREEN), Player(200, HEIGHT//2 + 80, GREEN)]
            self.players_enemy = [Player(WIDTH-200, HEIGHT//2 - 80, RED), Player(WIDTH-200, HEIGHT//2 + 80, RED)]
        self.selected_index = 0
        self.score_team = 0
        self.score_enemy = 0
        self.max_score = 5
        self.game_over = False

    # Botões
    def button_chute_normal(self): self.ball.vx = 10; self.ball.vy = 0
    def button_passe(self):
        mates = [p for i,p in enumerate(self.players_team) if i != self.selected_index]
        if mates: self.ball.pass_to_player(mates[0])
    def button_chute_gol(self): self.ball.kick_to_goal(left_side=False)
    def switch_player(self): self.selected_index = (self.selected_index + 1) % len(self.players_team)
    def toggle_pause(self): self.paused = not self.paused

    def handle_input(self):
        if self.paused or self.game_over: return
        dx = dy = 0
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1

        if joystick:
            axis_x = joystick.get_axis(0)
            axis_y = joystick.get_axis(1)
            deadzone = 0.2
            if abs(axis_x) > deadzone: dx += axis_x
            if abs(axis_y) > deadzone: dy += axis_y

            if joystick.get_button(0): self.button_chute_normal()
            if joystick.get_button(1): self.button_passe()
            if joystick.get_button(2): self.button_chute_gol()
            if joystick.get_button(3): self.switch_player()
            if joystick.get_button(7): self.toggle_pause()

        self.players_team[self.selected_index].move(dx, dy)

    def update(self):
        if self.paused or self.game_over: return

        # IA inimiga
        for e in self.players_enemy:
            dx = self.ball.x - e.x
            dy = self.ball.y - e.y
            l = vec_len(dx, dy)
            if l > 0:
                dx /= l
                dy /= l
            speed_multiplier = 1 + self.level / 50
            e.move(dx * speed_multiplier, dy * speed_multiplier)

        for p in self.players_team: self.ball.collide_player(p,'team')
        for p in self.players_enemy: self.ball.collide_player(p,'enemy')
        self.ball.update()

        # Verifica gols
        scored = False
        if self.ball.x < self.ball.r:
            if HEIGHT/2 - 90 < self.ball.y < HEIGHT/2 + 90: self.score_enemy += 1; scored=True
            self.ball.reset()
        elif self.ball.x > WIDTH - self.ball.r:
            if HEIGHT/2 - 90 < self.ball.y < HEIGHT/2 + 90: self.score_team += 1; scored=True
            self.ball.reset()
        if self.score_team>=self.max_score or self.score_enemy>=self.max_score: self.game_over=True

    def draw_field(self,surf):
        surf.fill((7,100,40))
        pygame.draw.rect(surf,WHITE,(30,30,WIDTH-60,HEIGHT-60),2)
        pygame.draw.line(surf,WHITE,(WIDTH//2,30),(WIDTH//2,HEIGHT-30),2)
        pygame.draw.circle(surf,WHITE,(WIDTH//2,HEIGHT//2),80,2)
        pygame.draw.circle(surf,WHITE,(WIDTH//2,HEIGHT//2),6)
        pygame.draw.rect(surf,WHITE,(0,HEIGHT//2-90,18,180))
        pygame.draw.rect(surf,WHITE,(WIDTH-18,HEIGHT//2-90,18,180))

    def draw(self,surf):
        self.draw_field(surf)
        for i,p in enumerate(self.players_team): p.draw(surf, selected=(i==self.selected_index))
        for p in self.players_enemy: p.draw(surf)
        self.ball.draw(surf)
        score_text = f"Você {self.score_team} - {self.score_enemy} Inimigo | Nível {self.level}"
        surf.blit(FONT.render(score_text,True,WHITE),(WIDTH//2-180,20))
        if self.paused: surf.blit(FONT.render("PAUSADO",True,WHITE),(WIDTH//2-60,HEIGHT//2))
        if self.game_over:
            msg = "VOCÊ VENCEU!" if self.score_team>self.score_enemy else "VOCÊ PERDEU"
            surf.blit(FONT.render(msg,True,RED if self.score_enemy>self.score_team else GREEN),(WIDTH//2-100,HEIGHT//2))

# =============================
# Loop principal
# =============================
game = SoccerGame(level, mode='1x1') # Pode trocar para '2x2'
running = True

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running=False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB: game.switch_player()
            if event.key == pygame.K_r: game.reset()

    game.handle_input()
    game.update()
    game.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()
  