import pygame
import random

# Inicializando Pygame
pygame.init()
pygame.joystick.init()

# Tela
dis_width = 600
dis_height = 400
dis = pygame.display.set_mode((dis_width, dis_height))
pygame.display.set_caption('Cobrinha Moderna')

# Cores
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
blue = (50, 153, 213)
yellow = (255, 255, 102)
colors = [(0,255,0), (0,200,0), (50,255,50), (100,255,100)]  # cores da cobra

clock = pygame.time.Clock()
snake_block = 10
snake_speed = 10  # Velocidade inicial

font_style = pygame.font.SysFont("bahnschrift", 25)
score_font = pygame.font.SysFont("comicsansms", 35)

# Inicializar joystick
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
for joystick in joysticks:
    joystick.init()

# Pontuação
def Your_score(score):
    value = score_font.render("Pontuação: " + str(score), True, yellow)
    dis.blit(value, [0, 0])

# Cobra
def our_snake(snake_block, snake_list):
    for i, x in enumerate(snake_list):
        color = colors[i % len(colors)]
        pygame.draw.rect(dis, color, [x[0], x[1], snake_block, snake_block])

# Mensagem
def message(msg, color):
    mesg = font_style.render(msg, True, color)
    dis.blit(mesg, [dis_width / 6, dis_height / 3])

# Função principal
def gameLoop():
    game_over = False
    game_close = False
    paused = False

    x1 = dis_width / 2
    y1 = dis_height / 2
    x1_change = 0
    y1_change = 0

    snake_List = []
    Length_of_snake = 1
    speed = snake_speed

    foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
    foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0

    particles = []

    while not game_over:

        while game_close:
            dis.fill(blue)
            message("Você perdeu! C para jogar novamente ou Q para sair", red)
            Your_score(Length_of_snake - 1)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        game_over = True
                        game_close = False
                    if event.key == pygame.K_c:
                        gameLoop()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

            # Pausa teclado
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    paused = not paused
                elif event.key == pygame.K_w:  # Cima
                    y1_change = -snake_block
                    x1_change = 0
                elif event.key == pygame.K_s:  # Baixo
                    y1_change = snake_block
                    x1_change = 0
                elif event.key == pygame.K_a:  # Esquerda
                    x1_change = -snake_block
                    y1_change = 0
                elif event.key == pygame.K_d:  # Direita
                    x1_change = snake_block
                    y1_change = 0

            # Pausa joystick
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 2:  # botão 3
                    paused = not paused

        # Movimento pelo joystick analógico
        if joysticks:
            axis_x = joysticks[0].get_axis(0)
            axis_y = joysticks[0].get_axis(1)
            if abs(axis_x) > 0.3:
                x1_change = snake_block if axis_x > 0 else -snake_block
                y1_change = 0
            elif abs(axis_y) > 0.3:
                y1_change = snake_block if axis_y > 0 else -snake_block
                x1_change = 0

        # Pausa
        if paused:
            dis.fill(blue)
            message("PAUSADO", red)
            Your_score(Length_of_snake - 1)
            pygame.display.update()
            clock.tick(5)
            continue

        # Checagem de limites
        if x1 >= dis_width or x1 < 0 or y1 >= dis_height or y1 < 0:
            game_close = True

        x1 += x1_change
        y1 += y1_change
        dis.fill(blue)

        # Desenhar comida
        pygame.draw.rect(dis, red, [foodx, foody, snake_block, snake_block])

        # Adicionar partículas na comida
        for p in particles:
            pygame.draw.circle(dis, yellow, (p[0], p[1]), p[2])
            p[2] -= 0.5  # reduzir tamanho
        particles = [p for p in particles if p[2] > 0]

        # Atualizar cobra
        snake_Head = [x1, y1]
        snake_List.append(snake_Head)
        if len(snake_List) > Length_of_snake:
            del snake_List[0]

        for x in snake_List[:-1]:
            if x == snake_Head:
                game_close = True

        our_snake(snake_block, snake_List)
        Your_score(Length_of_snake - 1)
        pygame.display.update()

        # Comer comida
        if x1 == foodx and y1 == foody:
            foodx = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
            foody = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0
            Length_of_snake += 1
            speed += 0.5  # aumenta velocidade
            # Criar partículas
            for _ in range(15):
                particles.append([foodx+5, foody+5, random.randint(3,7)])

        clock.tick(speed)

    pygame.quit()
    quit()

gameLoop()
