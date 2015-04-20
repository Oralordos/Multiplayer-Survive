import struct
import xdrlib

from twisted.internet.protocol import Protocol

MSG_ERROR = -99


class GProtocol(Protocol):
    def __init__(self):
        Protocol.__init__(self)
        self.packetBuffer = ''
        self.packetSize = 0
        self.errorMsg = ''
        self.errorId = 0
        self.msgMap = {}

    def connectionMade(self):
        self.packetBuffer = ''
        self.packetSize = 0
        self.errorMsg = ''
        self.errorId = 0
        self.msgMap = {}

    def dataReceived(self, data):
        self.packetBuffer += data
        while self.packetBuffer:
            if self.packetSize == 0:
                if len(self.packetBuffer) < 4:
                    return
                else:
                    self.packetSize = struct.unpack('i', self.packetBuffer[:4])[0] + 4
            if len(self.packetBuffer) >= self.packetSize:
                packet_data = self.packetBuffer[4:self.packetSize]
                self.packetBuffer = self.packetBuffer[self.packetSize:]
                self.packetSize = 0
                self.process_packet(packet_data)

    def process_packet(self, data):
        unpacker = xdrlib.Unpacker(data)
        msg_id = unpacker.unpack_int()
        handler_method = self.msgMap.get(msg_id)
        if handler_method:
            if not handler_method(unpacker):
                self.send_error()

    def register_handler(self, msg_id, handler):
        self.msgMap[msg_id] = handler

    def write_packer(self, packer):
        data_buffer = packer.get_buffer()
        size_buffer = struct.pack('i', len(data_buffer))
        self.transport.write(size_buffer)
        self.transport.write(data_buffer)

    def send_error(self):
        packer = xdrlib.Packer()
        packer.pack_int(MSG_ERROR)
        packer.pack_int(self.errorId)
        packer.pack_string(self.errorMsg)
        self.write_packer(packer)