import pygame
from src import config
from src.models.hotspot import Hotspot
from src.models.word_tile import WordTile

class World:
    """
    Gerencia o estado do cenário do jogo, os hotspots interativos,
    as overlays de zoom e as interações com o mouse.
    """
    def __init__(self, font_ui: pygame.font.Font, font_text: pygame.font.Font, font_word: pygame.font.Font):
        self.font_ui = font_ui
        self.font_text = font_text
        self.font_word = font_word
        
        # Posição de offset para centralizar a área de jogo 800x600 no canvas 1024x800
        self.play_offset_x = config.PLAY_OFFSET_X
        self.play_offset_y = config.PLAY_OFFSET_Y
        
        # Carrega o cenário de fundo
        try:
            self.background = pygame.image.load(config.PATH_BG).convert()
            if self.background.get_size() != (config.PLAY_W, config.PLAY_H):
                self.background = pygame.transform.scale(self.background, (config.PLAY_W, config.PLAY_H))
        except Exception as e:
            self.background = pygame.Surface((config.PLAY_W, config.PLAY_H))
            self.background.fill((40, 40, 40))
            print("Erro ao carregar imagem de cenário de fundo:", e)
            
        # Carrega os sprites animados do Chefe
        self.boss_frames = []
        self.boss_zoom = None
        try:
            for i in range(1, 11):
                img = pygame.image.load(config.PATH_SPRITES_BOSS.format(i=i)).convert_alpha()
                if img.get_at((0, 0))[:3] == (0, 0, 0):
                    img.set_colorkey((0, 0, 0))
                self.boss_frames.append(img)
            if self.boss_frames:
                self.boss_zoom = pygame.transform.scale(self.boss_frames[0], (200, 208))
            print(f"Loaded {len(self.boss_frames)} frames for boss.")
        except Exception as e:
            print("Failed to load boss anim frames:", e)

        # Carrega os sprites animados do Estagiário
        self.estagiario_frames = []
        try:
            for i in range(1, 3):
                img = pygame.image.load(config.PATH_SPRITES_INTERN.format(i=i)).convert_alpha()
                if img.get_at((0, 0))[:3] == (0, 0, 0):
                    img.set_colorkey((0, 0, 0))
                self.estagiario_frames.append(img)
            print(f"Loaded {len(self.estagiario_frames)} frames for estagiario.")
        except Exception as e:
            print("Erro ao carregar sprites do estagiario:", e)
            
        # Carrega sprites adicionais de objetos e ícones
        try:
            self.pendrive_image = pygame.image.load(config.PATH_PENDRIVE).convert_alpha()
        except Exception as e:
            self.pendrive_image = None
            print("Erro ao carregar pendrive.png:", e)
            
        try:
            self.notepad_image = pygame.image.load(config.PATH_NOTEPAD).convert_alpha()
        except Exception as e:
            self.notepad_image = None
            print("Erro ao carregar bloc_de_notas.png:", e)

        try:
            self.icon_boss = pygame.image.load(config.PATH_ICON_BOSS).convert_alpha()
        except Exception as e:
            self.icon_boss = None
            print("Erro ao carregar icone chefe.png:", e)

        try:
            self.icon_drawer = pygame.image.load(config.PATH_ICON_DRAWER).convert_alpha()
        except Exception as e:
            self.icon_drawer = None
            print("Erro ao carregar gaveta cheia.png:", e)
            
        # Hitboxes configuradas de acordo com o cenário devs e o roteiro (depuração do usuário)
        self.hotspots = [
            Hotspot("gaveta", "Gaveta do Chefe", pygame.Rect(12, 428, 56, 93)),
            Hotspot("bulletin_board", "Quadro Kanban", pygame.Rect(463, 188, 146, 143)),
            Hotspot("estagiario", "Estagiario (Acusado)", pygame.Rect(618, 320, 149, 213)),
            Hotspot("postit", "Post-it no Bloco de Notas", pygame.Rect(85, 308, 45, 41)),
            Hotspot("veteran", "Chefe Furioso", pygame.Rect(263, 294, 190, 240)),
            Hotspot("logs_de_acesso", "Logs de Acesso (PC do Chefe)", pygame.Rect(29, 350, 66, 59)),
            Hotspot("clock", "Relogio de Parede", pygame.Rect(639, 126, 100, 119)),
        ]
        
        # Configurações dinâmicas de overlay
        self.overlays_data = config.OVERLAYS_DATA
        
        # Estados internos
        self.zoom_overlay = None
        self.terminal_aberto = False
        self.debug_mode = False
        self.selected_hotspot = None
        self.hotspot_moving = False
        self.hotspot_resizing = False
        
        self.discovered_words = []
        self.discovered_word_tiles = []
        
        self.obj_selecionado = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        
        # Botões de interface no canvas lógico
        self.close_btn_rect = pygame.Rect(820, 165, 30, 30)
        self.btn_voltar_terminal = pygame.Rect(450, 595, 124, 35)
        
        self.active_word_rects = []

    def toggle_debug(self):
        self.debug_mode = not self.debug_mode
        self.selected_hotspot = None
        self.hotspot_moving = False
        self.hotspot_resizing = False
        if self.debug_mode:
            print("--- DEBUG MODE ENABLED ---")
            self.print_hotspots_code()
        else:
            print("--- DEBUG MODE DISABLED ---")

    def print_hotspots_code(self):
        code_lines = [
            "# COPY-PASTE THIS BLOCK INTO Mundo.py INSIDE self.hotspots LIST:",
            "        self.hotspots = ["
        ]
        for hs in self.hotspots:
            code_lines.append(f'            Hotspot("{hs.name}", "{hs.label}", pygame.Rect({hs.rect.x}, {hs.rect.y}, {hs.rect.width}, {hs.rect.height})),')
        code_lines.append("        ]")
        
        code_text = "\n".join(code_lines)
        print("\nUpdated Hotspots Layout:")
        print(code_text)
        print("------------------------\n")
        
        try:
            with open("hotspots_config.txt", "w") as f:
                f.write(code_text)
        except Exception as e:
            print("Failed to write to hotspots_config.txt:", e)

    def draw_kanban_board(self, surface: pygame.Surface, rect: pygame.Rect):
        rx = rect.x + self.play_offset_x
        ry = rect.y + self.play_offset_y
        rw = rect.width
        rh = rect.height
        
        # Placa traseira do quadro Kanban
        pygame.draw.rect(surface, (20, 15, 10), (rx + 3, ry + 3, rw, rh))
        pygame.draw.rect(surface, (80, 55, 35), (rx, ry, rw, rh))
        pygame.draw.rect(surface, (230, 225, 215), (rx + 4, ry + 4, rw - 8, rh - 8))
        
        # Colunas
        col_w = (rw - 8) // 3
        pygame.draw.line(surface, (170, 165, 155), (rx + 4 + col_w, ry + 4), (rx + 4 + col_w, ry + rh - 4), 1)
        pygame.draw.line(surface, (170, 165, 155), (rx + 4 + 2 * col_w, ry + 4), (rx + 4 + 2 * col_w, ry + rh - 4), 1)
        
        # Títulos das colunas
        pygame.draw.rect(surface, (100, 100, 100), (rx + 8, ry + 8, col_w - 8, 4))
        pygame.draw.rect(surface, (100, 100, 100), (rx + 4 + col_w + 4, ry + 8, col_w - 8, 4))
        pygame.draw.rect(surface, (100, 100, 100), (rx + 4 + 2 * col_w + 4, ry + 8, col_w - 8, 4))
        
        # Cards Kanban coloridos (Post-its)
        # Coluna A Fazer (Esquerda)
        pygame.draw.rect(surface, (235, 215, 80), (rx + 10, ry + 18, 12, 10))
        pygame.draw.rect(surface, (235, 100, 120), (rx + 25, ry + 22, 12, 10))
        pygame.draw.rect(surface, (235, 215, 80), (rx + 12, ry + 36, 12, 10))
        # Coluna Em Progresso (Meio)
        pygame.draw.rect(surface, (100, 205, 120), (rx + 4 + col_w + 6, ry + 16, 12, 10))
        pygame.draw.rect(surface, (100, 170, 220), (rx + 4 + col_w + 20, ry + 28, 12, 10))
        # Coluna Concluído (Direita)
        pygame.draw.rect(surface, (235, 215, 80), (rx + 4 + 2 * col_w + 8, ry + 15, 12, 10))
        pygame.draw.rect(surface, (100, 205, 120), (rx + 4 + 2 * col_w + 22, ry + 18, 12, 10))
        pygame.draw.rect(surface, (235, 215, 80), (rx + 4 + 2 * col_w + 12, ry + 32, 12, 10))

    def update(self):
        for tile in self.discovered_word_tiles:
            tile.update()

    def draw(self, surface: pygame.Surface):
        # 1. Desenha a sala de SOC retro
        surface.blit(self.background, (self.play_offset_x, self.play_offset_y))
        
        # 2. Desenha o Kanban
        kanban_hs = next((h for h in self.hotspots if h.name == "bulletin_board"), None)
        if kanban_hs:
            self.draw_kanban_board(surface, kanban_hs.rect)
            
        # 3. Desenha o Chefe animado (baseado na hitbox do Veterano)
        if self.boss_frames:
            vet_hs = next((h for h in self.hotspots if h.name == "veteran"), None)
            if vet_hs:
                frame_idx = (pygame.time.get_ticks() // 100) % len(self.boss_frames)
                boss_surf = pygame.transform.scale(self.boss_frames[frame_idx], (vet_hs.rect.width, vet_hs.rect.height))
                surface.blit(boss_surf, (vet_hs.rect.x + self.play_offset_x, vet_hs.rect.y + self.play_offset_y))
                
        # 4. Desenha o Estagiário animado (baseado na hitbox do Estagiário)
        if self.estagiario_frames:
            estag_hs = next((h for h in self.hotspots if h.name == "estagiario"), None)
            if estag_hs:
                frame_idx = (pygame.time.get_ticks() // 300) % len(self.estagiario_frames)
                estag_surf = pygame.transform.scale(self.estagiario_frames[frame_idx], (estag_hs.rect.width, estag_hs.rect.height))
                surface.blit(estag_surf, (estag_hs.rect.x + self.play_offset_x, estag_hs.rect.y + self.play_offset_y))
                
        # 5. Desenha a Gaveta se houver imagem (opcional)
        if self.pendrive_image:
            pen_hs = next((h for h in self.hotspots if h.name == "gaveta"), None)
            if pen_hs:
                pen_surf = pygame.transform.scale(self.pendrive_image, (pen_hs.rect.width, pen_hs.rect.height))
                surface.blit(pen_surf, (pen_hs.rect.x + self.play_offset_x, pen_hs.rect.y + self.play_offset_y))
                
        # 6. Desenha o Bloco de Notas (bloc_de_notas.png)
        if self.notepad_image:
            bn_hs = next((h for h in self.hotspots if h.name == "postit"), None)
            if bn_hs:
                np_surf = pygame.transform.scale(self.notepad_image, (bn_hs.rect.width, bn_hs.rect.height))
                surface.blit(np_surf, (bn_hs.rect.x + self.play_offset_x, bn_hs.rect.y + self.play_offset_y))
        
        # 7. Desenha Destaques ao passar o mouse por cima
        if not self.zoom_overlay and not self.terminal_aberto and not self.debug_mode:
            for hs in self.hotspots:
                if hs.hovered:
                    # Preenchimento translúcido
                    highlight_surf = pygame.Surface((hs.rect.width, hs.rect.height), pygame.SRCALPHA)
                    highlight_surf.fill(config.COLOR_HOVER_FILL)
                    surface.blit(highlight_surf, (hs.rect.x + self.play_offset_x, hs.rect.y + self.play_offset_y))
                    
                    # Contorno
                    pygame.draw.rect(surface, config.COLOR_HOVER_BORDER, 
                                     (hs.rect.x + self.play_offset_x, hs.rect.y + self.play_offset_y, hs.rect.width, hs.rect.height), 2)
                    
                    # Tooltip informativa
                    tooltip = self.font_ui.render(hs.label, True, (255, 255, 255))
                    shadow = self.font_ui.render(hs.label, True, (0, 0, 0))
                    tx = hs.rect.centerx + self.play_offset_x - tooltip.get_width() // 2
                    ty = hs.rect.y + self.play_offset_y - 25
                    surface.blit(shadow, (tx + 1, ty + 1))
                    surface.blit(tooltip, (tx, ty))

        # 8. Desenha a overlay de zoom ativa
        if self.zoom_overlay:
            self.draw_zoom_overlay(surface)

        # 9. Desenha o Terminal de Dedução
        if self.terminal_aberto:
            self.draw_terminal_overlay(surface)

        # 10. Desenha Visualização de Debug (se ativado)
        if self.debug_mode:
            self.draw_debug_visuals(surface)

    def draw_zoom_overlay(self, surface: pygame.Surface):
        # Máscara escura do fundo
        dark_overlay = pygame.Surface((config.PLAY_W, config.PLAY_H), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 185))
        surface.blit(dark_overlay, (self.play_offset_x, self.play_offset_y))
        
        # Caixa de Zoom Central
        ox, oy, ow, oh = 162, 150, 700, 460
        pygame.draw.rect(surface, config.COLOR_ZOOM_BG_SHADOW, (ox + 4, oy + 4, ow, oh))
        pygame.draw.rect(surface, config.COLOR_ZOOM_BG, (ox, oy, ow, oh))
        pygame.draw.rect(surface, config.COLOR_ZOOM_BORDER, (ox, oy, ow, oh), 6)
        pygame.draw.rect(surface, config.COLOR_ZOOM_INNER_BORDER, (ox + 4, oy + 4, ow - 8, oh - 8), 2)
        
        data = self.overlays_data.get(self.zoom_overlay)
        if data:
            # Título do zoom em amarelo/âmbar
            title_surf = self.font_ui.render(data["title"], True, config.COLOR_AMBER)
            surface.blit(title_surf, (ox + 25, oy + 20))
            
            pygame.draw.line(surface, config.COLOR_ZOOM_BORDER, (ox + 20, oy + 50), (ox + ow - 20, oy + 50), 2)
            
            self.active_word_rects = []
            
            start_y = oy + 80
            line_height = 40
            
            # Renderiza as linhas de texto da caixa de zoom
            for line_idx, line in enumerate(data["lines"]):
                current_x = ox + 35
                current_y = start_y + (line_idx * line_height)
                
                for part in line:
                    text_str, clue_id = part
                    
                    if clue_id:
                        is_discovered = clue_id in self.discovered_words
                        
                        # Palavras colecionáveis: destacadas ou cinza se já coletadas
                        if is_discovered:
                            color = (95, 85, 75)
                            border_color = (60, 55, 50)
                            bg_color = (25, 20, 15)
                        else:
                            color = config.COLOR_AMBER_LITE
                            border_color = config.COLOR_AMBER
                            bg_color = (55, 42, 28)
                            
                        word_surf = self.font_text.render(text_str, True, color)
                        ww = word_surf.get_width() + 12
                        wh = word_surf.get_height() + 8
                        
                        w_rect = pygame.Rect(current_x, current_y - 4, ww, wh)
                        pygame.draw.rect(surface, bg_color, w_rect)
                        pygame.draw.rect(surface, border_color, w_rect, 1)
                        surface.blit(word_surf, (current_x + 6, current_y))
                        
                        if not is_discovered:
                            self.active_word_rects.append((w_rect, clue_id))
                            
                        current_x += ww + 8
                    else:
                        text_surf = self.font_text.render(text_str, True, config.COLOR_TEXT_WHITE)
                        surface.blit(text_surf, (current_x, current_y))
                        current_x += text_surf.get_width()
                        
            # Renderiza retratos de Zoom
            if self.zoom_overlay == "veteran":
                if self.icon_boss:
                    boss_icon_scaled = pygame.transform.scale(self.icon_boss, (150, 150))
                    surface.blit(boss_icon_scaled, (ox + 480, oy + 110))
                elif self.boss_zoom:
                    surface.blit(self.boss_zoom, (ox + 450, oy + 110))
            elif self.zoom_overlay == "estagiario" and self.estagiario_frames:
                estag_zoom = pygame.transform.scale(self.estagiario_frames[0], (150, 200))
                surface.blit(estag_zoom, (ox + 480, oy + 110))
            elif self.zoom_overlay == "gaveta" and self.icon_drawer:
                drawer_icon_scaled = pygame.transform.scale(self.icon_drawer, (150, 150))
                surface.blit(drawer_icon_scaled, (ox + 480, oy + 110))
                         
        # Botão Fechar ("X")
        pygame.draw.rect(surface, config.COLOR_CLOSE_RED, self.close_btn_rect)
        pygame.draw.rect(surface, config.COLOR_CLOSE_RED_BORDER, self.close_btn_rect, 2)
        x_surf = self.font_ui.render("X", True, (255, 255, 255))
        surface.blit(x_surf, (self.close_btn_rect.centerx - x_surf.get_width()//2, self.close_btn_rect.centery - x_surf.get_height()//2))

    def draw_terminal_overlay(self, surface: pygame.Surface):
        # Escurecimento CRT
        dark_overlay = pygame.Surface((config.PLAY_W, config.PLAY_H), pygame.SRCALPHA)
        dark_overlay.fill((0, 0, 0, 210))
        surface.blit(dark_overlay, (self.play_offset_x, self.play_offset_y))
        
        ox, oy, ow, oh = 192, 140, 640, 520
        
        # Fundo CRT Verde Fosco
        pygame.draw.rect(surface, config.COLOR_CRT_BG, (ox, oy, ow, oh))
        pygame.draw.rect(surface, config.COLOR_CRT_GREEN, (ox, oy, ow, oh), 4)
        pygame.draw.rect(surface, (0, 120, 40), (ox + 4, oy + 4, ow - 8, oh - 8), 1)
        
        # Cabeçalho do Terminal
        tit_surf = self.font_ui.render(" TERMINAL DE RESOLUCAO DE INCIDENTES - SOC ", True, config.COLOR_CRT_GREEN)
        surface.blit(tit_surf, (ox + ow//2 - tit_surf.get_width()//2, oy + 15))
        pygame.draw.line(surface, (0, 150, 45), (ox + 10, oy + 40), (ox + ow - 10, oy + 40), 2)
        
        c_green = config.COLOR_CRT_GREEN_MID
        
        # Linhas de Texto Fixas (para encaixar os slots de dedução de forma alinhada)
        # Linha 1 (Y = oy + 75)
        surface.blit(self.font_text.render("O", True, c_green), (ox + 30, oy + 75))
        surface.blit(self.font_text.render("nao vazou os dados.", True, c_green), (ox + 205, oy + 75))
        
        # Linha 2 (Y = oy + 120)
        surface.blit(self.font_text.render("O ataque ocorreu porque o", True, c_green), (ox + 30, oy + 120))
        
        # Linha 3 (Y = oy + 165)
        surface.blit(self.font_text.render("usou a senha", True, c_green), (ox + 30, oy + 165))
        
        # Linha 4 (Y = oy + 210)
        surface.blit(self.font_text.render("para acessar o", True, c_green), (ox + 30, oy + 210))
        
        # Linha 5 (Y = oy + 255)
        surface.blit(self.font_text.render("e instalar o", True, c_green), (ox + 30, oy + 255))
        surface.blit(self.font_text.render(".", True, c_green), (ox + 445, oy + 255))
        
        # Linha Divisória
        pygame.draw.line(surface, (0, 150, 45), (ox + 10, oy + 295), (ox + ow - 10, oy + 295), 2)
        
        # Título de Dedução de Culpabilidade
        ev_title = self.font_ui.render(" QUADRO DE DEDUCAO E PROVAS: ", True, config.COLOR_CRT_GREEN)
        surface.blit(ev_title, (ox + 15, oy + 310))
        
        # Linha 6 (Y = oy + 355)
        surface.blit(self.font_text.render("Culpado:", True, c_green), (ox + 30, oy + 355))
        surface.blit(self.font_text.render("Provas:", True, c_green), (ox + 255, oy + 355))
        
        # Linha 7 (Y = oy + 400)
        surface.blit(self.font_text.render("e", True, c_green), (ox + 315, oy + 400))
        surface.blit(self.font_text.render(".", True, c_green), (ox + 545, oy + 400))
        
        # Botão Voltar
        pygame.draw.rect(surface, config.COLOR_CRT_BG_BUTTON, self.btn_voltar_terminal)
        pygame.draw.rect(surface, config.COLOR_CRT_GREEN, self.btn_voltar_terminal, 2)
        v_surf = self.font_ui.render("VOLTAR", True, config.COLOR_CRT_GREEN)
        surface.blit(v_surf, (self.btn_voltar_terminal.centerx - v_surf.get_width()//2, self.btn_voltar_terminal.centery - v_surf.get_height()//2))

    def draw_debug_visuals(self, surface: pygame.Surface):
        m_pos = pygame.mouse.get_pos()
        local_mx = m_pos[0] - self.play_offset_x
        local_my = m_pos[1] - self.play_offset_y
        m_text = self.font_ui.render(f"Mouse: ({local_mx}, {local_my})", True, config.COLOR_DEBUG_TEXT)
        surface.blit(m_text, (self.play_offset_x + 10, self.play_offset_y + 10))
        
        # Linhas de grade do mouse
        if 0 <= local_mx <= config.PLAY_W and 0 <= local_my <= config.PLAY_H:
            pygame.draw.line(surface, (80, 80, 80), (m_pos[0], self.play_offset_y), (m_pos[0], self.play_offset_y + config.PLAY_H), 1)
            pygame.draw.line(surface, (80, 80, 80), (self.play_offset_x, m_pos[1]), (self.play_offset_x + config.PLAY_W, m_pos[1]), 1)

        # Desenha as bordas e informações de todas as hitboxes
        for hs in self.hotspots:
            hs_x = hs.rect.x + self.play_offset_x
            hs_y = hs.rect.y + self.play_offset_y
            
            if hs == self.selected_hotspot:
                box_color = config.COLOR_DEBUG_SELECTED_BOX
                border_color = config.COLOR_DEBUG_SELECTED_BORDER
            else:
                box_color = config.COLOR_DEBUG_BOX
                border_color = config.COLOR_DEBUG_BORDER
                
            hs_surf = pygame.Surface((hs.rect.width, hs.rect.height), pygame.SRCALPHA)
            hs_surf.fill(box_color)
            surface.blit(hs_surf, (hs_x, hs_y))
            pygame.draw.rect(surface, border_color, (hs_x, hs_y, hs.rect.width, hs.rect.height), 2)
            pygame.draw.rect(surface, border_color, (hs_x + hs.rect.width - 8, hs_y + hs.rect.height - 8, 8, 8))
            
            # Texto da hitbox
            specs = f"{hs.name}: ({hs.rect.x},{hs.rect.y},{hs.rect.width},{hs.rect.height})"
            spec_surf = self.font_word.render(specs, True, (255, 255, 255))
            bg_rect = pygame.Rect(hs_x, hs_y - 20, spec_surf.get_width() + 4, spec_surf.get_height() + 2)
            pygame.draw.rect(surface, (0, 0, 0), bg_rect)
            surface.blit(spec_surf, (hs_x + 2, hs_y - 19))

    def clicar(self, pos: tuple) -> bool:
        if self.debug_mode:
            # Edição das hitboxes em modo de debug
            for hs in reversed(self.hotspots):
                screen_hs_rect = pygame.Rect(hs.rect.x + self.play_offset_x, 
                                             hs.rect.y + self.play_offset_y, 
                                             hs.rect.width, hs.rect.height)
                if screen_hs_rect.collidepoint(pos):
                    self.selected_hotspot = hs
                    br_x = screen_hs_rect.right
                    br_y = screen_hs_rect.bottom
                    if abs(pos[0] - br_x) < 15 and abs(pos[1] - br_y) < 15:
                        self.hotspot_resizing = True
                    else:
                        self.hotspot_moving = True
                        self.drag_offset_x = pos[0] - (hs.rect.x + self.play_offset_x)
                        self.drag_offset_y = pos[1] - (hs.rect.y + self.play_offset_y)
                    return True
            return False

        # 1. Interação com overlay de Zoom
        if self.zoom_overlay:
            if self.close_btn_rect.collidepoint(pos):
                self.zoom_overlay = None
                return True
                
            for w_rect, clue_id in self.active_word_rects:
                if w_rect.collidepoint(pos):
                    self.discover_clue(clue_id)
                    return True
            return True

        # 2. Interação com Terminal de Sentenças Aberto
        if self.terminal_aberto:
            if self.btn_voltar_terminal.collidepoint(pos):
                self.terminal_aberto = False
                return True
                
            for tile in reversed(self.discovered_word_tiles):
                if tile.rect.collidepoint(pos):
                    self.obj_selecionado = tile
                    tile.arrastando = True
                    if tile.slot:
                        tile.slot.item = None
                        tile.slot = None
                    self.drag_offset_x = pos[0] - tile.x
                    self.drag_offset_y = pos[1] - tile.y
                    self.discovered_word_tiles.remove(tile)
                    self.discovered_word_tiles.append(tile)
                    return True
            return True
            
        # 3. Modo exploração normal: Clique sobre palavras na estante ou hotspots (pistas já encaixadas são protegidas)
        for tile in reversed(self.discovered_word_tiles):
            if tile.slot is None and tile.rect.collidepoint(pos):
                self.obj_selecionado = tile
                tile.arrastando = True
                self.drag_offset_x = pos[0] - tile.x
                self.drag_offset_y = pos[1] - tile.y
                self.discovered_word_tiles.remove(tile)
                self.discovered_word_tiles.append(tile)
                return True
                
        for hs in self.hotspots:
            screen_hs_rect = pygame.Rect(hs.rect.x + self.play_offset_x, 
                                         hs.rect.y + self.play_offset_y, 
                                         hs.rect.width, hs.rect.height)
            if screen_hs_rect.collidepoint(pos):
                self.zoom_overlay = hs.name
                return True
                
        return False

    def mover(self, pos: tuple):
        if self.debug_mode and self.selected_hotspot:
            # Move ou redimensiona hitboxes no modo debug
            hs = self.selected_hotspot
            local_x = pos[0] - self.play_offset_x
            local_y = pos[1] - self.play_offset_y
            if self.hotspot_resizing:
                new_w = max(15, local_x - hs.rect.x)
                new_h = max(15, local_y - hs.rect.y)
                hs.rect.width = new_w
                hs.rect.height = new_h
            elif self.hotspot_moving:
                new_x = pos[0] - self.play_offset_x - self.drag_offset_x
                new_y = pos[1] - self.play_offset_y - self.drag_offset_y
                hs.rect.x = max(0, min(config.PLAY_W - hs.rect.width, new_x))
                hs.rect.y = max(0, min(config.PLAY_H - hs.rect.height, new_y))
            return

        # Arrasto de WordTiles
        if self.obj_selecionado:
            self.obj_selecionado.x = pos[0] - self.drag_offset_x
            self.obj_selecionado.y = pos[1] - self.drag_offset_y
            self.obj_selecionado.update()
        else:
            # Atualiza estado hovered dos hotspots na exploração
            for hs in self.hotspots:
                screen_hs_rect = pygame.Rect(hs.rect.x + self.play_offset_x, 
                                             hs.rect.y + self.play_offset_y, 
                                             hs.rect.width, hs.rect.height)
                hs.hovered = screen_hs_rect.collidepoint(pos)

    def soltar(self, all_slots: list):
        if self.debug_mode:
            if self.selected_hotspot:
                self.selected_hotspot = None
                self.hotspot_moving = False
                self.hotspot_resizing = False
                self.print_hotspots_code()
            return

        if self.obj_selecionado:
            tile = self.obj_selecionado
            tile.arrastando = False
            self.obj_selecionado = None
            
            snapped = False
            if self.terminal_aberto:
                # Tenta encaixar no slot colidido
                for slot in all_slots:
                    if slot.rect.colliderect(tile.rect):
                        if slot.item and slot.item != tile:
                            slot.item.reset_position()
                        slot.item = tile
                        tile.slot = slot
                        snapped = True
                        break
                        
            if not snapped:
                tile.reset_position()
                
            self.reorganize_shelf()

    def discover_clue(self, clue_id: str):
        if clue_id not in self.discovered_words:
            self.discovered_words.append(clue_id)
            tile = WordTile(clue_id, self.font_word)
            self.discovered_word_tiles.append(tile)
            self.reorganize_shelf()

    def reorganize_shelf(self):
        shelf_tiles = [tile for tile in self.discovered_word_tiles if tile.slot is None]
        
        # Organiza as pistas coletadas em linhas horizontais na prateleira (estante do rodapé)
        start_x = 40
        start_y = 722
        spacing_x = 12
        spacing_y = 6
        
        current_x = start_x
        current_y = start_y
        
        for tile in shelf_tiles:
            if current_x + tile.width > 984:
                current_x = start_x
                current_y += tile.height + spacing_y
                
            tile.original_x = current_x
            tile.original_y = current_y
            
            if not tile.arrastando:
                tile.x = current_x
                tile.y = current_y
                tile.update()
                
            current_x += tile.width + spacing_x
