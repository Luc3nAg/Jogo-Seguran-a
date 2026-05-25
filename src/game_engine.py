import pygame
import sys
from src import config
from src.world import World
from src.models.slot import Slot

class GameEngine:
    """
    Gerencia a inicialização global do jogo, o loop principal, o controle
    de eventos do teclado e mouse, as dimensões físicas da janela e o letterboxing.
    """
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("A Maldicao Criptica - Investigacao SOC 2026")
        
        self.screen_w = config.SCREEN_W
        self.screen_h = config.SCREEN_H
        self.tela = pygame.display.set_mode((self.screen_w, self.screen_h), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        
        # Canvas lógico para renderização virtual independente de resolução física
        self.canvas = pygame.Surface((config.CANVAS_W, config.CANVAS_H))
        
        # Parâmetros de escala e letterboxing padrão
        self.scale_factor = 1.0
        self.canvas_w = config.CANVAS_W
        self.canvas_h = config.CANVAS_H
        self.ox = 0
        self.oy = 0
        
        # Carrega fontes retro utilizando Consolas (garantida em sistemas Windows)
        self.font_title = pygame.font.SysFont("consolas", 40, bold=True)
        self.font_ui = pygame.font.SysFont("consolas", 18, bold=True)
        self.font_text = pygame.font.SysFont("consolas", 20)
        self.font_word = pygame.font.SysFont("consolas", 16, bold=True)
        self.font_victory = pygame.font.SysFont("consolas", 22)
        
        # Inicializa os slots de investigação no Terminal de Sentenças
        ox_term = 192
        oy_term = 140
        
        self.slot_who = Slot("", ox_term + 55, oy_term + 70, 140, 30, "Estagiário", self.font_ui)
        self.slot_how = Slot("", ox_term + 305, oy_term + 115, 140, 30, "Script", self.font_ui)
        self.slot_pwd = Slot("", ox_term + 170, oy_term + 160, 100, 30, "1234", self.font_ui)
        self.slot_where = Slot("", ox_term + 195, oy_term + 205, 140, 30, "Servidor", self.font_ui)
        self.slot_why = Slot("", ox_term + 295, oy_term + 250, 180, 30, "Reinicialização", self.font_ui)
        
        self.slot_culprit = Slot("", ox_term + 125, oy_term + 350, 120, 30, "Chefe", self.font_ui)
        self.slot_proof1 = Slot("", ox_term + 340, oy_term + 350, 200, 30, "Script Malicioso", self.font_ui)
        self.slot_proof2 = Slot("", ox_term + 340, oy_term + 395, 200, 30, "1234", self.font_ui)
        
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
        
        provas_corretas = {"Script Malicioso", "1234"}
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
                    self.rodando = False
                elif event.key == pygame.K_r and self.game_solved:
                    # Reinicia todo o estado da engine de jogo
                    self.__init__()
                elif event.key == pygame.K_d:
                    # Ativa/Desativa modo de depuração para hitboxes
                    self.world.toggle_debug()
      
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not self.game_solved:
                    # Se clicar no botão de abrir o terminal
                    if not self.world.terminal_aberto and not self.world.zoom_overlay:
                        abrir_terminal_rect = pygame.Rect(780, 25, 210, 45)
                        if abrir_terminal_rect.collidepoint(mouse):
                            self.world.terminal_aberto = True
                            continue
                    self.world.clicar(mouse)

            elif event.type == pygame.MOUSEBUTTONUP:
                if not self.game_solved:
                    self.world.soltar(self.investigation_slots)

            elif event.type == pygame.MOUSEMOTION:
                if not self.game_solved:
                    self.world.mover(mouse)

    def update(self):
        self.world.update()

    def draw(self):
        # Limpa o canvas lógico
        self.canvas.fill(config.COLOR_BG)

        # Título principal do jogo
        title_surf = self.font_title.render("A MALDICAO CRIPTICA", True, config.COLOR_AMBER)
        title_rect = title_surf.get_rect(centerx=config.CANVAS_W // 2, top=15)
        self.canvas.blit(title_surf, title_rect)
        
        # Placa do contador de pistas coletadas
        pygame.draw.rect(self.canvas, config.COLOR_SHELF_BORDER, (35, 25, 190, 45))
        pygame.draw.rect(self.canvas, config.COLOR_ZOOM_BORDER, (35, 25, 190, 45), 2)
        self.draw_bag_icon(self.canvas, 45, 35)
        clues_count = len(self.world.discovered_words)
        clues_surf = self.font_ui.render(f"PISTAS: {clues_count}/15", True, config.COLOR_AMBER)
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
                        hint_surf = self.font_ui.render("> ACESSO NEGADO: Parametros incorretos. Verifique as evidencias.", True, (255, 70, 60))
                        self.canvas.blit(hint_surf, (config.CANVAS_W // 2 - hint_surf.get_width() // 2, 195))
            else:
                instr_surf = self.font_ui.render("> Arraste as pistas do rodape para as caixas de parametros.", True, config.COLOR_CRT_GREEN)
                self.canvas.blit(instr_surf, (config.CANVAS_W // 2 - instr_surf.get_width() // 2, 195))

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
