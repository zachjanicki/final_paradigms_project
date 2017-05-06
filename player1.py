'''
player1 handles all logic for collisions and movement
it only sends the destruction of blocks and ball speeds to player 2

player2 does nothing but move the paddle and send its current position back to player1
'''

import pygame, sys, os
from pygame.locals import *
import math
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
import time

from threading import Thread

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


###################################
class MessageBroker(object):
    def __init__(self):
        self.messages_received = []
        self.messages_to_send = []

message_broker = MessageBroker()

class TPCSend(Protocol):
    def connectionMade(self):
        print('connection made! TPCSend')
        pass
    def dataReceived(self, data):
        pass

class TPCSendFactory(ClientFactory):
    def __init__(self):
        self.myconn = TPCSend()
    def buildProtocol(self, addr):
        return self.myconn

class TPCReceive(Protocol):
    def connectionMade(self):
        print('connection made! TPCReceive')
        pass
    def dataReceived(self, data):
        message_broker.messages_received.append(data)
        pass

class TPCReceiveFactory(ClientFactory):
    def __init__(self):
        self.myconn = TPCReceive()
    def buildProtocol(self, addr):
        return self.myconn
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
        else:
            self.surface.fill(GREEN)
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
 
'''       
class MyProtocol(protocol.Protocol):
    def connectionMade(self):
        self.factory.clientConnectionMade(self)
    def connectionLost(self, reason):
        self.factory.clientConnectionLost(self)

class MyFactory(protocol.Factory):
    protocol = MyProtocol
    def __init__(self):
        self.clients = []
        self.lc = LoopingCall(main)
        self.lc.start(.0166)
'''

#################################################
# game set up happens globally

######################################################

def main():

    ##############################################
    # tcp connections
    sender = TPCSendFactory()
    reactor.connectTCP('localhost', 40004, sender)
    receiver = TPCReceiveFactory()
    reactor.listenTCP(41004, receiver)

    #f = LoopingCall(main)
    #f.start(.016666)

    #testFactory = MyFactory()
    print('should be making tcp connections')
    
    print('should be done making tcp connections')
    #reactor.run()
    Thread(target=reactor.run, args=(False, )).start()
    ################################################

    pygame.init()
    screen = pygame.display.set_mode(SCREEN_SIZE)
    pygame.display.set_caption('Brick Breaker Player 1')
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((0, 0, 0))
    screen.blit(background, (0, 0))
    pygame.display.flip()

    clock = pygame.time.Clock()
    running = True

    # create game objects
    paddle1 = Paddle(1)
    paddle2 = Paddle(2)
    p1_bricks = []
    p2_bricks = []
    for i in range(TOTAL_BRICKS_PER_PLAYER):
        if i < 10: # lowest row of bricks
            b1 = Brick(i, BRICK_HEALTH, (i * PADDLE_WIDTH, P1_BRICK_POS_Y), 1)
            p1_bricks.append(b1)
            b2 = Brick(i, BRICK_HEALTH, (i * PADDLE_WIDTH, P2_BRICK_POS_Y), 2)
            p2_bricks.append(b2)
        elif i < 20:
            b1 = Brick(i, BRICK_HEALTH, ((i - 10) * PADDLE_WIDTH, P1_BRICK_POS_Y + PADDLE_HEIGHT), 1)
            p1_bricks.append(b1)
            b2 = Brick(i, BRICK_HEALTH, ((i - 10) * PADDLE_WIDTH, P2_BRICK_POS_Y + PADDLE_HEIGHT), 2)
            p2_bricks.append(b2)
        else:
            b1 = Brick(i, BRICK_HEALTH, ((i - 20) * PADDLE_WIDTH, P1_BRICK_POS_Y + PADDLE_HEIGHT * 2), 1)
            p1_bricks.append(b1)
            b2 = Brick(i, BRICK_HEALTH, ((i - 20) * PADDLE_WIDTH, P2_BRICK_POS_Y + PADDLE_HEIGHT * 2), 2)
            p2_bricks.append(b2)
    ball1 = Ball(1)
    ball2 = Ball(2)

    allsprites = pygame.sprite.Group()
    # add paddles
    allsprites.add(pygame.sprite.RenderPlain(paddle1))
    allsprites.add(pygame.sprite.RenderPlain(paddle2))
    # add bricks to screen
    for b in p1_bricks:
        allsprites.add(pygame.sprite.RenderPlain(b))
    for b in p2_bricks:
        allsprites.add(pygame.sprite.RenderPlain(b))
    # add balls
    allsprites.add(pygame.sprite.RenderPlain(ball1))
    allsprites.add(pygame.sprite.RenderPlain(ball2))

    while running:
        print('running')
        if ball1.speed == None:
            ball1.speed = [5, 5]
        clock.tick(120)
        for e in pygame.event.get():
            if e.type == QUIT:
                running = False
            elif e.type == KEYDOWN and e.key == K_RIGHT:
                paddle1.move('right')
            elif e.type == KEYDOWN and e.key == K_LEFT:
                paddle1.move('left')

        for obj in allsprites:
            if ball1.rect.colliderect(obj.rect) and obj.obj_type == 'paddle' and obj.player_number == 1:
                # then we have collided with our own paddle
                ball1.speed[1] *= -1

            if ball1.rect.colliderect(obj.rect) and obj.obj_type == 'brick': 
                # we have hit a brick so change directions
                ball1.speed[1] *= -1
                allsprites.remove(obj)

        if ball1.rect.right > SCREEN_SIZE[0] - BALL_SIZE[0]: # if we hit the right side
            ball1.speed[0] *= -1

        if ball1.rect.left < 0 + BALL_SIZE[0]: # left
            ball1.speed[0] *= -1

        if ball1.rect.bottom > SCREEN_SIZE[1] - BALL_SIZE[1]: # bottom
            allsprites.remove(ball1)
            ball1 = Ball(1)
            allsprites.add(pygame.sprite.RenderPlain(ball1))

        if ball1.rect.top < 0 + BALL_SIZE[1]: # top
            ball1.speed[1] *= -1

        
        message_broker.messages_to_send.append('hello from p1!')
        # send necessary data to p2 client
        for message in message_broker.messages_to_send:
            sender.myconn.transport.write(message.encode('ascii', 'ignore'))
        message_broker.messages_to_send = []

        # for each message coming from p2, do something about it
        for message in message_broker.messages_received:
            print('Received:', message)
            del message

        message_broker.messages_received = []
        
        allsprites.update()
        screen.blit(background, (0, 0))
        allsprites.draw(screen)
        pygame.display.flip()

if __name__ == '__main__':
    print('here')

    main()



















