import pygame
from src import config

class Slot:
    """
    Caixa receptora onde o jogador pode encaixar os WordTiles para resolver a sentença.
    """
    def __init__(self, label: str, x: int, y: int, largura: int, altura: int, resposta: str, font: pygame.font.Font):
        self.label = label
        self.rect = pygame.Rect(x, y, largura, altura)
        self.resposta = resposta
        self.item = None
        self.font = font

    def draw(self, surface: pygame.Surface):
        # Desenha a label acima do slot em verde CRT
        label_surf = self.font.render(self.label, True, config.COLOR_CRT_GREEN)
        label_rect = label_surf.get_rect(centerx=self.rect.centerx, bottom=self.rect.top - 6)
        surface.blit(label_surf, label_rect)

        # Desenha a caixa do slot (Fundo verde CRT escuro)
        pygame.draw.rect(surface, config.COLOR_CRT_BG_DARK, self.rect)
        
        # Borda dinâmica: acende se houver um item encaixado
        border_color = config.COLOR_CRT_GREEN_DARK
        if self.item:
            border_color = config.COLOR_CRT_GREEN_LITE
        pygame.draw.rect(surface, border_color, self.rect, 2)

        # Atualiza a posição da palavra encaixada centralizada no slot
        if self.item:
            self.item.x = self.rect.x + (self.rect.width - self.item.width) // 2
            self.item.y = self.rect.y + (self.rect.height - self.item.height) // 2
            self.item.update()

    def correto(self) -> bool:
        if self.item:
            return self.item.text == self.resposta
        return False
