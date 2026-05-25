import pygame

# ==============================================================================
# RESOLUÇÕES E DIMENSÕES
# ==============================================================================
SCREEN_W = 1024
SCREEN_H = 800
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

# ==============================================================================
# DIÁLOGOS DE ZOOM (OVERLAYS)
# ==============================================================================
OVERLAYS_DATA = {
    "postit": {
        "title": "ZOOM: POST-IT NO BLOCO DE NOTAS",
        "lines": [
            [("Um post-it amarelo esta colado no", False)],
            [("bloco de notas com anotacoes.", False)],
            [("Nele, ha uma anotacao da ", False), ("Senha", "Senha"), (":", False)],
            [("A senha do servidor e ", False), ("1234", "1234"), (".", False)]
        ]
    },
    "bulletin_board": {
        "title": "ZOOM: QUADRO KANBAN DA SPRINT",
        "lines": [
            [("O quadro Kanban detalha as operacoes", False)],
            [("programadas da startup.", False)],
            [("Na coluna Concluido, a tarefa diz:", False)],
            [("'Agendado: ", False), ("Server Reset", "Server Reset"), (" do servidor", False)],
            [("as 03:00 AM'. O script de logs", False)],
            [("forcava um shutdown, gerando uma", False)],
            [("Reinicialização", "Reinicialização"), (" completa do sistema.", False)],
            [("O plano original era so o ", False), ("Apagamento", "Apagamento"), (".", False)]
        ]
    },
    "pendrive": {
        "title": "ZOOM: PENDRIVE NO CHAO DA SALA",
        "lines": [
            [("Um dispositivo USB de metal", False)],
            [("esta jogado no chao da sala.", False)],
            [("Ao ler o conteudo dele, voce ve:", False)],
            [("O script contido no ", False), ("Pendrive", "Pendrive"), (" e um", False)],
            [("Script Malicioso", "Script Malicioso"), (" de automacao.", False)],
            [("Ele foi programado para rodar", False)],
            [("diretamente no ", False), ("Servidor", "Servidor"), (" central.", False)]
        ]
    },
    "estagiario": {
        "title": "ZOOM: ESTAGIARIO ACUSADO",
        "lines": [
            [("Estagiario: 'Eu juro que nao", False)],
            [("deletei os dados do servidor!'", False)],
            [("O Chefe esta furioso comigo,", False)],
            [("mas eu nao fiz nada de errado.", False)],
            [("Acho que o script que ele mesmo", False)],
            [("configurou deu erro no Servidor.", False)],
            [("Por favor, encontre as provas no", False)],
            [("Terminal para me inocentar!'", False)]
        ]
    },
    "veteran": {
        "title": "ZOOM: DEPOIMENTO DO CHEFE FURIOSO",
        "lines": [
            [("Chefe Bob: 'A culpa e toda daquele", False)],
            [("estagiario incompetente!'", False)],
            [("'Eu, o ", False), ("Chefe", "Chefe"), (", mandei ele revisar logs.'", False)],
            [("'Ele deve ter ativado algum ", False), ("Script", "Script"), ("'", False)],
            [("no sistema por erro!'", False)],
            [("'Toda a ", False), ("Culpa", "Culpa"), (" e dele! Ele derrubou'", False)],
            [("o servidor central!'", False)]
        ]
    },
    "logs_de_acesso": {
        "title": "ZOOM: LOGS DE ACESSO DO CHEFE",
        "lines": [
            [("Voce analisa o computador do Chefe.", False)],
            [("Na tela, estao abertos os logs.", False)],
            [("Nele, o Chefe acusa o ", False), ("Estagiário", "Estagiário"), (" de", False)],
            [("agir como o ", False), ("Atacante", "Atacante"), (" da invasao.", False)],
            [("E exige: 'Verificar os ", False)],
            [("Logs de Acesso", "Logs de Acesso"), (" urgente!'.", False)]
        ]
    },
    "clock": {
        "title": "ZOOM: RELOGIO DE PAREDE",
        "lines": [
            [("O relogio de parede parou de", False)],
            [("funcionar subitamente.", False)],
            [("Os ponteiros travados marcam", False)],
            [("o horario exato da queda: ", False), ("03:00", "03:00"), (".", False)]
        ]
    }
}

# ==============================================================================
# NARRATIVA DA VITÓRIA
# ==============================================================================
STORY_LINES = [
    "O Chefe Bob tentou de tudo para culpar o Estagiario pela queda,",
    "mas as pistas revelaram a verdade dos fatos.",
    "",
    "A senha obvia '1234' estava colada no monitor do proprio Chefe.",
    "O pendrive no chao continha um script de automacao configurado",
    "por ele mesmo para 'limpar os logs' da maquina as 03:00 AM.",
    "",
    "O script executou com erro e derrubou o servidor central,",
    "fazendo os ponteiros do relogio congelarem no tempo.",
    "",
    "O Estagiario foi inocentado. O verdadeiro culpado foi revelado!"
]
