import pygame

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
PATH_BG = './imagens/cenario devs.png'
PATH_PENDRIVE = './imagens/pendrive.png'
PATH_NOTEPAD = './imagens/bloc_de_notas.png'
PATH_SPRITES_BOSS = './imagens/sprites chefe/chefe-idle{i}.png'
PATH_SPRITES_INTERN = './imagens/sprites estagiario/estagiario-idle{i}.png'
PATH_ICON_BOSS = './imagens/icones/icone chefe.png'
PATH_ICON_DRAWER = './imagens/icones/gaveta cheia.png'

# ==============================================================================
# DIÁLOGOS DE ZOOM (OVERLAYS)
# ==============================================================================
OVERLAYS_DATA = {
    "postit": {
        "title": "ZOOM: POST-IT AO LADO DA MAQUINA",
        "lines": [
            [("Um post-it esta colado ao lado", False)],
            [("da maquina do estagiario.", False)],
            [("Nele, ha a ", False), ("Senha", "Senha"), (" de acesso do", False)],
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
            [("Voce abre a ", False), ("Gaveta", "Gaveta"), (" do ", False), ("Chefe", "Chefe"), (".", False)],
            [("Dentro dela, ha um dispositivo USB", False)],
            [("aparentemente largado as pressas:", False)],
            [("Um ", False), ("Pendrive", "Pendrive"), (" suspeito contendo", False)],
            [("arquivos criados recentemente.", False)]
        ]
    },
    "estagiario": {
        "title": "ZOOM: ESTAGIARIO ACUSADO",
        "lines": [
            [("Estagiario: 'Eu sou inocente!'", False)],
            [("'Fui o primeiro a ser acusado,", False)],
            [("mas eu nao fiz nada!'", False)],
            [("'Alguem usou o meu computador'", False)],
            [("'enquanto eu estava fora!'", False)]
        ]
    },
    "veteran": {
        "title": "ZOOM: DEPOIMENTO DO SENIOR",
        "lines": [
            [("Senior: 'Fui demitido e saio", False)],
            [("em uma semana. Nao me importo com", False)],
            [("essa investigacao da empresa.'", False)],
            [("Ao lado dele, o seu ", False), ("Celular", "Celular"), (" pessoal", False)],
            [("exibe uma ", False), ("Conversa", "Conversa"), (" de um", False)],
            [("funcionario ", False), ("Sênior", "Sênior"), (" insatisfeito.", False)]
        ]
    },
    "logs_de_acesso": {
        "title": "ZOOM: LOGS DO PC DO ESTAGIARIO",
        "lines": [
            [("Ao verificar o log do ", False), ("PC", "PC"), (", voce", False)],
            [("percebe uma atividade suspeita.", False)],
            [("Houve a instalacao de um ", False), ("Malware", "Malware"), (",", False)],
            [("que realizou o ", False), ("Vazamento", "Vazamento"), (" de", False)],
            [("80% dos dados dos clientes.", False)]
        ]
    },
    "clock": {
        "title": "ZOOM: RELOGIO DE PAREDE",
        "lines": [
            [("O relogio de parede marca o", False)],
            [("Horário", "Horário"), (" exato do vazamento:", False)],
            [("Os ponteiros pararam as ", False), ("03:00", "03:00"), (" AM.", False)]
        ]
    }
}

# ==============================================================================
# NARRATIVA DA VITÓRIA
# ==============================================================================
STORY_LINES = [
    "O Estagiario foi acusado pelo vazamento de 80% dos dados da nuvem,",
    "ja que o ataque partiu do computador dele.",
    "",
    "No entanto, as investigacoes revelaram a verdade dos fatos.",
    "O funcionario Senior, insatisfeito e subornado por terceiros,",
    "obteve a senha 'senh@forte123' anotada em um post-it.",
    "",
    "Ele criou um Malware em um Pendrive e infectou a maquina do",
    "estagiario, mas esqueceu o Pendrive em sua propria gaveta.",
    "",
    "As conversas em seu Celular comprovaram toda a sua culpabilidade.",
    "O Estagiario foi inocentado!"
]
