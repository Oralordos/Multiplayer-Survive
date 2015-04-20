import pygame
from pygame.locals import *

from client.application import GenericClient
from client.protocol import ClientProtocol


class AdventureClientProtocol(ClientProtocol):
    pass


class AdventureClient(GenericClient):
    def __init__(self):
        GenericClient.__init__(self, AdventureClientProtocol)


def main():
    pygame.init()
    screen = pygame.display.set_mode((640, 480))
    client = AdventureClient()
    try:
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

            client.update()

            screen.fill((0, 0, 0))
            pygame.display.flip()
    finally:
        client.request_leave_game()
        pygame.quit()

if __name__ == '__main__':
    main()