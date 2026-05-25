import pygame

class Palavra:

    def __init__(self, x, y, texto, fonte):

        self.nome = texto

        self.texto = fonte.render(texto, True, (255,255,255))

        self.rect = self.texto.get_rect(topleft=(x,y))

        self.x = x
        self.y = y

        self.arrastando = False

    def draw(self, tela):

        tela.blit(self.texto, (self.x, self.y))

    def update(self):

        self.rect.topleft = (self.x, self.y)