import xdrlib

from shared.gprotocol import GProtocol
from shared.messages import *


class ServerProtocol(GProtocol):
    def __init__(self, app):
        GProtocol.__init__(self)
        self.app = app
        self.player = None

    def connectionMade(self):
        GProtocol.connection_made(self)
        self.player = self.app.add_player(self)

        self.register_handler(CS_CREATE_GAME, self.on_create_game)
        self.register_handler(CS_JOIN_GAME, self.on_join_game)
        self.register_handler(CS_LOGIN, self.on_login)
        self.register_handler(CS_LEAVE_GAME, self.on_leave_game)

    def connectionLost(self, reason=None):
        self.app.remove_player(self.player)

    def on_login(self, unpacker):
        name = unpacker.unpack_string()
        return self.app.login(name, self.player)

    def on_create_game(self, unpacker):
        name = unpacker.unpack_string()
        max_players = unpacker.unpack_int()
        return self.app.create_game(name, self.player, max_players)

    def on_join_game(self, unpacker):
        name = unpacker.unpack_string()
        self.app.join_game(name, self.player)
        return True

    def on_leave_game(self, unpacker):
        self.app.leave_game(self.player)
        return True

    def send_ready(self, game_name, num_players):
        packer = xdrlib.Packer()
        packer.pack_int(SC_GAME_READY)
        packer.pack_string(game_name)
        packer.pack_int(num_players)
        self.write_packer(packer)

    def send_player_leave(self, player_name):
        packer = xdrlib.Packer()
        packer.pack_int(SC_PLAYER_LEAVE)
        packer.pack_string(player_name)
        self.write_packer(packer)

    def send_game_list(self, games):
        packer = xdrlib.Packer()
        packer.pack_int(SC_LIST_OF_GAMES)
        packer.pack_int(len(games))
        [packer.pack_string(game.name) for game in games]
        self.write_packer(packer)

    def send_remove_game(self, game_name):
        packer = xdrlib.Packer()
        packer.pack_int(SC_REMOVE_GAME)
        packer.pack_string(game_name)
        self.write_packer(packer)

    def send_new_game(self, game_name):
        packer = xdrlib.Packer()
        packer.pack_int(SC_NEW_GAME)
        packer.pack_string(game_name)
        self.write_packer(packer)