import pygame, sys, random
from pygame.locals import QUIT, K_SPACE

pygame.init()

class constant:
    screen_w = 500
    screen_h = 600
    bg_color = (135, 206, 235)
    gravity = 0.25
    jump_force = -6.5
    fps = 60
    ground_h = 50
    pipe_w = 70
    pipe_gap = 200
    pipe_speed = 2.5

screen = pygame.display.set_mode((constant.screen_w, constant.screen_h))
pygame.display.set_caption('Flapy bird')
clock = pygame.time.Clock()

font = pygame.font.SysFont(None, 36)

class bird:
    def __init__(self):
        self.x = 100
        self.y = constant.screen_h // 2
        self.wb = 30
        self.hb = 30
        self.v = 0
        self.rect = pygame.Rect(self.x + 8, self.y + 6, self.wb - 16, self.hb - 12)

        self.image = pygame.image.load('bird.png')
        self.image = pygame.transform.scale(self.image, (self.wb, self.hb))
    
    def update(self):
        self.v += constant.gravity
        self.y += self.v

        self.rect.y = self.y + 6

        if self.y < 0:
            self.y = 0
            self.v = 0

        if self.y + self.hb >= constant.screen_h - constant.ground_h:
            self.y = constant.screen_h - constant.ground_h - self.hb
            self.v = 0

    def jump(self):
        self.v = constant.jump_force

    def draw(self, surface):
        surface.blit(self.image, (self.x, self.y))

class pipe:
    def __init__(self, x):
        self.x = x
        self.w = constant.pipe_w
        self.gap = constant.pipe_gap
        self.passed = False

        min_top_h = 80
        min_bottom_h = 100
        max_top_h = constant.screen_h - constant.ground_h - self.gap - min_bottom_h

        self.top_h = random.randint(min_top_h, max_top_h)

        self.top_rect = pygame.Rect(self.x + 15, 0, self.w - 30, self.top_h)
        self.bottom_rect = pygame.Rect(
            self.x + 15,
            self.top_h + self.gap,
            self.w - 30,
            constant.screen_h - self.top_h - self.gap - constant.ground_h
        )

        self.pipe_image = pygame.image.load('pipe.png')
        self.pipe_image = pygame.transform.scale(self.pipe_image, (self.w, constant.screen_h))
        self.top_pipe_image = pygame.transform.flip(self.pipe_image, False, True)

    def update(self):
        self.x -= constant.pipe_speed
        self.top_rect.x = self.x + 15
        self.bottom_rect.x = self.x + 15

    def off_screen(self):
        return self.x + self.w < 0
    
    def draw(self, surface):
        surface.blit(self.top_pipe_image, (self.x, 0), (0, constant.screen_h - self.top_h, self.w, self.top_h))

        bottom_pipe_y = self.top_h + self.gap
        bottom_pipe_height = constant.screen_h - self.top_h - self.gap - constant.ground_h
        surface.blit(self.pipe_image, (self.x, bottom_pipe_y), (0, 0, self.w, bottom_pipe_height))

class game: 
    def __init__(self):
        self.bird = bird()
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.pipe_timer = 0
        self.pipe_interval = 2000

        self.spawn_pipe()

    def spawn_pipe(self):
        new_pipe = pipe(constant.screen_w)
        self.pipes.append(new_pipe)

    def update(self):
        if self.game_over:
            return
        
        self.bird.update()

        if self.bird.y + self.bird.hb >= constant.screen_h - constant.ground_h:
            self.game_over = True

        for pipe in self.pipes[:]:
            pipe.update()

            if self.bird.rect.colliderect(pipe.top_rect) or self.bird.rect.colliderect(pipe.bottom_rect):
                self.game_over = True
                
            if not pipe.passed and pipe.x + pipe.w < self.bird.x:
                pipe.passed = True
                self.score += 1

            if pipe.off_screen():
                self.pipes.remove(pipe)

        self.pipe_timer += clock.get_time()
        if self.pipe_timer > self.pipe_interval:
            self.spawn_pipe()
            self.pipe_timer = 0

    def draw(self, surface):
        surface.fill(constant.bg_color)

        for pipe in self.pipes:
            pipe.draw(surface)

        self.bird.draw(surface)

        pygame.draw.rect(
            surface,
            (34, 139, 34),
            (0, constant.screen_h - constant.ground_h, constant.screen_w, constant.ground_h)
        )

        score_text = font.render(f'Счет: {self.score}', True, (255, 255, 255))
        surface.blit(score_text, (10,10))

        if self.game_over:
            game_over_text = font.render('Нажмите пробел для возрождения', True, (255, 0, 0))
            text_rect = game_over_text.get_rect(center=(constant.screen_w//2, constant.screen_h//2))
            surface.blit(game_over_text, text_rect)
    
    def restart(self):
        self.__init__()

games = game()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == K_SPACE:
                if games.game_over:
                    games.restart()
                else:
                    games.bird.jump()

    games.update()
    games.draw(screen)
    pygame.display.update()
    clock.tick(constant.fps)