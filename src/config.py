import pygame
import os
import sys

def get_path(relative_path):
    """ Retorna o caminho absoluto do recurso, compatível com desenvolvimento e executável do PyInstaller """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# ==============================================================================
# RESOLUÇÕES E DIMENSÕES
# ==============================================================================
SCREEN_W = 1280
SCREEN_H = 720
CANVAS_W = 1024
CANVAS_H = 800

# Área do cenário retro centralizado (800x600)
PLAY_OFFSET_X = 112
PLAY_OFFSET_Y = 120
PLAY_W = 800
PLAY_H = 600

# Área do Terminal de Sentenças
TERM_X = 142
TERM_Y = 135
TERM_W = 740
TERM_H = 570

# ==============================================================================
# CORES DO JOGO
# ==============================================================================
COLOR_BG = (16, 13, 10)
COLOR_TEXT_WHITE = (225, 215, 200)

# Estilo Fósforo Verde (Dedução / CRT / Terminal)
COLOR_CRT_GREEN = (0, 230, 70)
COLOR_CRT_GREEN_LITE = (0, 255, 90)
COLOR_CRT_GREEN_MID = (0, 210, 60)
COLOR_CRT_GREEN_DARK = (0, 100, 30)
COLOR_CRT_BG = (2, 10, 5)
COLOR_CRT_BG_DARK = (5, 18, 8)
COLOR_CRT_BG_BUTTON = (5, 45, 15)

# Estilo Ouro / Âmbar (Pistas Coletadas / Cabeçalho)
COLOR_AMBER = (235, 195, 80)
COLOR_AMBER_LITE = (255, 235, 150)
COLOR_AMBER_DARK = (150, 110, 30)
COLOR_SHELF_BG = (24, 19, 14)
COLOR_SHELF_BORDER = (45, 35, 25)
COLOR_CLUE_SHADOW = (20, 15, 10)

# Zoom Overlay / Botão Fechar
COLOR_ZOOM_BG = (28, 22, 16)
COLOR_ZOOM_BG_SHADOW = (10, 8, 5)
COLOR_ZOOM_BORDER = (80, 60, 45)
COLOR_ZOOM_INNER_BORDER = (140, 110, 80)
COLOR_CLOSE_RED = (140, 35, 25)
COLOR_CLOSE_RED_BORDER = (200, 60, 50)

# Destaque de Hover das hitboxes
COLOR_HOVER_FILL = (0, 235, 70, 45)
COLOR_HOVER_BORDER = (0, 235, 70)

# Debug
COLOR_DEBUG_TEXT = (255, 255, 100)
COLOR_DEBUG_BOX = (255, 100, 100, 50)
COLOR_DEBUG_BORDER = (255, 100, 100)
COLOR_DEBUG_SELECTED_BOX = (50, 200, 255, 90)
COLOR_DEBUG_SELECTED_BORDER = (50, 220, 255)

# ==============================================================================
# CAMINHOS E ASSETS
# ==============================================================================
PATH_BG = get_path('imagens/cenario.png')
PATH_PENDRIVE = get_path('imagens/pendrive.png')
PATH_NOTEPAD = get_path('imagens/bloc_de_notas.png')
PATH_SPRITES_BOSS = get_path('imagens/sprites chefe/chefe-idle{i}.png')
PATH_SPRITES_INTERN = get_path('imagens/sprites estagiario/estagiario-idle{i}.png')
PATH_ICON_BOSS = get_path('imagens/icones/icone chefe.png')
PATH_ICON_DRAWER = get_path('imagens/icones/gaveta cheia.png')

