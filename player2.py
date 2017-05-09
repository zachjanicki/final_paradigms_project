import pygame, sys, os
from pygame.locals import *
import math
from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
from twisted.internet.task import LoopingCall
from threading import Thread
import time
from game_objects import *

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
P1_BALL_POS_Y = SCREEN_SIZE[1] - (SCREEN_SIZE[1] * (4 / 5) - 50)
P2_BALL_POS_Y = SCREEN_SIZE[1] - (SCREEN_SIZE[1] * (1 / 5) + 50)
###################################

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption('Brick Breaker Player 2')
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
        b2 = Brick(i + TOTAL_BRICKS_PER_PLAYER, BRICK_HEALTH, (i * PADDLE_WIDTH, P2_BRICK_POS_Y), 2)
        p2_bricks.append(b2)
    elif i < 20:
        b1 = Brick(i, BRICK_HEALTH, ((i - 10) * PADDLE_WIDTH, P1_BRICK_POS_Y + PADDLE_HEIGHT), 1)
        p1_bricks.append(b1)
        b2 = Brick(i + TOTAL_BRICKS_PER_PLAYER, BRICK_HEALTH, ((i - 10) * PADDLE_WIDTH, P2_BRICK_POS_Y + PADDLE_HEIGHT), 2)
        p2_bricks.append(b2)
    else:
        b1 = Brick(i, BRICK_HEALTH, ((i - 20) * PADDLE_WIDTH, P1_BRICK_POS_Y + PADDLE_HEIGHT * 2), 1)
        p1_bricks.append(b1)
        b2 = Brick(i + TOTAL_BRICKS_PER_PLAYER, BRICK_HEALTH, ((i - 20) * PADDLE_WIDTH, P2_BRICK_POS_Y + PADDLE_HEIGHT * 2), 2)
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

obj_dict = {'screen': screen,
            'background': background,
            'paddle1': paddle1,
            'paddle2': paddle2,
            'p1_bricks': p1_bricks,
            'p2_bricks': p2_bricks,
            'ball1': ball1,
            'ball2': ball2,
            'allsprites': allsprites}

def main(objects):
    # while running:
    #clock.tick(30)
    screen = objects['screen']
    background = objects['background']
    paddle1 = objects['paddle1']
    paddle2 = objects['paddle2']
    p1_bricks = objects['p1_bricks']
    p2_bricks = objects['p2_bricks']
    ball1 = objects['ball1']
    ball2 = objects['ball2']
    allsprites = objects['allsprites']
    if ball1.speed == None:
        ball1.speed = [5, 5]
    if ball2.speed == None:
        ball2.speed = [-5, -5]
    for e in pygame.event.get():
        if e.type == QUIT:
            running = False
        elif e.type == KEYDOWN and e.key == K_RIGHT:
            paddle2.move('right')
            ### TODO:: send tcp message of paddle movement
            m = 'paddle move right'
            message_broker.messages_to_send.append(m)
        elif e.type == KEYDOWN and e.key == K_LEFT:
            paddle2.move('left')
            ### TODO:: send tcp message of paddle movement
            m = 'paddle move left'
            message_broker.messages_to_send.append(m)
    print(message_broker.messages_to_send)
    for message in message_broker.messages_to_send:
        sender.myconn.transport.write(message.encode('ascii', 'ignore'))
    message_broker.messages_to_send = []

    # for each message coming from p1, do something about it
    for message in message_broker.messages_received:
        print('Received:', message)
        if message == 'paddle move right':
            paddle1.move('right')
        elif message == 'paddle move left':
            paddle1.move('left')
        elif message == 'invert ball1 y_direction':
            ball1.speed[1] *= -1
        elif message == 'invert ball2 y_direction':
            ball2.speed[1] *= -1
        elif message == 'invert ball1 x_direction':
            ball1.speed[0] *= -1
        elif message == 'invert ball2 x_direction':
            ball2.speed[0] *= -1
        elif message == 'new ball1':
            '''
            allsprites.remove(ball1)
            del ball1
            ball1 = Ball(1)
            allsprites.add(pygame.sprite.RenderPlain(ball1))
            ball1.speed = [5, 5]
            '''
        elif message == 'new ball2':
            '''
            allsprites.remove(ball2)
            del ball2
            ball2 = Ball(2)
            allsprites.add(pygame.sprite.RenderPlain(ball2))
            ball2.speed = [-5, -5]
            '''
        elif message.split()[0] == 'delete':
            message = message.split()
            for obj in allsprites:
                if obj.id == int(message[2]):
                    allsprites.remove(obj)
        '''
        elif isinstance(message, int):
            for obj in allsprites:
                if obj.id == message:
                    allsprites.remove(obj)
        '''
        del message

    message_broker.messages_received = []

    allsprites.update()
    screen.blit(background, (0, 0))
    allsprites.draw(screen)
    pygame.display.flip()

###################################
class MessageBroker(object):
    def __init__(self):
        self.messages_received = []
        self.messages_to_send = []

message_broker = MessageBroker()

class TPCSend(Protocol):
    def connectionMade(self):
        print('connection made! TPCSend')
        sender.myconn.transport.write('connect'.encode('ascii', 'ignore'))
        #sender.myconn.transport.write('start'.encode('ascii', 'ignore'))
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
        data = data.decode('utf-8')
        if data == 'begin!':
            sender.myconn.transport.write('begin!'.encode('ascii', 'ignore'))
            f = LoopingCall(main, (obj_dict))
            f.start(.0166)

            return None
        message_broker.messages_received.append(data)
        pass

class TPCReceiveFactory(ClientFactory):
    def __init__(self):
        self.myconn = TPCReceive()
    def buildProtocol(self, addr):
        return self.myconn
######################################


#sender.myconn.transport.write('begin!')

#Thread(target=reactor.run, args=(False, )).start()

receiver = TPCReceiveFactory()
reactor.listenTCP(40004, receiver)

sender = TPCSendFactory()
reactor.connectTCP('localhost', 41004, sender)

print('made tcp connections')

reactor.run()
