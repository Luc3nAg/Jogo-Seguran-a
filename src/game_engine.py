import pygame
import sys
from src import config
from src.world import World
from src.models.slot import Slot
from src.models.hotspot import Hotspot

class GameEngine:
    """
    Gerencia a inicialização global do jogo, o loop principal, o controle
    de eventos do teclado e mouse, as dimensões físicas da janela e o letterboxing.
    """
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Vazamento Critico - Investigacao SOC 2026")
        
        self.screen_w = config.SCREEN_W
        self.screen_h = config.SCREEN_H
        self.tela = pygame.display.set_mode((self.screen_w, self.screen_h), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        
        # Canvas lógico para renderização virtual independente de resolução física
        self.canvas = pygame.Surface((config.CANVAS_W, config.CANVAS_H))
        
        # Parâmetros de escala e letterboxing padrão
        self.scale_factor = min(self.screen_w / config.CANVAS_W, self.screen_h / config.CANVAS_H)
        self.canvas_w = int(config.CANVAS_W * self.scale_factor)
        self.canvas_h = int(config.CANVAS_H * self.scale_factor)
        self.ox = (self.screen_w - self.canvas_w) // 2
        self.oy = (self.screen_h - self.canvas_h) // 2
        
        # Carrega fontes retro utilizando a fonte pixel VT323
        font_path = config.get_path("fontes/VT323-Regular.ttf")
        try:
            self.font_title = pygame.font.Font(font_path, 48)
            self.font_ui = pygame.font.Font(font_path, 24)
            self.font_text = pygame.font.Font(font_path, 26)
            self.font_word = pygame.font.Font(font_path, 24)
            self.font_victory = pygame.font.Font(font_path, 24)
        except Exception as e:
            print("Erro ao carregar fonte VT323, usando consolas:", e)
            self.font_title = pygame.font.SysFont("consolas", 40, bold=True)
            self.font_ui = pygame.font.SysFont("consolas", 18, bold=True)
            self.font_text = pygame.font.SysFont("consolas", 20)
            self.font_word = pygame.font.SysFont("consolas", 18, bold=True)
            self.font_victory = pygame.font.SysFont("consolas", 18)
        
        # Inicializa os slots de investigação no Terminal de Sentenças
        ox_term = config.TERM_X
        oy_term = config.TERM_Y
        
        self.slot_who = Slot("", ox_term + 105, oy_term + 85, 140, 30, "Estagiário", self.font_ui)
        self.slot_how = Slot("", ox_term + 370, oy_term + 140, 140, 30, "Sênior", self.font_ui)
        self.slot_pwd = Slot("", ox_term + 230, oy_term + 195, 160, 30, "senh@forte123", self.font_ui)
        self.slot_where = Slot("", ox_term + 250, oy_term + 250, 100, 30, "PC", self.font_ui)
        self.slot_why = Slot("", ox_term + 230, oy_term + 305, 140, 30, "Malware", self.font_ui)
        
        self.slot_culprit = Slot("", ox_term + 175, oy_term + 415, 120, 30, "Chefe", self.font_ui)
        self.slot_proof1 = Slot("", ox_term + 390, oy_term + 415, 200, 30, "Pendrive", self.font_ui)
        self.slot_proof2 = Slot("", ox_term + 390, oy_term + 470, 200, 30, "Celular", self.font_ui)
        
        self.investigation_slots = [
            self.slot_who, self.slot_how, self.slot_pwd, self.slot_where, self.slot_why,
            self.slot_culprit, self.slot_proof1, self.slot_proof2
        ]
        
        # Cria a instância da lógica de mundo
        self.world = World(self.font_ui, self.font_text, self.font_word)
        
        # Controle de estado do fluxo do motor
        self.rodando = True
        self.game_solved = False
        self.victory_alpha = 0
        self.hint_timer = 0
        
        # Carrega a imagem do menu
        self.menu_image = None
        try:
            self.menu_image = pygame.image.load(config.PATH_MENU).convert()
            self.menu_image_scaled = pygame.transform.scale(self.menu_image, (config.CANVAS_W, config.CANVAS_H))
        except Exception as e:
            print("Erro ao carregar imagem do menu:", e)
            self.menu_image_scaled = pygame.Surface((config.CANVAS_W, config.CANVAS_H))
            self.menu_image_scaled.fill(config.COLOR_BG)
            
        self.state = "MENU"  # Estados: "MENU", "CREDITS", "PLAYING"
        self.menu_hovered_btn = None  # None, "JOGAR", "CREDITOS", "SAIR"
        self.credits_hovered_btn = False  # se o botão de voltar em Créditos está hovered
        
        # Modo de depuração para hitboxes do Menu
        self.debug_mode = False
        self.selected_hotspot = None
        self.hotspot_moving = False
        self.hotspot_resizing = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # Hotspots do menu (JOGAR, CREDITOS, SAIR)
        default_menu_hotspots = [
            Hotspot("JOGAR", "Botao Jogar", pygame.Rect(384, 293, 256, 54)),
            Hotspot("CREDITOS", "Botao Creditos", pygame.Rect(384, 368, 256, 54)),
            Hotspot("SAIR", "Botao Sair", pygame.Rect(384, 444, 256, 54))
        ]
        
        self.menu_hotspots = []
        import json
        import os
        json_path = config.get_path("menu_hotspots_config.json")
        if os.path.exists(json_path):
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for item in data:
                    self.menu_hotspots.append(
                        Hotspot(item["name"], item["label"], pygame.Rect(item["x"], item["y"], item["w"], item["h"]))
                    )
                print(f"Loaded menu hotspots from {json_path}")
            except Exception as e:
                print("Failed to load menu_hotspots_config.json, using defaults:", e)
                self.menu_hotspots = default_menu_hotspots
        else:
            self.menu_hotspots = default_menu_hotspots

        # Inicializa o cursor de lupa customizado para os hotspots do jogo
        try:
            self.lupa_cursor = self.create_lupa_cursor()
        except Exception as e:
            print("Erro ao criar cursor de lupa:", e)
            self.lupa_cursor = pygame.SYSTEM_CURSOR_HAND

    def create_lupa_cursor(self):
        # Cria uma superfície 32x32 com canal alfa
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        
        # Desenha a lupa em estilo pixel art com cores harmônicas e tamanho ampliado
        # Borda preta externa para contraste e contorno
        pygame.draw.circle(surf, (0, 0, 0), (10, 10), 9, 2)
        # Borda verde brilhante (CRT Green)
        pygame.draw.circle(surf, (0, 230, 70), (10, 10), 8, 2)
        # Preenchimento de vidro translúcido
        pygame.draw.circle(surf, (0, 230, 70, 70), (10, 10), 6)
        
        # Cabo diagonal (estende-se de 15,15 a 28,28)
        # Contorno preto grosso do cabo
        pygame.draw.line(surf, (0, 0, 0), (15, 15), (28, 28), 5)
        # Miolo do cabo em cinza metálico/branco
        pygame.draw.line(surf, (220, 220, 220), (16, 16), (27, 27), 3)
        # Detalhe em ouro/âmbar na ponta do cabo
        pygame.draw.line(surf, (235, 195, 80), (24, 24), (27, 27), 3)
        
        # Retorna o cursor com o hotspot no centro da lente (10, 10)
        return pygame.cursors.Cursor((10, 10), surf)

    def draw_bag_icon(self, surface: pygame.Surface, x: int, y: int):
        # Alça da bolsa
        pygame.draw.rect(surface, (100, 75, 45), (x + 6, y + 2, 12, 4))
        pygame.draw.rect(surface, (25, 20, 15), (x + 8, y + 4, 8, 2))
        # Corpo
        pygame.draw.rect(surface, (135, 95, 55), (x + 2, y + 6, 20, 16))
        pygame.draw.rect(surface, (100, 75, 45), (x + 2, y + 20, 20, 2))
        # Aba
        pygame.draw.rect(surface, (100, 75, 45), (x + 4, y + 6, 16, 7))
        # Fivela dourada
        pygame.draw.rect(surface, (235, 195, 80), (x + 11, y + 11, 3, 3))

    def verificar_solucao(self) -> bool:
        # Verifica se os 6 primeiros slots de preenchimento obrigatório estão corretos
        for i in range(6):
            if not self.investigation_slots[i].correto():
                return False
                
        # Provas 1 e 2 são independentes de ordem
        p1 = self.investigation_slots[6].item.text if self.investigation_slots[6].item else None
        p2 = self.investigation_slots[7].item.text if self.investigation_slots[7].item else None
        
        provas_corretas = {"Pendrive", "Celular"}
        if p1 in provas_corretas and p2 in provas_corretas and p1 != p2:
            return True
        return False

    def handle_events(self):
        mouse_fisica = pygame.mouse.get_pos()
        
        # Mapeia coordenadas físicas da janela física para coordenadas virtuais (1024x800)
        mouse = (
            int((mouse_fisica[0] - self.ox) / self.scale_factor),
            int((mouse_fisica[1] - self.oy) / self.scale_factor)
        )
        
        # Detect hover over interactive elements to set hand/magnifier cursor
        hover_interactive = False
        hover_hotspot = False
        
        if self.state == "MENU":
            # Get hotspots from self.menu_hotspots
            hs_jogar = next((h for h in self.menu_hotspots if h.name == "JOGAR"), None)
            hs_creditos = next((h for h in self.menu_hotspots if h.name == "CREDITOS"), None)
            hs_sair = next((h for h in self.menu_hotspots if h.name == "SAIR"), None)
            
            rect_jogar = hs_jogar.rect if hs_jogar else pygame.Rect(384, 293, 256, 54)
            rect_creditos = hs_creditos.rect if hs_creditos else pygame.Rect(384, 368, 256, 54)
            rect_sair = hs_sair.rect if hs_sair else pygame.Rect(384, 444, 256, 54)
            
            if self.debug_mode:
                for hs in self.menu_hotspots:
                    if hs.rect.collidepoint(mouse):
                        hover_interactive = True
                        break
                    br_x = hs.rect.right
                    br_y = hs.rect.bottom
                    if abs(mouse[0] - br_x) < 15 and abs(mouse[1] - br_y) < 15:
                        hover_interactive = True
                        break
            else:
                if rect_jogar.collidepoint(mouse):
                    self.menu_hovered_btn = "JOGAR"
                    hover_interactive = True
                elif rect_creditos.collidepoint(mouse):
                    self.menu_hovered_btn = "CREDITOS"
                    hover_interactive = True
                elif rect_sair.collidepoint(mouse):
                    self.menu_hovered_btn = "SAIR"
                    hover_interactive = True
                else:
                    self.menu_hovered_btn = None
                
        elif self.state == "CREDITS":
            rect_voltar = pygame.Rect(384, 550, 256, 54)
            if rect_voltar.collidepoint(mouse):
                self.credits_hovered_btn = True
                hover_interactive = True
            else:
                self.credits_hovered_btn = False
                
        elif self.state == "PLAYING" and not self.game_solved:
            if not self.world.terminal_aberto and not self.world.zoom_overlay:
                abrir_terminal_rect = pygame.Rect(780, 25, 210, 45)
                if abrir_terminal_rect.collidepoint(mouse):
                    hover_interactive = True
            
            if self.world.zoom_overlay:
                if self.world.close_btn_rect.collidepoint(mouse):
                    hover_interactive = True
                for w_rect, clue_id in self.world.active_word_rects:
                    if w_rect.collidepoint(mouse):
                        hover_interactive = True
            elif self.world.terminal_aberto:
                if self.world.btn_voltar_terminal.collidepoint(mouse):
                    hover_interactive = True
                for tile in self.world.discovered_word_tiles:
                    if tile.rect.collidepoint(mouse):
                        hover_interactive = True
            else:
                # exploration
                for tile in self.world.discovered_word_tiles:
                    if tile.slot is None and tile.rect.collidepoint(mouse):
                        hover_interactive = True
                for hs in self.world.hotspots:
                    screen_hs_rect = pygame.Rect(hs.rect.x + self.world.play_offset_x, 
                                                 hs.rect.y + self.world.play_offset_y, 
                                                 hs.rect.width, hs.rect.height)
                    if screen_hs_rect.collidepoint(mouse):
                        hover_hotspot = True

        if hover_hotspot:
            pygame.mouse.set_cursor(self.lupa_cursor)
        elif hover_interactive:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.rodando = False
                
            elif event.type == pygame.VIDEORESIZE:
                self.screen_w = event.w
                self.screen_h = event.h
                self.tela = pygame.display.set_mode((self.screen_w, self.screen_h), pygame.RESIZABLE)
                self.scale_factor = min(self.screen_w / config.CANVAS_W, self.screen_h / config.CANVAS_H)
                self.canvas_w = int(config.CANVAS_W * self.scale_factor)
                self.canvas_h = int(config.CANVAS_H * self.scale_factor)
                self.ox = (self.screen_w - self.canvas_w) // 2
                self.oy = (self.screen_h - self.canvas_h) // 2

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "PLAYING":
                        if self.world.terminal_aberto:
                            self.world.terminal_aberto = False
                        elif self.world.zoom_overlay:
                            self.world.zoom_overlay = None
                        else:
                            self.state = "MENU"
                    elif self.state == "CREDITS":
                        self.state = "MENU"
                    elif self.state == "MENU":
                        self.rodando = False
                elif event.key == pygame.K_r and self.game_solved:
                    # Reinicia todo o estado da engine de jogo
                    self.__init__()
                    self.state = "PLAYING"
                elif event.key == pygame.K_d:
                    if self.state == "PLAYING":
                        # Ativa/Desativa modo de depuração para hitboxes
                        self.world.toggle_debug()
                    elif self.state == "MENU":
                        # Ativa/Desativa modo de depuração para o menu
                        self.toggle_debug()
                elif self.state == "CREDITS":
                    self.state = "MENU"
       
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.state == "MENU":
                    if self.debug_mode:
                        # Editor de hitboxes no menu
                        for hs in reversed(self.menu_hotspots):
                            if hs.rect.collidepoint(mouse):
                                self.selected_hotspot = hs
                                br_x = hs.rect.right
                                br_y = hs.rect.bottom
                                if abs(mouse[0] - br_x) < 15 and abs(mouse[1] - br_y) < 15:
                                    self.hotspot_resizing = True
                                else:
                                    self.hotspot_moving = True
                                    self.drag_offset_x = mouse[0] - hs.rect.x
                                    self.drag_offset_y = mouse[1] - hs.rect.y
                                break
                    else:
                        if self.menu_hovered_btn == "JOGAR":
                            self.state = "PLAYING"
                        elif self.menu_hovered_btn == "CREDITOS":
                            self.state = "CREDITS"
                        elif self.menu_hovered_btn == "SAIR":
                            self.rodando = False
                elif self.state == "CREDITS":
                    if self.credits_hovered_btn:
                        self.state = "MENU"
                elif self.state == "PLAYING":
                    if not self.game_solved:
                        if not self.world.terminal_aberto and not self.world.zoom_overlay:
                            abrir_terminal_rect = pygame.Rect(780, 25, 210, 45)
                            if abrir_terminal_rect.collidepoint(mouse):
                                self.world.terminal_aberto = True
                                continue
                        self.world.clicar(mouse)

            elif event.type == pygame.MOUSEBUTTONUP:
                if self.state == "MENU" and self.debug_mode:
                    if self.selected_hotspot:
                        self.selected_hotspot = None
                        self.hotspot_moving = False
                        self.hotspot_resizing = False
                        self.save_menu_hotspots()
                elif self.state == "PLAYING" and not self.game_solved:
                    self.world.soltar(self.investigation_slots)

            elif event.type == pygame.MOUSEMOTION:
                if self.state == "MENU" and self.debug_mode and self.selected_hotspot:
                    hs = self.selected_hotspot
                    if self.hotspot_resizing:
                        new_w = max(15, mouse[0] - hs.rect.x)
                        new_h = max(15, mouse[1] - hs.rect.y)
                        hs.rect.width = new_w
                        hs.rect.height = new_h
                    elif self.hotspot_moving:
                        new_x = mouse[0] - self.drag_offset_x
                        new_y = mouse[1] - self.drag_offset_y
                        hs.rect.x = max(0, min(config.CANVAS_W - hs.rect.width, new_x))
                        hs.rect.y = max(0, min(config.CANVAS_H - hs.rect.height, new_y))
                elif self.state == "PLAYING" and not self.game_solved:
                    self.world.mover(mouse)

    def toggle_debug(self):
        self.debug_mode = not self.debug_mode
        self.selected_hotspot = None
        self.hotspot_moving = False
        self.hotspot_resizing = False
        if self.debug_mode:
            print("--- MENU DEBUG MODE ENABLED ---")
            self.save_menu_hotspots()
        else:
            print("--- MENU DEBUG MODE DISABLED ---")

    def save_menu_hotspots(self):
        import json
        data = []
        for hs in self.menu_hotspots:
            data.append({
                "name": hs.name,
                "label": hs.label,
                "x": hs.rect.x,
                "y": hs.rect.y,
                "w": hs.rect.width,
                "h": hs.rect.height
            })
        try:
            json_path = config.get_path("menu_hotspots_config.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            print(f"Saved menu layout to {json_path}")
        except Exception as e:
            print("Failed to write to menu_hotspots_config.json:", e)

    def update(self):
        if self.state == "PLAYING":
            self.world.update()

    def draw_crt_effect(self, surface: pygame.Surface):
        # 1. Subtle scanlines (horizontal lines)
        if not hasattr(self, 'scanline_surf') or self.scanline_surf is None:
            self.scanline_surf = pygame.Surface((config.CANVAS_W, config.CANVAS_H), pygame.SRCALPHA)
            for y in range(0, config.CANVAS_H, 4):
                pygame.draw.line(self.scanline_surf, (0, 0, 0, 35), (0, y), (config.CANVAS_W, y))
        surface.blit(self.scanline_surf, (0, 0))
        
        # 2. Moving phosphor beam
        if not hasattr(self, 'beam_y'):
            self.beam_y = 0.0
        self.beam_y = (self.beam_y + 1.2) % config.CANVAS_H
        
        beam_surf = pygame.Surface((config.CANVAS_W, 30), pygame.SRCALPHA)
        beam_surf.fill((0, 230, 70, 6))
        surface.blit(beam_surf, (0, int(self.beam_y)))

    def draw_menu(self):
        # 1. Desenha o fundo do menu
        self.canvas.blit(self.menu_image_scaled, (0, 0))
        
        # 2. Destaque de hover nos botões
        if self.menu_hovered_btn and not self.debug_mode:
            # Encontra a hitbox correspondente
            hs = next((h for h in self.menu_hotspots if h.name == self.menu_hovered_btn), None)
            rect = hs.rect if hs else pygame.Rect(384, 293, 256, 54)
            
            # Preenchimento de hover
            glow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            glow_surf.fill((0, 230, 70, 25))
            self.canvas.blit(glow_surf, (rect.x, rect.y))
            # Borda brilhante
            pygame.draw.rect(self.canvas, (0, 255, 90), rect, 3)
            
        # 3. Efeito CRT
        self.draw_crt_effect(self.canvas)

        # 4. Desenha as hitboxes de debug se ativo
        if self.debug_mode:
            mouse_fisica = pygame.mouse.get_pos()
            mouse = (
                int((mouse_fisica[0] - self.ox) / self.scale_factor),
                int((mouse_fisica[1] - self.oy) / self.scale_factor)
            )
            self.draw_menu_debug_visuals(self.canvas, mouse)

    def draw_menu_debug_visuals(self, surface: pygame.Surface, mouse: tuple):
        # Texto das coordenadas do mouse no Menu
        m_text = self.font_ui.render(f"Mouse Menu: ({mouse[0]}, {mouse[1]})", True, config.COLOR_DEBUG_TEXT)
        surface.blit(m_text, (10, 10))
        
        # Linhas de grade
        if 0 <= mouse[0] <= config.CANVAS_W and 0 <= mouse[1] <= config.CANVAS_H:
            pygame.draw.line(surface, (80, 80, 80), (mouse[0], 0), (mouse[0], config.CANVAS_H), 1)
            pygame.draw.line(surface, (80, 80, 80), (0, mouse[1]), (config.CANVAS_W, mouse[1]), 1)
            
        # Desenha as hitboxes do menu
        for hs in self.menu_hotspots:
            if hs == self.selected_hotspot:
                box_color = config.COLOR_DEBUG_SELECTED_BOX
                border_color = config.COLOR_DEBUG_SELECTED_BORDER
            else:
                box_color = config.COLOR_DEBUG_BOX
                border_color = config.COLOR_DEBUG_BORDER
                
            hs_surf = pygame.Surface((hs.rect.width, hs.rect.height), pygame.SRCALPHA)
            hs_surf.fill(box_color)
            surface.blit(hs_surf, (hs.rect.x, hs.rect.y))
            pygame.draw.rect(surface, border_color, (hs.rect.x, hs.rect.y, hs.rect.width, hs.rect.height), 2)
            
            # Alça de redimensionamento no canto inferior direito
            pygame.draw.rect(surface, border_color, (hs.rect.right - 8, hs.rect.bottom - 8, 8, 8))
            
            # Texto explicativo
            specs = f"{hs.name}: ({hs.rect.x},{hs.rect.y},{hs.rect.width},{hs.rect.height})"
            spec_surf = self.font_word.render(specs, True, (255, 255, 255))
            bg_rect = pygame.Rect(hs.rect.x, hs.rect.y - 20, spec_surf.get_width() + 4, spec_surf.get_height() + 2)
            pygame.draw.rect(surface, (0, 0, 0), bg_rect)
            surface.blit(spec_surf, (hs.rect.x + 2, hs.rect.y - 19))

    def draw_credits(self):
        # Fundo CRT escuro
        self.canvas.fill(config.COLOR_CRT_BG)
        
        # Moldura de terminal
        pygame.draw.rect(self.canvas, config.COLOR_CRT_GREEN, (40, 40, config.CANVAS_W - 80, config.CANVAS_H - 80), 4)
        pygame.draw.rect(self.canvas, (0, 120, 40), (44, 44, config.CANVAS_W - 88, config.CANVAS_H - 88), 1)
        
        # Título
        tit_surf = self.font_title.render("CREDITOS DO JOGO", True, config.COLOR_CRT_GREEN)
        self.canvas.blit(tit_surf, (config.CANVAS_W // 2 - tit_surf.get_width() // 2, 70))
        pygame.draw.line(self.canvas, (0, 150, 45), (60, 130), (config.CANVAS_W - 60, 130), 2)
        
        c_green = config.COLOR_CRT_GREEN_MID
        c_green_lite = config.COLOR_CRT_GREEN_LITE
        
        credits_lines = [
            ("INVESTIGACAO SOC 2026: VAZAMENTO CRITICO", c_green_lite, True),
            ("", c_green, False),
            ("DESENVOLVIDO POR:", c_green_lite, False),
            ("Luc3nAg (GitHub: Luc3nAg/Jogo-Seguran-a)", c_green, False),
            ("", c_green, False),
            ("TECNOLOGIAS UTILIZADAS:", c_green_lite, False),
            ("Python 3 & Pygame Library", c_green, False),
            ("Pixel Art & Custom Retro GUI assets", c_green, False),
            ("", c_green, False),
            ("OBJETIVO PEDAGOGICO:", c_green_lite, False),
            ("Simular a analise forense de incidentes de seguranca,", c_green, False),
            ("compreendendo conceitos de senhas, malware, vazamento,", c_green, False),
            ("e correlacao de logs no contexto de seguranca da informacao.", c_green, False)
        ]
        
        sy = 160
        for line_text, color, is_bold in credits_lines:
            if line_text == "":
                sy += 15
                continue
            
            font = self.font_title if is_bold else self.font_text
            text_surf = font.render(line_text, True, color)
            self.canvas.blit(text_surf, (config.CANVAS_W // 2 - text_surf.get_width() // 2, sy))
            sy += 30
            
        # Botão Voltar
        rect_voltar = pygame.Rect(384, 550, 256, 54)
        bg_btn = config.COLOR_CRT_BG_BUTTON
        border_color = config.COLOR_CRT_GREEN
        if self.credits_hovered_btn:
            bg_btn = (0, 75, 25)
            border_color = (0, 255, 90)
            
            glow_surf = pygame.Surface((rect_voltar.width, rect_voltar.height), pygame.SRCALPHA)
            glow_surf.fill((0, 255, 70, 25))
            self.canvas.blit(glow_surf, (rect_voltar.x, rect_voltar.y))
            
        pygame.draw.rect(self.canvas, bg_btn, rect_voltar)
        pygame.draw.rect(self.canvas, border_color, rect_voltar, 3)
        
        btn_text = self.font_ui.render("VOLTAR AO MENU", True, border_color)
        self.canvas.blit(btn_text, (rect_voltar.centerx - btn_text.get_width() // 2, rect_voltar.centery - btn_text.get_height() // 2))
        
        # Efeito CRT
        self.draw_crt_effect(self.canvas)

    def draw(self):
        # Limpa o canvas lógico
        self.canvas.fill(config.COLOR_BG)
        
        if self.state == "MENU":
            self.draw_menu()
        elif self.state == "CREDITS":
            self.draw_credits()
        elif self.state == "PLAYING":
            # Título principal do jogo
            title_surf = self.font_title.render("VAZAMENTO CRITICO", True, config.COLOR_AMBER)
            title_rect = title_surf.get_rect(centerx=config.CANVAS_W // 2, top=15)
            self.canvas.blit(title_surf, title_rect)
            
            # Placa do contador de pistas coletadas
            pygame.draw.rect(self.canvas, config.COLOR_SHELF_BORDER, (35, 25, 190, 45))
            pygame.draw.rect(self.canvas, config.COLOR_ZOOM_BORDER, (35, 25, 190, 45), 2)
            self.draw_bag_icon(self.canvas, 45, 35)
            clues_count = len(self.world.discovered_words)
            clues_surf = self.font_ui.render(f"PISTAS: {clues_count}/16", True, config.COLOR_AMBER)
            self.canvas.blit(clues_surf, (78, 38))
    
            # Botão abrir terminal de sentenças
            if not self.world.terminal_aberto and not self.game_solved:
                abrir_terminal_rect = pygame.Rect(780, 25, 210, 45)
                pygame.draw.rect(self.canvas, config.COLOR_CRT_BG_BUTTON, abrir_terminal_rect)
                pygame.draw.rect(self.canvas, config.COLOR_CRT_GREEN, abrir_terminal_rect, 2)
                term_btn_surf = self.font_ui.render("ABRIR TERMINAL", True, config.COLOR_CRT_GREEN)
                self.canvas.blit(term_btn_surf, (abrir_terminal_rect.centerx - term_btn_surf.get_width()//2, abrir_terminal_rect.centery - term_btn_surf.get_height()//2))
    
            # Linha separadora do menu superior
            pygame.draw.line(self.canvas, config.COLOR_SHELF_BORDER, (0, 115), (config.CANVAS_W, 115), 3)
    
            # Instruções na tela principal do SOC
            if not self.world.terminal_aberto and not self.game_solved:
                main_instr = self.font_ui.render("Investigue a sala do SOC. Colete 15 pistas e abra o Terminal para resolver o caso.", True, (220, 195, 140))
                self.canvas.blit(main_instr, (config.CANVAS_W // 2 - main_instr.get_width() // 2, 80))
    
            # Renderiza a área de visualização e objetos do cenário
            self.world.draw(self.canvas)
    
            # Elementos de interface do Terminal de sentenças
            if self.world.terminal_aberto and not self.game_solved:
                for slot in self.investigation_slots:
                    slot.draw(self.canvas)
                    
                slots_filled = all(s.item is not None for s in self.investigation_slots)
                if slots_filled:
                    if self.verificar_solucao():
                        self.game_solved = True
                    else:
                        self.hint_timer += 1
                        if (self.hint_timer // 20) % 2 == 0:
                            hint_surf = self.font_ui.render("> ACESSO NEGADO: Parâmetros incorretos. Verifique as evidências.", True, (255, 70, 60))
                            self.canvas.blit(hint_surf, (config.CANVAS_W // 2 - hint_surf.get_width() // 2, config.TERM_Y + 52))
                else:
                    instr_surf = self.font_ui.render("> Arraste as pistas do rodapé para as caixas de parâmetros.", True, config.COLOR_CRT_GREEN)
                    self.canvas.blit(instr_surf, (config.CANVAS_W // 2 - instr_surf.get_width() // 2, config.TERM_Y + 52))
    
            # Desenha a moldura da viewport de jogo
            pygame.draw.rect(self.canvas, (65, 45, 30), (104, 112, 816, 616), 8)
            pygame.draw.rect(self.canvas, (100, 75, 55), (108, 116, 808, 608), 2)
            pygame.draw.rect(self.canvas, (35, 22, 15), (103, 111, 818, 618), 1)
    
            # Rodapé / Shelf
            pygame.draw.rect(self.canvas, config.COLOR_SHELF_BG, (0, 730, config.CANVAS_W, 70))
            pygame.draw.line(self.canvas, config.COLOR_SHELF_BORDER, (0, 730), (config.CANVAS_W, 730), 4)
    
            # Desenha as pistas coletadas (esconde as que estão nos slots do terminal se o terminal estiver fechado)
            for tile in self.world.discovered_word_tiles:
                if not tile.arrastando:
                    if self.world.terminal_aberto or tile.slot is None:
                        tile.draw(self.canvas)
    
            # Pista em arrasto na camada superior
            if self.world.obj_selecionado:
                self.world.obj_selecionado.draw(self.canvas)
    
            # Tela final de vitória (Caso Resolvido)
            if self.game_solved:
                if self.victory_alpha < 235:
                    self.victory_alpha += 5
                    
                victory_mask = pygame.Surface((config.CANVAS_W, config.CANVAS_H), pygame.SRCALPHA)
                victory_mask.fill((5, 15, 8, self.victory_alpha))
                self.canvas.blit(victory_mask, (0, 0))
                
                px, py, pw, ph = 162, 130, 700, 540
                pygame.draw.rect(self.canvas, (2, 12, 6), (px, py, pw, ph))
                pygame.draw.rect(self.canvas, config.COLOR_CRT_GREEN, (px, py, pw, ph), 4)
                
                vic_title = self.font_title.render("CASO RESOLVIDO!", True, (0, 255, 100))
                self.canvas.blit(vic_title, (px + pw // 2 - vic_title.get_width() // 2, py + 30))
                
                sy = py + 95
                for line in config.STORY_LINES:
                    line_surf = self.font_victory.render(line, True, (200, 255, 210))
                    self.canvas.blit(line_surf, (px + pw // 2 - line_surf.get_width() // 2, sy))
                    sy += 26
                    
                restart_surf = self.font_ui.render("Pressione ESC para sair ou R para reiniciar a investigacao", True, (0, 180, 60))
                self.canvas.blit(restart_surf, (px + pw // 2 - restart_surf.get_width() // 2, py + ph - 40))

        # Renderiza o canvas lógico escalado centralizado na tela
        scaled_canvas = pygame.transform.scale(self.canvas, (self.canvas_w, self.canvas_h))
        self.tela.fill((0, 0, 0))
        self.tela.blit(scaled_canvas, (self.ox, self.oy))
        pygame.display.flip()

    def run(self):
        while self.rodando:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()
