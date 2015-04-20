from twisted.internet.protocol import ClientFactory
from twisted.internet import reactor
from protocol import ClientProtocol
from shared.player import Player


class GameClientFactory(ClientFactory):
    def __init__(self, app):
        self.app = app

    def buildProtocol(self, address):
        return ClientProtocol(self.app)


class GenericClient:
    def __init__(self, client_factory_class, player_name):
        self.clientFactoryClass = client_factory_class
        self.playerName = player_name
        self.gameNames = []
        self.player = None
        self.currentGame = None

    @staticmethod
    def update():
        reactor.runUntilCurrent()
        reactor.doSelect(0)

    def on_connected(self, protocol):
        self.player = Player(protocol)
        self.request_login()
        return self.player

    def connect(self, hostname, port):
        reactor.connectTCP(hostname, port, self.clientFactoryClass(self))
        reactor.running = True

    def server_set_game_list(self, game_names):
        self.gameNames = game_names

    def server_add_game(self, name):
        self.gameNames.append(name)

    def server_remove_game(self, name):
        self.gameNames.remove(name)

    def server_ready(self, game_name, num_players):
        self.currentGame = game_name

    def server_player_leave(self, player_name):
        pass

    def request_login(self):
        self.player.protocol.send_login(self.playerName)

    def request_create_game(self, game_name):
        self.player.protocol.send_create_game(game_name)

    def request_join_game(self, game_name):
        self.player.protocol.send_join_game(game_name)

    def request_leave_game(self):
        self.player.protocol.send_leave_game()