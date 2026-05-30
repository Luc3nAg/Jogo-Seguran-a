# Vazamento Crítico - Investigação SOC 2026 🕵️‍♂️💻

**Vazamento Crítico** é um jogo educativo e interativo de investigação forense digital e segurança da informação, desenvolvido em **Python** utilizando a biblioteca **Pygame**. 

No papel de um analista de segurança do SOC (Security Operations Center), o jogador deve explorar o cenário retro, analisar evidências, correlacionar pistas e desvendar quem realmente foi o responsável por um vazamento crítico de dados da empresa.

---

## 📖 Enredo da Investigação

A empresa sofreu um vazamento massivo de 80% dos dados sensíveis de seus clientes. O **Estagiário** foi o primeiro acusado, pois a atividade maliciosa partiu de seu computador de trabalho. 

No entanto, as aparências enganam! Ao investigar a sala do SOC, você encontrará pistas espalhadas por diversos locais:
* **Gaveta do Chefe**: Um pendrive misterioso deixado às pressas.
* **Celular do Sênior**: Conversas suspeitas exibidas na tela do celular de um funcionário insatisfeito que está prestes a sair da empresa.
* **Logs de Acesso**: Registros do PC mostrando a instalação de um malware e o horário do incidente.
* **Post-it**: Anotações contendo credenciais de acesso vulneráveis.
* **Relógio de Parede**: O horário exato em que o ataque aconteceu.

---

## 🎮 Mecânicas e Controles

* **Exploração com Cursor Dinâmico**: Ao mover o mouse sobre áreas investigáveis (hotspots), o cursor se transforma em uma **lupa estilizada** de 32x32 pixels, indicando que o objeto pode ser inspecionado.
* **Caixas de Zoom**: Ao clicar em uma área de interesse, abre-se uma tela detalhada com a descrição das pistas. Palavras-chave destacadas em **ouro/âmbar** podem ser coletadas clicando sobre elas.
* **Terminal de Dedução**: Colete as pistas necessárias e abra o Terminal do SOC no menu superior. Arraste as pistas coletadas da prateleira (rodapé) e encaixe-as nos campos correspondentes para montar a sentença que resolve o caso.
* **Teclas de Atalho**:
  * `ESC`: Volta ao menu principal, fecha telas de zoom ou fecha o terminal de dedução.
  * `R`: Reinicia a investigação quando o caso é resolvido (na tela de vitória).
  * `D`: Ativa o modo de depuração (Debug Mode) para ajustar ou visualizar as coordenadas das caixas de colisão.

---

## 🛠️ Tecnologias Utilizadas

* **Linguagem**: Python 3.13+
* **Engine gráfica/UI**: Pygame 2.6.1 (com suporte a cursores coloridos de 32 bits a partir do SDL2)
* **Design Visual**: Estilo CRT/retro terminal com fósforo verde e paleta âmbar.
* **Empacotamento**: PyInstaller (para compilação em executável standalone)

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
Certifique-se de ter o Python 3.10 ou superior instalado em sua máquina.

### Passo 1: Configurar o ambiente virtual e instalar dependências
Crie um ambiente virtual na pasta do projeto e instale as dependências:
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# No Windows (PowerShell):
venv\Scripts\Activate.ps1
# No Linux/macOS:
source venv/bin/activate

# Instalar o Pygame
pip install pygame
```

### Passo 2: Executar o jogo
Execute o arquivo principal para iniciar a partida:
```bash
python index.py
```

---

## 📦 Como Gerar o Executável (.exe)

O projeto vem com o arquivo de especificação do PyInstaller (`Vazamento_Critico.spec`) configurado para incluir automaticamente as pastas de assets (`imagens` e `fontes`).

Para compilar o jogo:
```bash
# Certifique-se de ter o PyInstaller instalado no venv
pip install pyinstaller

# Gerar o executável
pyinstaller Vazamento_Critico.spec
```
O executável compilado será gerado na pasta `dist/Vazamento_Critico/`.

---

## 📂 Estrutura de Arquivos

* `index.py`: Ponto de entrada que inicializa a engine e roda o loop principal.
* `src/`:
  * `game_engine.py`: Gerenciador do loop principal, eventos de mouse/teclado, dimensionamento dinâmico (letterboxing) e efeitos visuais CRT.
  * `world.py`: Gerencia a lógica do cenário de jogo, overlays de zoom, carregamento de sprites, coleta de pistas e preenchimento do terminal.
  * `config.py`: Definições globais de resolução, cores (RGB), caminhos dos arquivos e base de dados dos diálogos.
  * `models/`:
    * `hotspot.py`: Representa as áreas clicáveis no cenário.
    * `slot.py`: Representa os campos receptores de respostas no terminal.
    * `word_tile.py`: Representa as palavras arrastáveis e colecionáveis.
* `imagens/`: Contém os sprites de animação do chefe, estagiário, fundos de menu/cenário e ícones.
* `fontes/`: Fontes pixeladas utilizadas na interface do usuário (VT323).
