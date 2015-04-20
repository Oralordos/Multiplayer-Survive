import argparse
import xdrlib

from server.gameserver import ServerGame, GameServerApp
from server.protocol import ServerProtocol
from adventuremessages import *

LOBBY = 0


class AdventureProtocol(ServerProtocol):
    def connectionMade(self):
        ServerProtocol.connectionMade(self)

        self.register_handler(CS_LOGIN_GAME, self.on_login_game)

    def on_login_game(self, unpacker):
        email = unpacker.unpack_string()
        self.player.email = email
        [player.protocol.send_player_login(self.player, email) for player in self.app.players]

    def send_player_login(self, player, email):
        packer = xdrlib.Packer()
        packer.pack_int(SC_LOGIN_PLAYER)
        packer.pack_string(player.name)
        packer.pack_string(email)
        self.write_packer(packer)


class AdventureGame(ServerGame):
    def __init__(self, name, application, max_players):
        max_players = min(4, max_players)
        ServerGame.__init__(self, name, application, max_players)

        self.currentMode = LOBBY

    def add_player(self, player):
        if self.currentMode != LOBBY:
            player.set_error(100, 'Game is in progress')
            return False

        return ServerGame.add_player(self, player)

    def remove_player(self, player):
        ServerGame.remove_player(self, player)

    def update(self, interval):
        pass


def main():
    parser = argparse.ArgumentParser(description='Game Server')
    parser.add_argument('-p', '--port', default=10000, type=int, help='Port to run the server on.')
    args = parser.parse_args()
    server_app = GameServerApp(args.port, AdventureProtocol, AdventureGame)
    server_app.run(1.0/30)

if __name__ == '__main__':
    main()