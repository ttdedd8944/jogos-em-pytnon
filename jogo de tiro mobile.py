# Aura 8.0 – Versão Mobile/Tablet otimizada para Pydroid 3
# Autor: adaptado por ChatGPT
# Requisitos: kivy>=2.3.0 (instalar no Pydroid via PIP)

from kivy.config import Config
Config.set('graphics', 'fullscreen', 'auto')
Config.set('graphics', 'orientation', 'landscape')

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ListProperty, BooleanProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, Ellipse
from random import randint

KV = r"""
#:import dp kivy.metrics.dp

<GameRoot@FloatLayout>:
    Label:
        id: score_lbl
        text: f"Score: {root.score}"
        pos_hint: {"x":0.02, "top":1}
        size_hint: None, None
        size: self.texture_size
        bold: True
    Label:
        id: lives_lbl
        text: f"Lives: {root.lives}"
        pos_hint: {"right":0.98, "top":1}
        size_hint: None, None
        size: self.texture_size
        bold: True
    Label:
        id: paused_lbl
        text: "PAUSED" if root.paused else ""
        font_size: "24sp"
        pos_hint: {"center_x":0.5, "center_y":0.5}
        size_hint: None, None
        size: self.texture_size
        color: 1,1,0,1

    GameCanvas:
        id: game
        pos_hint: {"x":0, "y":0.15}
        size_hint: 1, 0.7
        on_touch_down: root.on_area_touch(*args)
        on_touch_move: root.on_area_touch(*args)

    Button:
        text: "◀"
        pos_hint: {"x":0.02, "y":0.02}
        size_hint: 0.18, 0.11
        on_press: root.move_dir = -1
        on_release: root.move_dir = 0
    Button:
        text: "▶"
        pos_hint: {"x":0.22, "y":0.02}
        size_hint: 0.18, 0.11
        on_press: root.move_dir = 1
        on_release: root.move_dir = 0
    Button:
        text: "FIRE"
        pos_hint: {"right":0.98, "y":0.02}
        size_hint: 0.22, 0.11
        on_press: root.request_shoot()
    Button:
        text: "⏯"
        pos_hint: {"right":0.98, "top":0.98}
        size_hint: 0.12, 0.10
        on_release: root.toggle_pause()

<GameCanvas@Widget>:
"""

class Bullet:
    def __init__(self, x, y, w, h, speed):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.speed = speed
    def update(self, dt):
        self.y += self.speed * dt
    def rect(self):
        return (self.x, self.y, self.w, self.h)

class Enemy:
    def __init__(self, x, y, w, h, speed):
        self.x, self.y = x, y
        self.w, self.h = w, h
        self.speed = speed
    def update(self, dt):
        self.y -= self.speed * dt
    def rect(self):
        return (self.x, self.y, self.w, self.h)

class Explosion:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.t = 0.0
        self.duration = 0.25
    def update(self, dt):
        self.t += dt
    @property
    def alive(self):
        return self.t < self.duration

