import pygame
import neat
import time
import os
import random

WIDTH, HEIGHT = 500, 800;
pygame.font.init()
BIRD_IMAGS = [];
BIRD_IMAGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
              pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
              pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 50)

FPS = 30
GEN = 0



class Bird():
    IMGS = BIRD_IMAGS
    MAX_ROTAITION = 25
    ROT_VEL = 20
    ANIMATION_TIME = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0
        self.height = self.y

    def move(self):
        self.tick_count += 1

        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2

        if d >= 16:
            d = 16
        if d < 0:
            d -= 2
        self.y = self.y + d
        if d < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTAITION:
                self.tilt = self.MAX_ROTAITION
        else:
            if self.tilt > -90:
                self.tilt = -self.ROT_VEL

    def draw(self, win):
        self.img_count += 1
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME * 2
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)


def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)

    surf.blit(rotated_image, new_rect.topleft)


class Pipe:
    GAP = 200


    def __init__(self, x,vel):
        self.x = x
        self.height = 0
        self.top = 0
        self.buttom = 0
        self.VEL=vel
        self.TOP_PIPE = pygame.transform.flip(PIPE_IMG, False, True)
        self.PIPE_BUTTOM = PIPE_IMG
        self.passed = False
        self.set_height()

    def speed_up(self):
        self.VEL += 1

    def set_height(self):
        self.height = random.randrange(50, 450)
        self.top = self.height - self.TOP_PIPE.get_height()
        self.buttom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(self.TOP_PIPE, (self.x, self.top))
        win.blit(self.PIPE_BUTTOM, (self.x, self.buttom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.TOP_PIPE)
        buttom_mask = pygame.mask.from_surface(self.PIPE_BUTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        buttom_offset = (self.x - bird.x, self.buttom - round(bird.y))

        b_point = bird_mask.overlap(buttom_mask, buttom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)
        if t_point or b_point:
            return True
        else:
            return False


class Base():
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0:
            self.x1 = self.x2 + self.WIDTH
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score, gen):
    if gen == 0:
        gen = 1
    win.blit(BG, ((0, 0)))
    for pipe in pipes:
        pipe.draw(win)

    score_text = STAT_FONT.render("Score : " + str(score), 1, (255, 255, 255))
    gen_text = STAT_FONT.render("Gen : " + str(gen), 1, (255, 255, 255))
    alive_text = STAT_FONT.render("Alive : " + str(len(birds)), 1, (255, 255, 255))
    win.blit(score_text, (WIDTH - 10 - score_text.get_width(), 10))
    win.blit(gen_text, (10, 10))
    win.blit(alive_text, (10, gen_text.get_height() + 10))
    base.draw(win)
    for bird in birds:
        bird.draw(win)
    pygame.display.update()


def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    birds = []
    speedUp = False
    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)
    base = Base(HEIGHT - 70)
    PIPE_VEl = 5
    pipes = [Pipe(700,PIPE_VEl)]
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    run = True
    clock = pygame.time.Clock()
    score = 0

    while run:
        clock.tick(FPS)
        pipe_ind = 0
        if score % 5 == 1:
            speedUp = False
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].TOP_PIPE.get_width():
                pipe_ind = 1
        else:
            run = False
            break
        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1
            output = nets[x].activate(
                (bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].buttom)))
            if output[0] > 0.5:
                bird.jump()
        add_pipe = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        rem = []
        for pipe in pipes:
            if score is not 0 and score % 5 == 0:
                if not speedUp:
                    PIPE_VEl+=1
                    speedUp = True
            pipe.move()
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True
            if pipe.x + pipe.PIPE_BUTTOM.get_width() < 0:
                rem.append(pipe)

        if add_pipe:
            score += 1
            for g in ge:
                g.fitness += 2
            pipes.append(Pipe(700,PIPE_VEl))
        for pipe in rem:
            pipes.remove(pipe)
        draw_window(win, birds, pipes, base, score, GEN)
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= HEIGHT - 70 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
        base.move()


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)
    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(neat.StatisticsReporter())
    winner = p.run(main, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
