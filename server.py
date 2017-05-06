from twisted.internet.protocol import ClientFactory
from twisted.internet.protocol import Protocol
from twisted.internet import reactor
import time

class conn_count(object):
    def __init__(self):
        self.count = 0

c = conn_count()

class P1Listen(Protocol):
    def connectionMade(self):
        c.count += 1
        print('listening for messages from p1')
        reactor.connectTCP('localhost', 43004, p2S)
        pass

    def dataReceived(self, data):
        print(data)
        if c.count > 1:
            p2S.myconn.transport.write(data)
        pass

class P1ListenFactory(ClientFactory):
    def __init__(self):
        self.myconn = P1Listen()
    def buildProtocol(self, addr):
        return self.myconn

class P1Send(Protocol):
    def connectionMade(self):
        print('able to send messages to p1')
        pass

    def dataReceived(self, data):
        print('data to be sent to p1', data)
        pass

class P1SendFactory(ClientFactory):
    def __init__(self):
        self.myconn = P1Send()
    def buildProtocol(self, addr):
        return self.myconn

class P2Listen(Protocol):
    def connectionMade(self):
        c.count += 1
        print('listening for messages from p2')
        reactor.connectTCP('localhost', 41004, p1S)
        pass

    def dataReceived(self, data):
        print(data)
        if c.count > 1:
            p1S.myconn.transport.write(data)
        pass

class P2ListenFactory(ClientFactory):
    def __init__(self):
        self.myconn = P2Listen()
    def buildProtocol(self, addr):
        return self.myconn

class P2Send(Protocol):
    def connectionMade(self):
        print('able to send messages to p2')
        pass

    def dataReceived(self, data):
        print('data to be sent to p2', data)
        pass

class P2SendFactory(ClientFactory):
    def __init__(self):
        self.myconn = P2Send()
    def buildProtocol(self, addr):
        return self.myconn

p1L = P1ListenFactory()
p1S = P1SendFactory()
p2L = P2ListenFactory()
p2S = P2SendFactory()

reactor.listenTCP(40004, p1L)

reactor.listenTCP(42004, p2L)

reactor.run()