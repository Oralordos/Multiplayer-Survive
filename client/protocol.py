import xdrlib

from shared.gprotocol import GProtocol, MSG_ERROR
from shared.messages import *


class ClientProtocol(GProtocol):
    def __init__(self, app):
        GProtocol.__init__(self)
        self.app = app

    def connectionMade(self):
        GProtocol.connectionMade(self)

        self.register_handler(MSG_ERROR, self.on_error)
        self.register_handler(SC_GAME_READY, self.on_ready)
        self.register_handler(SC_NEW_GAME, self.on_new_game)
        self.register_handler(SC_LIST_OF_GAMES, self.on_list_of_games)
        self.register_handler(SC_PLAYER_LEAVE, self.on_player_leave)
        self.register_handler(SC_REMOVE_GAME, self.on_remove_game)

        self.app.on_connected(self)

    @staticmethod
    def on_error(unpacker):
        unpacker.unpack_int()
        unpacker.unpack_string()
        return True

    def on_ready(self, unpacker):
        name = unpacker.unpack_string()
        num_players = unpacker.unpack_int()
        self.app.server_ready(name, num_players)
        return True

    def on_new_game(self, unpacker):
        name = unpacker.unpack_string()
        self.app.server_add_game(name)
        return True

    def on_remove_game(self, unpacker):
        name = unpacker.unpack_string()
        self.app.server_remove_game(name)
        return True

    def on_player_leave(self, unpacker):
        name = unpacker.unpack_string()
        self.app.server_player_leave(name)
        return True

    def on_list_of_games(self, unpacker):
        num_games = unpacker.unpack_int()
        game_names = []
        for i in range(num_games):
            game_names.append(unpacker.unpack_string())
        self.app.server_set_game_list(game_names)
        return True

    def send_login(self, name):
        packer = xdrlib.Packer()
        packer.pack_int(CS_LOGIN)
        packer.pack_string(name)
        self.write_packer(packer)

    def send_create_game(self, game_name, max_players):
        packer = xdrlib.Packer()
        packer.pack_int(CS_CREATE_GAME)
        packer.pack_string(game_name)
        packer.pack_int(max_players)
        self.write_packer(packer)

    def send_join_game(self, game_name):
        packer = xdrlib.Packer()
        packer.pack_int(CS_JOIN_GAME)
        packer.pack_string(game_name)
        self.write_packer(packer)

    def send_leave_game(self):
        packer = xdrlib.Packer()
        packer.pack_int(CS_LEAVE_GAME)
        self.write_packer(packer)