# ==============================================================================
# DIÁLOGOS DE ZOOM (OVERLAYS)
# ==============================================================================
OVERLAYS_DATA = {
    "postit": {
        "title": "ZOOM: POST-IT AO LADO DA MÁQUINA",
        "lines": [
            [("Um post-it está colado ao lado", False)],
            [("da máquina do estagiário.", False)],
            [("Nele, há a ", False), ("Senha", "Senha"), (" de acesso do", False)],
            [("Estagiário", "Estagiário"), (": ", False), ("senh@forte123", "senh@forte123"), (".", False)]
        ]
    },
    "bulletin_board": {
        "title": "ZOOM: QUADRO KANBAN DA SPRINT",
        "lines": [
            [("O quadro Kanban detalha a", False)],
            [("infraestrutura da empresa.", False)],
            [("Ela gerencia o armazenamento de", False)],
            [("Dados", "Dados"), (" dos clientes na ", False), ("Nuvem", "Nuvem"), (".", False)]
        ]
    },
    "gaveta": {
        "title": "ZOOM: GAVETA DO CHEFE",
        "lines": [
            [("Você abre a ", False), ("Gaveta", "Gaveta"), (" do ", False), ("Chefe", "Chefe"), (".", False)],
            [("Dentro dela, há um dispositivo USB", False)],
            [("aparentemente largado às pressas:", False)],
            [("Um ", False), ("Pendrive", "Pendrive"), (" suspeito contendo", False)],
            [("arquivos criados recentemente.", False)]
        ]
    },
    "estagiario": {
        "title": "ZOOM: ESTAGIÁRIO ACUSADO",
        "lines": [
            [("Estagiário: 'Eu sou inocente!'", False)],
            [("'Fui o primeiro a ser acusado,", False)],
            [("mas eu não fiz nada!'", False)],
            [("'Alguém usou o meu computador'", False)],
            [("'enquanto eu estava fora!'", False)]
        ]
    },
    "veteran": {
        "title": "ZOOM: DEPOIMENTO DO SÊNIOR",
        "lines": [
            [("Sênior: 'Fui demitido e saio", False)],
            [("em uma semana. Não me importo com", False)],
            [("essa investigação da empresa.'", False)],
            [("Ao lado dele, o seu ", False), ("Celular", "Celular"), (" pessoal", False)],
            [("exibe uma ", False), ("Conversa", "Conversa"), (" de um", False)],
            [("funcionário ", False), ("Sênior", "Sênior"), (" insatisfeito.", False)]
        ]
    },
    "logs_de_acesso": {
        "title": "ZOOM: LOGS DO PC DO ESTAGIÁRIO",
        "lines": [
            [("Ao verificar o log do ", False), ("PC", "PC"), (", você", False)],
            [("percebe uma atividade suspeita.", False)],
            [("Houve a instalação de um ", False), ("Malware", "Malware"), (",", False)],
            [("que realizou o ", False), ("Vazamento", "Vazamento"), (" de", False)],
            [("80% dos dados dos clientes.", False)]
        ]
    },
    "clock": {
        "title": "ZOOM: RELÓGIO DE PAREDE",
        "lines": [
            [("O relógio de parede marca o", False)],
            [("Horário", "Horário"), (" exato do vazamento:", False)],
            [("Os ponteiros pararam às ", False), ("03:00", "03:00"), (" AM.", False)]
        ]
    }
}

# ==============================================================================
# NARRATIVA DA VITÓRIA
# ==============================================================================
STORY_LINES = [
    "A empresa sofreu um vazamento de 80%",
    "dos dados sensíveis de seus clientes.",
    "O Estagiário foi o primeiro acusado, pois",
    "o vazamento partiu de seu PC.",
    "",
    "A investigação revelou um post-it com a",
    "senha 'senh@forte123' ao lado de sua máquina,",
    "e um pendrive largado na gaveta do Chefe.",
    "",
    "No celular do Chefe, havia uma conversa com",
    "um anônimo oferecendo dinheiro pelo vazamento.",
    "",
    "Ele criou o malware no pendrive e",
    "incriminou o Estagiário. Seu erro foi ter",
    "esquecido o pendrive na sua própria gaveta."
]
