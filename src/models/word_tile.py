import pygame
from src import config

class WordTile:
    """
    Representa uma pista coletada pelo jogador em formato de palavra arrastável.
    """
    def __init__(self, text: str, font: pygame.font.Font, x: int = 0, y: int = 0):
        self.text = text
        self.font = font
        self.arrastando = False
        
        # Calcula dimensões com base na renderização de texto
        text_surf = self.font.render(self.text, True, (0, 0, 0))
        self.width = text_surf.get_width() + 14
        self.height = text_surf.get_height() + 8
        
        self.x = x
        self.y = y
        self.original_x = x
        self.original_y = y
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.slot = None  # Slot onde a palavra está encaixada (se houver)

    def update(self):
        self.rect.x = self.x
        self.rect.y = self.y

    def draw(self, surface: pygame.Surface):
        if self.slot:
            # Se a pista estiver encaixada num slot do terminal, ajusta para as coordenadas internas dele
            draw_x = self.slot.rect.x + 2
            draw_y = self.slot.rect.y + 2
            draw_w = self.slot.rect.width - 4
            draw_h = self.slot.rect.height - 4
        else:
            draw_x = self.x
            draw_y = self.y
            draw_w = self.width
            draw_h = self.height

        # Sombra
        shadow_rect = pygame.Rect(draw_x + 2, draw_y + 2, draw_w, draw_h)
        pygame.draw.rect(surface, config.COLOR_CLUE_SHADOW, shadow_rect)
        
        # Placa (Fundo Ouro/Âmbar)
        plate_rect = pygame.Rect(draw_x, draw_y, draw_w, draw_h)
        pygame.draw.rect(surface, config.COLOR_AMBER, plate_rect)
        
        # Destaques e Bordas
        pygame.draw.rect(surface, config.COLOR_AMBER_LITE, plate_rect, 2)  # Borda interna clara
        pygame.draw.rect(surface, config.COLOR_AMBER_DARK, plate_rect, 1)  # Borda externa escura
        
        # Renderização do texto da pista
        text_surf = self.font.render(self.text, True, config.COLOR_CLUE_SHADOW)
        
        # Ajusta/Redimensiona a largura do texto caso ele exceda a largura útil da placa (evitando overflow)
        max_text_w = draw_w - 10
        if text_surf.get_width() > max_text_w:
            scale = max_text_w / text_surf.get_width()
            new_w = max_text_w
            new_h = int(text_surf.get_height() * scale)
            text_surf = pygame.transform.scale(text_surf, (new_w, new_h))
            
        # Blita centralizado verticalmente e horizontalmente
        tx = draw_x + (draw_w - text_surf.get_width()) // 2
        ty = draw_y + (draw_h - text_surf.get_height()) // 2
        surface.blit(text_surf, (tx, ty))

    def reset_position(self):
        self.x = self.original_x
        self.y = self.original_y
        self.slot = None
        self.update()
