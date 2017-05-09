import pygame, sys, os
from pygame.locals import *
import math

''' some global constants '''
###################################
SCREEN_SIZE = (500, 500)
PADDLE_WIDTH = SCREEN_SIZE[0] / 10
PADDLE_HEIGHT = SCREEN_SIZE[1] / 50
TOTAL_BRICKS_PER_PLAYER = int(3 * SCREEN_SIZE[0] / PADDLE_WIDTH)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BRICK_HEALTH = 10
P1_BRICK_POS_Y = SCREEN_SIZE[1] - (SCREEN_SIZE[1] / 2 - (SCREEN_SIZE[1] / 10)) - PADDLE_HEIGHT * 2
P2_BRICK_POS_Y = -1 * (P1_BRICK_POS_Y - SCREEN_SIZE[1])
BALL_SIZE = (10, 10)
P1_BALL_POS_Y = SCREEN_SIZE[1] - (SCREEN_SIZE[1] * (1 / 5) + 50)
P2_BALL_POS_Y = SCREEN_SIZE[1] - (SCREEN_SIZE[1] * (4 / 5) - 50)
###################################

class Paddle(pygame.sprite.Sprite):
    def __init__(self, player_number):
        pygame.sprite.Sprite.__init__(self)
        self.obj_type = 'paddle'
        self.player_number = player_number
        self.surface = pygame.Surface((PADDLE_WIDTH, PADDLE_HEIGHT))
        self.rect = self.surface.get_rect()
        self.surface.fill(WHITE)
        self.image = self.surface
        if player_number == 1: # position of player 1
            self.rect = self.rect.move(SCREEN_SIZE[0] / 2 - PADDLE_WIDTH / 2, SCREEN_SIZE[1] - 50)
        else: # position of player 2
            self.rect = self.rect.move(SCREEN_SIZE[0] / 2 - PADDLE_WIDTH / 2, SCREEN_SIZE[1] - (SCREEN_SIZE[1] - 50))

    def update(self):
        pass
        
    def move(self, direction):
        if direction == 'right' and self.rect.right < SCREEN_SIZE[0]:
            self.rect = self.rect.move([20, 0])
        elif direction == 'left' and self.rect.left > 0:
            self.rect = self.rect.move([-20, 0])

class Brick(pygame.sprite.Sprite):
    def __init__(self, brick_id, health, starting_location, player_number):
        pygame.sprite.Sprite.__init__(self)
        self.obj_type = 'brick'
        self.player_number = player_number
        self.id = brick_id
        self.health = health
        self.surface = pygame.Surface(((SCREEN_SIZE[0] / 10), 10))
        self.rect = self.surface.get_rect()
        self.image = self.surface
        # this assumes we keep 10 bricks per row
        if brick_id < 10:
            self.surface.fill(BLUE)
        elif brick_id < 20:
            self.surface.fill(RED)
        elif brick_id < 30:
            self.surface.fill(GREEN)
        elif brick_id < 40:
            self.surface.fill(GREEN)
        elif brick_id < 50:
            self.surface.fill(RED)
        elif brick_id < 60:
            self.surface.fill(BLUE)
        self.rect = self.rect.move(starting_location)

    def update(self):
        pass

class Ball(pygame.sprite.Sprite):
    def __init__(self, player_number):
        pygame.sprite.Sprite.__init__(self)
        self.obj_type = 'ball'
        self.player_number = player_number
        self.surface = pygame.Surface(BALL_SIZE)
        self.surface.fill(WHITE)
        self.rect = self.surface.get_rect()
        self.image = self.surface
        self.speed = None
        if player_number == 1:
            self.rect = self.rect.move([SCREEN_SIZE[0] / 2, P1_BALL_POS_Y])
        else:
            self.rect = self.rect.move([SCREEN_SIZE[0] / 2, P2_BALL_POS_Y])

    def update(self):
        if self.speed:
            self.rect = self.rect.move(self.speed)
 