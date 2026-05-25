class Objetos: 
    def __init__(self, x, y, imagem, valor):
        self.x = x
        self.y = y

        self.valor = valor

        self.imagem = imagem

        self.rect = self.imagem.get_rect(topleft=(x, y))

        self.arrastando = False

    def update(self):
        self.rect.topleft = (self.x, self.y)

    def draw(self, surface):
        surface.blit(self.imagem, (self.x, self.y))