import pygame

class Slot:

    def __init__(self, x, y, largura, altura, resposta):

        self.rect = pygame.Rect(x, y, largura, altura)

        self.resposta = resposta

        self.item = None

    def draw(self, tela):

        pygame.draw.rect(tela, (200,200,200), self.rect, 2)

        if self.item:
            self.item.draw(tela)

    def correto(self):

        if self.item:
            return self.item.nome == self.resposta

        return False