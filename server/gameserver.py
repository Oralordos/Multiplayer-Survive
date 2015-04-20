import time

from twisted.internet import reactor
from twisted.internet.protocol import Factory
from shared.player import Player


class GameProtocolFactory(Factory):
    def __init__(self, app, protocol_class):
        self.app = app
        self.protocolClass = protocol_class

    def buildProtocol(self, address):
        p = self.protocolClass(self.app)
        p.factory = self
        return p


class ServerGame:
    def __init__(self, name, application, max_players):
        self.name = name
        self.application = application
        self.max_players = max_players
        self.players = []

    def add_player(self, player):
        if self.max_players > len(self.players):
            self.players.append(player)
            return True
        player.set_error(14, 'Game is full')
        return False

    def remove_player(self, player):
        self.players.remove(player)


class GameServerApp:
    def __init__(self, port, protocol_class, game_class):
        self.port = port
        self.gameClass = game_class
        self.factory = GameProtocolFactory(self, protocol_class)
        reactor.listenTCP(port, self.factory)
        self.players = []
        self.games = []
        self.running = True
        self.beginFrame = 0
        self.lastFrame = 0

    def run(self, delay):
        self.lastFrame = time.time()
        self.beginFrame = time.time()

        while self.running:
            now = time.time()
            interval = now - self.beginFrame
            self.beginFrame = now
            self.iterate(interval)
            time.sleep(delay)

    def iterate(self, interval):
        reactor.doSelect(0)
        [game.update(interval) for game in self.games]

    def login(self, name, player):
        player.name = name
        player.protocol.sendGameList(self.games)
        return True

    def add_player(self, protocol):
        new_player = Player(protocol)
        self.players.append(new_player)
        return new_player

    def remove_player(self, player):
        if player.currentGame:
            player.currentGame.remove_player(player)
        player.destroy()
        self.players.remove(player)

    def create_game(self, name, player, max_players):
        for game in self.games:
            if game.name == name:
                player.set_error(11, 'Game {0} already exists'.format(name))
                return False
        new_game = self.gameClass(name, self, max_players)
        self.games.append(new_game)

        [p.protocol.sendNewGame(name) for p in self.players]

        return self.join_game(name, player)

    def join_game(self, name, player):
        if player.currentGame:
            player.set_error(12, 'Already playing a game')
            return False

        for game in self.games:
            if game.name == name:
                result = game.add_player(player)
                if result:
                    player.currentGame = game
                return result

        player.set_error(13, 'Game {0} does not exist'.format(name))
        return False

    @staticmethod
    def leave_game(player):
        if not player.currentGame:
            player.set_error(15, 'Not in a game!!!')
            return 0

        player.currentGame.remove_player(player)
        player.currentGame = None

    def remove_game(self, game):
        self.games.remove(game)
        [p.protocol.send_remove_game(game.name) for p in self.players]