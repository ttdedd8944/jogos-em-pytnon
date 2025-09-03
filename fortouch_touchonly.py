import pygame
import math
import sys
import random

# =============================
# Futebol com a Mão - Versão Mobile (controles na tela)
# =============================

WIDTH, HEIGHT = 1000, 650
FPS = 60

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Futebol com a Mão - Mobile Controls")
clock = pygame.time.Clock()

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (60, 200, 120)
RED = (220, 70, 70)
TRANSLUCENT = (255, 255, 255, 90)

FONT = pygame.font.SysFont("arial", 28, bold=True)
level = 1


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

        # Controles para tela (touch)
        # Joystick virtual no canto inferior esquerdo
        self.joy_center = (120, HEIGHT - 120)
        self.joy_radius = 70
        self.joy_knob_pos = self.joy_center
        self.joy_active = False

        # Botões no canto inferior direito (x,y,raio,label,callback)
        self.buttons = []
        btn_x = WIDTH - 120
        btn_y_base = HEIGHT - 140
        spacing = 90
        self.buttons.append({'pos': (btn_x, btn_y_base), 'r': 40, 'label': 'PASSE', 'fn': self.button_passe})
        self.buttons.append({'pos': (btn_x, btn_y_base + spacing), 'r': 40, 'label': 'CHUTE', 'fn': self.button_chute_normal})
        self.buttons.append({'pos': (btn_x, btn_y_base + spacing*2), 'r': 40, 'label': 'GOL', 'fn': self.button_chute_gol})
        # botões menores para trocar e pausar
        self.buttons.append({'pos': (btn_x - 110, btn_y_base + spacing), 'r': 32, 'label': 'TROCA', 'fn': self.switch_player})
        self.buttons.append({'pos': (btn_x - 110, btn_y_base + spacing*2), 'r': 32, 'label': 'PAUSA', 'fn': self.toggle_pause})

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

    # Ações (reaproveitadas)
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
        # Apenas movimento do joystick virtual (touch)
        if self.joy_active:
            jx, jy = self.joy_knob_pos
            cx, cy = self.joy_center
            mdx = jx - cx
            mdy = jy - cy
            if vec_len(mdx, mdy) > 0:
                dx += mdx / self.joy_radius
                dy += mdy / self.joy_radius

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

        # Desenhar joystick virtual (base e knob)
        # base
        pygame.draw.circle(surf, (200,200,200,60), self.joy_center, self.joy_radius, 2)
        # knob
        pygame.draw.circle(surf, (220,220,220), (int(self.joy_knob_pos[0]), int(self.joy_knob_pos[1])), 28)
        pygame.draw.circle(surf, BLACK, (int(self.joy_knob_pos[0]), int(self.joy_knob_pos[1])), 28, 2)

        # Desenhar botões
        for b in self.buttons:
            x,y = b['pos']
            r = b['r']
            pygame.draw.circle(surf, (220,220,220), (int(x),int(y)), r)
            pygame.draw.circle(surf, BLACK, (int(x),int(y)), r, 2)
            # label
            lbl = FONT.render(b['label'], True, BLACK)
            lbl_rect = lbl.get_rect(center=(x, y))
            surf.blit(lbl, lbl_rect)

# =============================
# Loop principal
# =============================
game = SoccerGame(level, mode='1x1') # Pode trocar para '2x2'
running = True

# Estados para touch/mouse
mouse_down = False
mouse_id_active = None

while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False

        # Teclado
        # Touch/Mouse handling (funciona tanto para toque quanto para mouse)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            mouse_down = True

            # Verifica se começou dentro do joystick
            cx, cy = game.joy_center
            if vec_len(mx - cx, my - cy) <= game.joy_radius:
                game.joy_active = True
                # limitar knob ao raio
                dx = mx - cx
                dy = my - cy
                dist = vec_len(dx, dy)
                if dist > game.joy_radius:
                    dx = dx / dist * game.joy_radius
                    dy = dy / dist * game.joy_radius
                game.joy_knob_pos = (cx + dx, cy + dy)
            else:
                # verifica botões
                for b in game.buttons:
                    bx, by = b['pos']
                    if vec_len(mx - bx, my - by) <= b['r']:
                        # chama a função do botão
                        try:
                            b['fn']()
                        except Exception as e:
                            print("Erro botão:", e)

        elif event.type == pygame.MOUSEMOTION:
            if mouse_down and game.joy_active:
                mx, my = event.pos
                cx, cy = game.joy_center
                dx = mx - cx
                dy = my - cy
                dist = vec_len(dx, dy)
                if dist > game.joy_radius:
                    dx = dx / dist * game.joy_radius
                    dy = dy / dist * game.joy_radius
                game.joy_knob_pos = (cx + dx, cy + dy)

        elif event.type == pygame.MOUSEBUTTONUP:
            mouse_down = False
            # soltar joystick: reset knob ao centro
            if game.joy_active:
                game.joy_active = False
                game.joy_knob_pos = game.joy_center

        # (Opcional) tratar multi-touch ou eventos específicos de touch se necessário
        # algumas plataformas mapeiam toques para MOUSE* automaticamente

    game.handle_input()
    game.update()
    game.draw(screen)
    pygame.display.flip()

pygame.quit()
sys.exit()

