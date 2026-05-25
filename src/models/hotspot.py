import pygame

class Hotspot:
    """
    Representa uma área interativa (hitbox) na tela de exploração do cenário.
    """
    def __init__(self, name: str, label: str, rect: pygame.Rect):
        self.name = name
        self.label = label
        self.rect = rect  # Coordenadas lógicas relativas à área 800x600 do cenário
        self.hovered = False