class GameRoot(Widget):
    score = NumericProperty(0)
    lives = NumericProperty(3)
    paused = BooleanProperty(False)

    player_size = ListProperty([64, 36])
    player_pos = ListProperty([0, 0])
    player_speed = NumericProperty(420)
    move_dir = NumericProperty(0)

    bullets: list
    enemies: list
    explosions: list

    bullet_speed = NumericProperty(900)
    enemy_speed = NumericProperty(140)
    enemy_spawn_chance = NumericProperty(0.018)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bullets = []
        self.enemies = []
        self.explosions = []
        Clock.schedule_once(self._post_build, 0)
        self._shoot_cooldown = 0.0
        self.bind(size=self._on_resize)

    def _post_build(self, *_):
        game = self.ids.game
        px = game.x + game.width / 2
        py = game.y + self.player_size[1] / 2 + 8
        self.player_pos = [px, py]
        Clock.schedule_interval(self.update, 1/60)

    def _on_resize(self, *_):
        game = self.ids.game
        self.player_pos[1] = game.y + self.player_size[1] / 2 + 8
        self.player_pos[0] = min(max(self.player_pos[0], game.x + self.player_size[0]/2), game.right - self.player_size[0]/2)

    def toggle_pause(self):
        self.paused = not self.paused

    def request_shoot(self):
        if self._shoot_cooldown <= 0 and not self.paused:
            w, h = 10, 24
            bx = self.player_pos[0] - w/2
            by = self.player_pos[1] + self.player_size[1]/2
            self.bullets.append(Bullet(bx, by, w, h, self.bullet_speed))
            self._shoot_cooldown = 0.18

    def on_area_touch(self, widget, touch):
        if widget is not self.ids.game:
            return False
        if self.paused:
            return False
        if not self.ids.game.collide_point(*touch.pos):
            return False
        self.player_pos[0] = min(max(touch.x, self.ids.game.x + self.player_size[0]/2), self.ids.game.right - self.player_size[0]/2)
        return True

    def spawn_enemy(self, dt):
        game = self.ids.game
        w, h = 56, 32
        x = randint(int(game.x + 4), int(game.right - w - 4))
        y = game.top + h + 12
        self.enemies.append(Enemy(x, y, w, h, self.enemy_speed))

    def update(self, dt):
        if self.paused:
            return
        if self._shoot_cooldown > 0:
            self._shoot_cooldown -= dt
        game = self.ids.game
        if self.move_dir != 0:
            self.player_pos[0] += self.move_dir * self.player_speed * dt
            self.player_pos[0] = min(max(self.player_pos[0], game.x + self.player_size[0]/2), game.right - self.player_size[0]/2)
        from random import random
        if random() < self.enemy_spawn_chance:
            self.spawn_enemy(dt)
        for b in self.bullets[:]:
            b.update(dt)
            if b.y > game.top + 40:
                self.bullets.remove(b)
        for e in self.enemies[:]:
            e.update(dt)
            if e.y + e.h < game.y:
                self.enemies.remove(e)
                self.lose_life()
        self._handle_collisions()
        for ex in self.explosions[:]:
            ex.update(dt)
            if not ex.alive:
                self.explosions.remove(ex)
        self.render()
        if self.lives <= 0:
            self.paused = True
            self.ids.paused_lbl.text = "GAME OVER"

    def lose_life(self):
        self.lives -= 1

    def _handle_collisions(self):
        def collides(ax, ay, aw, ah, bx, by, bw, bh):
            return (ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by)
        pw, ph = self.player_size
        px = self.player_pos[0] - pw/2
        py = self.player_pos[1] - ph/2
        for e in self.enemies[:]:
            hit = False
            for b in self.bullets[:]:
                if collides(b.x, b.y, b.w, b.h, e.x, e.y, e.w, e.h):
                    self.bullets.remove(b)
                    hit = True
                    break
            if hit:
                self.enemies.remove(e)
                self.explosions.append(Explosion(e.x + e.w/2, e.y + e.h/2))
                self.score += 1
            else:
                if collides(px, py, pw, ph, e.x, e.y, e.w, e.h):
                    self.enemies.remove(e)
                    self.explosions.append(Explosion(e.x + e.w/2, e.y + e.h/2))
                    self.lose_life()

    def render(self):
        game = self.ids.game
        game.canvas.clear()
        with game.canvas:
            Color(0, 0, 0, 1)
            Rectangle(pos=game.pos, size=game.size)
            Color(0.2, 0.6, 1, 1)
            pw, ph = self.player_size
            px = self.player_pos[0] - pw/2
            py = self.player_pos[1] - ph/2
            Rectangle(pos=(px, py), size=(pw, ph))
            Color(1, 1, 1, 1)
            for b in self.bullets:
                Rectangle(pos=(b.x, b.y), size=(b.w, b.h))
            Color(1, 0.2, 0.2, 1)
            for e in self.enemies:
                Rectangle(pos=(e.x, e.y), size=(e.w, e.h))
            for ex in self.explosions:
                t = ex.t / ex.duration
                r = 12 + 60 * t
                alpha = max(0.0, 1.0 - t)
                Color(1, 0.6, 0.2, alpha)
                Ellipse(pos=(ex.x - r/2, ex.y - r/2), size=(r, r))

class AuraMobileApp(App):
    def build(self):
        Builder.load_string(KV)
        root = Builder.template("GameRoot")
        return root

if __name__ == "__main__":
    AuraMobileApp().run()
