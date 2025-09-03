#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Console de Jogos (Launcher) para Pygame
Coloque este arquivo na MESMA PASTA dos jogos e execute:
    python console_launcher.py
Controles:
  - ↑/↓ ou W/S: navegar
  - Enter / Espaço / Botão A (joystick): iniciar jogo
  - Esc / Q: sair (ou voltar ao menu quando um jogo estiver aberto)
  - Joystick: eixo/hat para navegar; A para iniciar; B para voltar
"""
import os
import sys
import subprocess
import pygame
from pathlib import Path
from typing import List

# ------------- Config -------------
WIDTH, HEIGHT = 900, 600
FPS = 60
BG = (15, 15, 22)
FG = (235, 235, 245)
ACCENT = (120, 200, 255)
MUTED = (120, 120, 140)

# Lista de jogos (nome, arquivo, descrição)
GAMES = [
    {"name": "Cobrinha Moderna", "file": "dinossauro.py", "desc": "Cobra com partículas, pausa, joystick."},
    {"name": "Futebol com a Mão (Mobile)", "file": "fortouch.py", "desc": "Controles na tela + teclado/joystick."},
    {"name": "Futebol com a Mão (Clássico)", "file": "Jogo de fut.py", "desc": "1x1 (ou 2x2 no código), placar até 5."},
    {"name": "Jogo do Dinossauro", "file": "pakman.py", "desc": "Pula obstáculos; pausa no R/3 ou botão 3."},
]

# ------------- Helpers -------------
def resolve_path(filename: str) -> Path:
    """Resolve o caminho do arquivo procurando na pasta do script e na pasta de trabalho."""
    here = Path(__file__).resolve().parent
    candidates = [here / filename, Path.cwd() / filename]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]  # default

def wrap_text(font, text, max_width):
    words = text.split()
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def draw_centered(surface, text, font, color, y):
    s = font.render(text, True, color)
    rect = s.get_rect(center=(WIDTH//2, y))
    surface.blit(s, rect)

# ------------- Pygame Setup -------------
pygame.init()
pygame.joystick.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🎮 Console de Jogos (Pygame)")
clock = pygame.time.Clock()
title_font = pygame.font.SysFont("bahnschrift", 46, bold=True)
item_font = pygame.font.SysFont("bahnschrift", 28)
small_font = pygame.font.SysFont("bahnschrift", 22)

# Joysticks
joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
for js in joysticks:
    js.init()

selected = 0
blink = 0

def launch_game(game_path: Path):
    """Executa o jogo em um processo separado e mostra uma tela de status enquanto roda."""
    running = True
    try:
        # Inicia o processo do jogo
        proc = subprocess.Popen([sys.executable, str(game_path)], stdin=subprocess.DEVNULL, cwd=str(game_path.parent))
    except FileNotFoundError:
        # Mostra erro de arquivo não encontrado
        err_loop("Arquivo não encontrado:\n" + str(game_path))
        return
    except Exception as e:
        err_loop("Erro ao iniciar o jogo:\n" + str(e))
        return

    # Loop de monitoramento
    info = f"Iniciando: {game_path.name}"
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Fecha o jogo externo e sai
                try:
                    proc.terminate()
                except Exception:
                    pass
                pygame.quit()
                sys.exit(0)
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_q):
                    # Tenta encerrar o jogo e voltar ao menu
                    try:
                        proc.terminate()
                    except Exception:
                        pass
            elif event.type == pygame.JOYBUTTONDOWN:
                # Botão B (1) como voltar
                if event.button in (1, 6, 7):  # 1=B, 6/7=Back/Start em alguns controles
                    try:
                        proc.terminate()
                    except Exception:
                        pass

        # Se o processo já terminou, volta ao menu
        if proc.poll() is not None:
            running = False

        # Tela de "Carregando/Jogando"
        screen.fill(BG)
        draw_centered(screen, "Jogo em execução…", title_font, FG, HEIGHT//2 - 20)
        draw_centered(screen, "Pressione ESC (ou B no controle) para voltar ao menu", small_font, MUTED, HEIGHT//2 + 20)
        pygame.display.flip()

def err_loop(msg: str):
    t = 0
    while t < 240:  # ~4 segundos
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit(0)
            elif event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                return
        screen.fill(BG)
        draw_centered(screen, "Erro", title_font, (255,120,120), HEIGHT//2 - 60)
        for i, line in enumerate(wrap_text(small_font, msg, WIDTH - 120)):
            draw_centered(screen, line, small_font, FG, HEIGHT//2 + i*26)
        pygame.display.flip()
        t += 1

def handle_joystick_nav():
    global selected
    moved = False
    for js in joysticks:
        # Hat (seta do direcional)
        if js.get_numhats() > 0:
            hat = js.get_hat(0)
            if hat[1] == 1 and not handle_joystick_nav.last_up:
                selected = (selected - 1) % len(GAMES)
                moved = True
            if hat[1] == -1 and not handle_joystick_nav.last_down:
                selected = (selected + 1) % len(GAMES)
                moved = True
            handle_joystick_nav.last_up = (hat[1] == 1)
            handle_joystick_nav.last_down = (hat[1] == -1)

        # Eixo Y do analógico esquerdo
        axis_y = js.get_axis(1) if js.get_numaxes() > 1 else 0.0
        dead = 0.4
        if axis_y < -dead and not handle_joystick_nav.axis_up:
            selected = (selected - 1) % len(GAMES); moved = True
        if axis_y > dead and not handle_joystick_nav.axis_down:
            selected = (selected + 1) % len(GAMES); moved = True
        handle_joystick_nav.axis_up = axis_y < -dead
        handle_joystick_nav.axis_down = axis_y > dead

        # Botões
        if js.get_button(0):  # A
            # Lança jogo
            game_file = resolve_path(GAMES[selected]["file"])
            launch_game(game_file)
    return moved
handle_joystick_nav.last_up = False
handle_joystick_nav.last_down = False
handle_joystick_nav.axis_up = False
handle_joystick_nav.axis_down = False

# ------------- Main Loop -------------
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                selected = (selected - 1) % len(GAMES)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                selected = (selected + 1) % len(GAMES)
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                game_file = resolve_path(GAMES[selected]["file"])
                launch_game(game_file)
            elif event.key in (pygame.K_ESCAPE, pygame.K_q):
                running = False

    # Navegação por joystick (poll a cada frame)
    handle_joystick_nav()

    # Render
    screen.fill(BG)
    draw_centered(screen, "🎮 Console de Jogos", title_font, FG, 80)

    top = 150
    item_h = 86
    for i, g in enumerate(GAMES):
        y = top + i * item_h
        rect = pygame.Rect(120, y-28, WIDTH-240, 64)
        # highlight
        if i == selected:
            pygame.draw.rect(screen, (30, 40, 60), rect, border_radius=14)
            pygame.draw.rect(screen, ACCENT, rect, width=2, border_radius=14)
        else:
            pygame.draw.rect(screen, (25, 28, 35), rect, border_radius=14)
            pygame.draw.rect(screen, (45, 55, 70), rect, width=1, border_radius=14)

        name_surf = item_font.render(g["name"], True, FG if i == selected else (210,210,220))
        screen.blit(name_surf, (rect.x + 18, rect.y + 10))

        desc_lines = []
        # wrap description
        desc = g.get("desc","")
        # manual wrap to width
        # use small_font.size to check width
        words = desc.split()
        line = ""
        for w in words:
            test = (line + " " + w).strip()
            if small_font.size(test)[0] <= rect.width - 36:
                line = test
            else:
                if line:
                    desc_lines.append(line)
                line = w
        if line:
            desc_lines.append(line)
        for j, ln in enumerate(desc_lines[:2]):
            screen.blit(small_font.render(ln, True, MUTED), (rect.x + 18, rect.y + 36 + j*22))

    # footer/help
    help_text = "↑/↓ para navegar • Enter/Espaço para iniciar • ESC para sair"
    draw_centered(screen, help_text, small_font, MUTED, HEIGHT - 30)

    pygame.display.flip()

pygame.quit()
