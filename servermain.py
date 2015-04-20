import argparse
import xdrlib

from server.gameserver import ServerGame, GameServerApp
from server.protocol import ServerProtocol
from adventuremessages import *

LOBBY = 0


class AdventureServerProtocol(ServerProtocol):
    def connectionMade(self):
        ServerProtocol.connectionMade(self)

        self.register_handler(CS_LOGIN_GAME, self.on_login_game)
        self.register_handler(CS_START_GAME, self.on_start_game)

    def on_login_game(self, unpacker):
        email = unpacker.unpack_string()
        self.player.email = email
        [player.protocol.send_player_login(self.player, email) for player in self.app.players]

    def on_start_game(self, unpacker):
        if self.player != self.player.currentGame.host:
            self.player.set_error(1000, 'Cannot start game if you are not host.')
            return False
        elif self.player.currentGame.currentMode != LOBBY:
            self.player.set_error(1001, 'Cannot start an already started game.')
            return False
        else:
            self.player.currentGame.start_game()
            return True

    def send_player_login(self, player, email):
        packer = xdrlib.Packer()
        packer.pack_int(SC_LOGIN_PLAYER)
        packer.pack_string(player.name)
        packer.pack_string(email)
        self.write_packer(packer)

    def send_start_game(self):
        packer = xdrlib.Packer()
        packer.pack_int(SC_START_GAME)
        self.write_packer(packer)

    def send_game_information(self):
        packer = xdrlib.Packer()
        packer.pack_int(SC_SEND_GAME_INFORMATION)
        self.write_packer(packer)


class AdventureGame(ServerGame):
    def __init__(self, name, application, max_players):
        max_players = min(4, max_players)
        ServerGame.__init__(self, name, application, max_players)

        self.currentMode = LOBBY
        self.host = None

    def add_player(self, player):
        if self.currentMode != LOBBY:
            player.set_error(100, 'Game is in progress')
            return False

        added = ServerGame.add_player(self, player)
        if added:
            self.host = self.host or player
            player.protocol.send_game_information()
        return added

    def remove_player(self, player):
        ServerGame.remove_player(self, player)
        if player.name == self.host.name:
            if len(self.players) == 0:
                self.host = None
            else:
                self.host = self.players[0]

    def start_game(self):
        [player.protocol.send_start_game() for player in self.players]

    def update(self, interval):
        pass


def main():
    parser = argparse.ArgumentParser(description='Game Server')
    parser.add_argument('-p', '--port', default=10000, type=int, help='Port to run the server on.')
    args = parser.parse_args()
    server_app = GameServerApp(args.port, AdventureServerProtocol, AdventureGame)
    server_app.run(1.0/30)

if __name__ == '__main__':
    main()