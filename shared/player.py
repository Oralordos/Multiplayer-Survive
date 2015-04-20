class Player:
    def __init__(self, protocol):
        self.protocol = protocol
        self.currentGame = None
        self.name = None

    def destroy(self):
        self.protocol = None

    def set_error(self, id, msg):
        self.protocol.error_id = id
        self.protocol.error_msg = msg