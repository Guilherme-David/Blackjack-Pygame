import random
import os
import sys

import pygame
from pygame.locals import *
import blackjack_gamefunc as bj_func

pygame.font.init()
pygame.mixer.init()

SCREEN = pygame.display.set_mode((800, 480))
CLOCK = pygame.time.Clock()


# SISTEMA DE FUNÇÕES GRÁFICAS COMEÇA
def carregar_imagem(nome: str, carta: int) -> tuple:
    """ Função para carregar alguma imagem da pasta 'images'.
    - A função os.path.join é usada para guardar o nome completo da carta que é = nome da imagem .png
    - Parâmetros:
        - nome: nome completo da imagem.
        - carta: 1 para cartas, 0 para outro tipo de imagem.
    - Variáveis:
        - nome_imagem: guarda o caminho (pasta) e o nome para a  imagem em si, onde está localizada no diretório.
        - imagem: tipo SURFACE é usado para representar qualquer imagem no pygame.
    - Retorno:
        - Representação da imagem, e um quadrado retângular do tamanho da imagem para desenha-la.
    - AVISO: O jogo tem de ser compatível com múltiplas versões da biblioteca 'os'. """
    
    if carta == 1: # Imagem de Carta
        nome_imagem: str = os.path.join("images/cards/", nome)
    else: # Plano de fundo e outros
        nome_imagem: str = os.path.join('images', nome)
    
    imagem = pygame.image.load(nome_imagem) 
    
    imagem = imagem.convert() # Método de conversão do pygame
    
    return imagem, imagem.get_rect() 
        
def carregar_som(nome: str) : 
    """ Mesma idéia da função 'carregar_imagem'.
    - Retorno:
        - -> Sound, uma classe do pygame é o retorno."""
    nome_som = os.path.join('sounds', nome)
    som = pygame.mixer.Sound(nome_som) # Som programado para ser mixado, tocado
    return som

def exibir(fonte: pygame.font, mensagem: str):
    """ Exibe o texto na parte baixa da tela, informando o que está acontecendo no momento exato, ao jogador.
    - Parâmetros:
        - fonte: modulo para fontes no pygame.
        - mensagem: mensagem a ser exibida.
    - Variável:
        - displayFont: combinação da fonte e da mensagem.
    - Retorno: 
        - -> Surface. A representação da mensagem construída, e renderizada."""
    
    display_fonte = pygame.font.Font.render(fonte, mensagem, 1, (255,255,255), (0,0,0)) 
    return display_fonte

def tocar_som() -> None:
    '''Função que armazena o som do Click, ativada quando obviamente o jogador clica em algo.
    - Sem Parâmetros.
    - Variável: 
        - do tipo Sound, passa o nome do som e recebe ele formatado para tocar.'''
    clickSound = carregar_som("click2.wav")
    clickSound.play() # toca o som
    
def gameOver() -> None:
    """ Exibe uma tela de gameOver, quando o jogador perde todas as suas fichas.
    - Tudo que o jogador pode fazer nessa tela é sair do jogo.
    - Sem retorno, e sem parâmtros.
    - AVISO: Quem chegar nessa tela, não tem seu nome registrado no Ranking."""
    
    while 1: # loop infinito
        for event in pygame.event.get(): # para cada ação em pygame.event.get -> detectar a ação
            if event.type == QUIT: # se o tipo de ação for == 'QUIT' = 'SAIR'
                sys.exit() # Usa a biblioteca sys, para fechar a tela de jogo 
            if event.type == KEYDOWN and event.key == K_ESCAPE: # Atalhos de saída
                sys.exit()

        # Preenche a tela com preto
        SCREEN.fill((0,0,0))
        
        # Exibe a mensagem de gameover na tela
        oFont = pygame.font.Font(None, 30)
        display_fonte = pygame.font.Font.render(oFont, "Game over! Suas fichas acabaram! Não aparece no RANKING do jogo!", 1, (255,255,255), (0,0,0)) 
        SCREEN.blit(display_fonte, (70, 220))
        
        # Atualiza a exibição
        pygame.display.flip()
        
def fim_jogo() -> None:
    """ Acionado quando o jogador quer sair do jogo.
    - Exibe uma mensagem, pedindo para o jogador registrar seu nome no terminal.
    - Motivo: registrar jogador no ranking, e exibir top 3."""
    
    # Preenche a tela com preto
    SCREEN.fill((0,0,0))
        
    # Exibe a mensagem de gameover na tela
    oFont = pygame.font.Font(None, 40)
    display_fonte = pygame.font.Font.render(oFont, "Registre seu nome lá em BAIXO, para encerrar!", 1, (255,255,255), (0,0,0)) 
    SCREEN.blit(display_fonte, (100, 220))
        
    # Atualiza a exibição
    pygame.display.flip()
    
# FUNÇÕES DA CLASSE 'SPRITE' COMEÇA, EXIBIÇÃO DE IMAGENS DE CARTAS E BOTÕES
class cardSprite(pygame.sprite.Sprite):
    """ Sprite para exibir alguma carta específica. """
    
    def __init__(self, carta: str, posicao: tuple[int]) -> None:
        '''Constroi o corpo da carta.
        - Recebe a própria carta, e a posição que ela será desenhada.'''
        pygame.sprite.Sprite.__init__(self)
        imagem_carta = carta + ".png" # nome da carta
        self.image, self.rect = carregar_imagem(imagem_carta, 1) # carrega a imagem
        self.position = posicao # define a posição 
    def update(self) -> None:
        '''update padrão do Sprite, desenha a carta na tela, em cima do formato rect = retângulo.'''
        self.rect.center = self.position
        
class puxarButton(pygame.sprite.Sprite):
    """ Botão que permite o jogador puxar uma carta do baralho. """
    
    def __init__(self) -> None:
        '''Constrói o corpo do botão PUXAR.
        - Não recebe parâmetros, exceto ele mesmo.'''
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = carregar_imagem("hit-grey.png", 0) # por padrão a imagem carregada é cinza.
        self.position = (735, 400)
        
    def update(self, mX:int, mY:int, baralho:list, cemiterio:list, mao_jogador:list, cartas:pygame.sprite.Group, j_carta_pos:tuple, rodada_fim:int, cardSprite:cardSprite, click:int) -> tuple[list, list, list, tuple, int]:
        """ Se o botão for pressionado e a rodada NÃO acabou, dá ao jogador uma nova carta vinda do baralho.
        - A função também cria um sprite para a carta e exibe.
        - Retorna o baralho, o cemitério e mão do jogador como listas. E a posição da carta, e o click como inteiro."""
        
        if rodada_fim == 0: # se a rodada ainda não acabou, pode puxar carta
            self.image, self.rect = carregar_imagem("hit.png", 0)
        else: 
            self.image, self.rect = carregar_imagem("hit-grey.png", 0)
        
        self.position = (735, 400) # posição do botão
        self.rect.center = self.position
        
        if self.rect.collidepoint(mX, mY) == 1 and click == 1: # se o botão for pressionado
            if rodada_fim == 0:  # se a rodada não acabou,
                tocar_som()
                baralho, cemiterio, mao_jogador = bj_func.hit(baralho, cemiterio, mao_jogador) # puxa a carta

                carta_atual = len(mao_jogador) - 1 # índice da carta puxada 
                carta = cardSprite(mao_jogador[carta_atual], j_carta_pos) # desenhar a carta, com o cardSprite
                cartas.add(carta) # adiciona a carta ao grupo Sprite das cartas exibidas 
                j_carta_pos = (j_carta_pos[0] - 80, j_carta_pos[1]) # Posição da carta à esquerda das outras
            
                click = 0 # Redefine o click para 0, para não manter o botão pressionado
            
        return baralho, cemiterio, mao_jogador, j_carta_pos, click
        
class pararButton(pygame.sprite.Sprite):
    """ Botão que permite o jogador parar. Não puxar mais cartas. """
    
    def __init__(self) -> None:
        '''Constrói o corpo do botão PARAR
        - Não recebe parâmetros, exceto ele mesmo.'''
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = carregar_imagem("stand-grey.png", 0)
        self.position = (735, 365)
        
    def update(self, mX:int, mY:int, baralho:list, cemiterio:list, mao_jogador:list, mao_dealer:list, cartas:pygame.sprite.Group, j_carta_pos:tuple, rodada_fim:int, cardSprite:cardSprite, fichas:float, aposta:float, display_fonte:pygame.font.Font) -> tuple[list, list, int, float, list, list, tuple, pygame.font.Font]:
        """ Se o botão for pressionado e a rodada ainda NÃO acabou, permite o jogador parar."""
        
        if rodada_fim == 0:  # Se a rodada não acabou
            self.image, self.rect = carregar_imagem("stand.png", 0) # O jogador pode apertar o botão
        else: 
            self.image, self.rect = carregar_imagem("stand-grey.png", 0)
        
        self.position = (735, 365) # Posição do botão
        self.rect.center = self.position
        
        if self.rect.collidepoint(mX, mY) == 1: # Se o botão for pressionado
            if rodada_fim == 0:  # rodada ainda não acabou
                tocar_som()
                baralho, cemiterio, rodada_fim, fichas, display_fonte = bj_func.comparar_maos(baralho, cemiterio, mao_jogador, mao_dealer, fichas, aposta, cartas, cardSprite) # Compara as mãos, e dá o resultado da rodada 
            
        return baralho, cemiterio, rodada_fim, fichas, mao_jogador, cemiterio, j_carta_pos, display_fonte 
        
class dobrarButton(pygame.sprite.Sprite):
    """ Botão que permite o jogador dobrar a aposta, puxar uma carta.
    - Se tiver 2 cartas na mão.
    - Para de puxar cartas."""
    
    def __init__(self):
        '''Constrói o corpo do botão DOBRAR.
        - Não recebe parâmetros, exceto ele mesmo.'''
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = carregar_imagem("double-grey.png", 0)
        self.position = (735, 330)
        
    def update(self, mX:int, mY:int, baralho:list, cemiterio:list, mao_jogador:list, mao_dealer:list, cartas_jogador:pygame.sprite.Group, cartas:pygame.sprite.Group, j_carta_pos:tuple, rodada_fim:int, cardSprite:cardSprite, fichas:float, aposta:float, display_fonte:pygame.font.Font) -> tuple[list, list, int, float, float, list, list, tuple, pygame.font.Font, float]:
        """ Se o botão for clicado, e a rodada NÃO acabou, permite o jogador dobrara sua aposta. """
        
        if rodada_fim == 0 and fichas >= aposta * 2 and len(mao_jogador) == 2: #  Se a rodada não acabou, e a qtd de fichas é maior igual a aposta dobrada
            self.image, self.rect = carregar_imagem("double.png", 0)
        else: 
            self.image, self.rect = carregar_imagem("double-grey.png", 0)
            
        self.position = (735, 330) # Posição do botão
        self.rect.center = self.position
            
        if self.rect.collidepoint(mX, mY) == 1: # Pressionado
            if rodada_fim == 0 and fichas >= aposta * 2 and len(mao_jogador) == 2: 
                aposta = aposta * 2 # Se pode, dobra a aposta
                
                tocar_som()
                baralho, cemiterio, mao_jogador = bj_func.hit(baralho, cemiterio, mao_jogador) # Puxa a carta

                # semelhante ao hit
                carta_atual = len(mao_jogador) - 1  
                carta = cardSprite(mao_jogador[carta_atual], j_carta_pos)
                cartas_jogador.add(carta)
                j_carta_pos = (j_carta_pos[0] - 80, j_carta_pos[1])
    
                baralho, cemiterio, rodada_fim, fichas, display_fonte = bj_func.comparar_maos(baralho, cemiterio, mao_jogador, mao_dealer, fichas, aposta, cartas, cardSprite) # compara o resultado, após a parada
                
                aposta = aposta / 2 # aposta assume o valor normal

        return baralho, cemiterio, rodada_fim, fichas, mao_jogador, cemiterio, j_carta_pos, display_fonte, aposta

class jogarButton(pygame.sprite.Sprite):
    """ Botão que pode ser apertado quando não há uma rodada em jogo.
    - Nova mão de cartas dadas, e continua/começa o jogo."""
    
    def __init__(self):
        '''Constrói o botão JOGAR.
        - Sem parâmetros, exceto ele mesmo.'''
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = carregar_imagem("deal.png", 0)
        self.position = (735, 450)

    def update(self, mX:int, mY:int, baralho:list, cemiterio:list, rodada_fim:int, cardSprite:cardSprite, cartas:pygame.sprite.Group, mao_jogador:list, mao_dealer:list, d_carta_pos:tuple, j_carta_pos:tuple, display_fonte:pygame.font.Font, cartas_jogador:pygame.sprite.Group, click:int, maos_jogadas:int) -> tuple[list | tuple | int | str]:
        """ Se a posição do mouse colide com o botão, e ele está sendo pressionado e rodada_fim não é =0,
        - Chama a função dar_cartas para criar uma mão para o jogador e o dealer, e seus sprites de exibição, colocando-os na mesa.
        - O botão jogar, só pode ser apertado ao fimde uma rodada com um vencedor já declarado, Ou na inicialização do jogo."""
        
        fonte_texto = pygame.font.Font(None, 28)
        
        if rodada_fim == 1: # Se não há rodada em curso
            self.image, self.rect = carregar_imagem("deal.png", 0)
        else: 
            self.image, self.rect = carregar_imagem("deal-grey.png", 0)
        
        self.position = (735, 450) # posição do botão
        self.rect.center = self.position
        
            
        if self.rect.collidepoint(mX, mY) == 1: # apertado
            if rodada_fim == 1 and click == 1:
                tocar_som()
                display_fonte = exibir(fonte_texto, "")
                
                cartas.empty() # esvazia as cartas antigas
                cartas_jogador.empty()
                
                baralho, cemiterio, mao_jogador, mao_dealer = bj_func.dar_cartas(baralho, cemiterio) # dá as cartas

                d_carta_pos = (50, 70) # posição da primerira carta do dealer (X,Y)
                j_carta_pos = (540,370) # posição da primeira carta do jogador (X,Y)

                # Cria os sprites de exibição das cartas do jogador
                for x in mao_jogador:
                    carta = cardSprite(x, j_carta_pos)
                    j_carta_pos = (j_carta_pos[0] - 80, j_carta_pos [1])
                    cartas_jogador.add(carta)
                
                # Cria os sprites de exibição das cartas do dealer 
                verso_carta = cardSprite("back", d_carta_pos) # carta oculta do dealer
                d_carta_pos = (d_carta_pos[0] + 80, d_carta_pos[1])
                cartas.add(verso_carta)

                carta = cardSprite(mao_dealer [0], d_carta_pos)
                cartas.add(carta)
                rodada_fim = 0
                click = 0
                maos_jogadas += 1
                
        return baralho, cemiterio, mao_jogador, mao_dealer, d_carta_pos, j_carta_pos, rodada_fim, display_fonte, click, maos_jogadas
        
        
class apostaAumentadaButton(pygame.sprite.Sprite):
    """ Botão que permite o jogador aumentar sua aposta. """
    
    def __init__(self):
        '''Constrói o botão de aumentar aposta.
        - Sem parâmetros, exceto ele mesmo.'''
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = carregar_imagem("up.png", 0)
        self.position = (710, 255)
        
    def update(self, mX:int, mY:int, aposta:float, fichas:float, click:int, fim_rodada:int) -> tuple[float | int]:
        '''Clicável ao fim das rodadas, para aumentar a aposta.'''
        if fim_rodada == 1: 
            self.image, self.rect = carregar_imagem("up.png", 0)
        else: 
            self.image, self.rect = carregar_imagem("up-grey.png", 0)
        
        self.position = (710, 255)
        self.rect.center = self.position
        
        if self.rect.collidepoint(mX, mY) == 1 and click == 1 and fim_rodada == 1: # clicado
            tocar_som()
                
            if aposta < fichas:
                aposta += 5.0
                # Se a aposta não for múltipla de 5
                # Isso só pode acontecer, se o jogador conseguiu um blackjack de 2 cartas
                if aposta % 5 != 0:
                    while aposta % 5 != 0:
                        aposta -= 1 # Reduz a aposta, até ser divisível por 5

            click = 0
        
        return aposta, click
        
class apostaReduzidaButton(pygame.sprite.Sprite):
    """ Botão que permite o jogador reduzir sua aposta. """
    
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = carregar_imagem("down.png", 0)
        self.position = (710, 255)
        
    def update(self, mX:int, mY:int, aposta:float, click:int, fim_rodada:int) -> tuple[float | int]:
        '''Mesmo sentido do botão para aumentar a aposta, só que aqui diminui.'''
        if fim_rodada == 1: 
            self.image, self.rect = carregar_imagem("down.png", 0)
        else: 
            self.image, self.rect = carregar_imagem("down-grey.png", 0)
    
        self.position = (760, 255)
        self.rect.center = self.position
        
        if self.rect.collidepoint(mX, mY) == 1 and click == 1 and fim_rodada == 1:
            tocar_som()
            if aposta > 5:
                aposta -= 5.0
                if aposta % 5 != 0:
                    while aposta % 5 != 0:
                        aposta += 1
                
            click = 0
        
        return aposta, click
# FUNÇÕES SPRITE DE EXIBIÇÃO TERMINAM

def mostrar_informacoes(fonte_texto:str, fichas:float, display_fonte:pygame.font.Font, aposta:float, maos_jogadas:int) -> None:
    '''Função usada dentro do jogo, para exibir fichas, aposta, e rodada atuais.
    - Recebe como parâmetros a fonte padrão, as fichas e aposta do jogador, a mensagem a ser exibida e as mãos jogadas.
    - Sem retorno, é de exibição. '''
    
    SCREEN.blit(display_fonte, (60, 444))
    fonte_fichas = pygame.font.Font.render(fonte_texto, "Fichas: R$%.2f" %(fichas), 1, (255,255,255), (0,0,0))
    SCREEN.blit(fonte_fichas, (663, 205))
    fonte_aposta = pygame.font.Font.render(fonte_texto, "Aposta: R$%.2f" %(aposta), 1, (255,255,255), (0,0,0))
    SCREEN.blit(fonte_aposta, (663, 285))
    fonte_rodada = pygame.font.Font.render(fonte_texto, "Rodada: %i " %(maos_jogadas), 1, (255,255,255), (0,0,0))
    SCREEN.blit(fonte_rodada, (663, 180))
# FIM DAS FUNÇÕES GRÁFICAS

# FUNÇÕES PRINCIPAIS
def inicializar() -> float:
    """ Função responsável por inicializar o jogo.
    - Retorna a pontuação do jogador."""
    
    # PROCESSO DE INICIALIZAÇÃO COMEÇA
    # Essa fonte é usada como padrão
    textFont = pygame.font.Font(None, 24)

    # Define o background, e desenha-o em formato retangular
    background, background_rect = carregar_imagem("bjs.png", 0)
    
    # O grupo sprite, que vai ter todas as cartas de exibição, do dealer
    cartas = pygame.sprite.Group()
    # Mesmo propósito. Mas, para o jogador
    cartas_jogador = pygame.sprite.Group()

    # INSTÂNCIAS para todas as classes de botões
    aAB = apostaAumentadaButton()
    aRB = apostaReduzidaButton()
    pararB = pararButton()
    jogarB = jogarButton()
    puxarB = puxarButton()
    dobrarB = dobrarButton()
    
    # INUTILIZADO, mas criado por garantia
    buttons = pygame.sprite.Group(aAB, aRB, puxarB, pararB, jogarB, dobrarB)

    # O Baralho de 52 cartas é criado
    baralho = bj_func.fazer_baralho()
    # O cemitério vai ter todas as cartas descartadas
    cemiterio = []

    # Valores padrão, que serão alterados posteriormente
    mao_jogador, mao_dealer, d_carta_pos, j_carta_pos = [],[],(),()
    mX, mY = 0, 0
    click = 0

    # Fichas padrão = R$100.00, Aposta padrão = R$10.00
    fichas = 100.00
    aposta = 10.00

    # Contagem de rodadas
    maos_jogadas = 0

    # Quando as cartas não foram dadas ainda, rodada_fim = 1
    # Quando a rodada não acabou, rodada_fim = 0
    fim_rodada = 1
    
    # VARIÁVEL usada uma única vez, para exibir uma mensagem no canto de baixo da tela
    primeira_vez = 1
    # FIM DE INICIALIZAÇÃO
    
    # LOOP PRINCIPAL
    fichas = jogar(background, background_rect, textFont, cartas, jogarB, aAB, aRB, pararB, dobrarB, puxarB, cartas_jogador, aposta, fichas, fim_rodada, primeira_vez, maos_jogadas, mX, mY, click, baralho, cemiterio, mao_jogador, mao_dealer, d_carta_pos, j_carta_pos) # pois, fichas = pontuação
    return fichas

def jogar(background:pygame.surface.Surface, background_rect:pygame.rect.Rect, fonte_texto:str, cartas:pygame.sprite.Group, jogarB:jogarButton, aAB:apostaAumentadaButton, aRB:apostaReduzidaButton, pararB:pararButton, dobrarB:dobrarButton, puxarB:puxarButton, cartas_jogador:tuple, aposta:float, fichas:float, fim_rodada:int, primeira_vez:int, maos_jogadas:int, mX:int, mY:int, click:int, baralho:list, cemiterio:list, mao_jogador:list, mao_dealer:list, d_carta_pos:tuple, j_carta_pos:tuple) -> float:
    '''Executa uma partida completa do jogo.
    - Retorna a pontuação.'''
    buttons = pygame.sprite.Group(aAB, aRB, puxarB, pararB, jogarB, dobrarB) # Definição padrão dos sprites dos botões
    # LOOP DO JOGO
    while 1:
        SCREEN.blit(background, background_rect) # exibe o plano de fundo
        
        if aposta > fichas:
            # Se você perdeu dinheiro, e sua aposta é maior que suas fichas, faz a aposta = qtd de fichas
            aposta = fichas
        
        if fim_rodada == 1 and primeira_vez == 1:
            # Quando o jogador ainda não jogou a primeria vez. Só vai ser exibido no início.
            display_fonte = exibir(fonte_texto, "Clique nas setas para declarar sua aposta. JOGAR para começar rodada.")
            primeira_vez = 0 # Não será mais usado

        # Mostra as informaçõs principais
        mostrar_informacoes(fonte_texto, fichas, display_fonte, aposta, maos_jogadas)

        # Se a ação for de sair
        for event in pygame.event.get():
            if event.type == QUIT:
                fim_jogo() # Exibe a tela de fim de jogo
                return fichas # Retorna as fichas, pois fichas = pontuação
            elif event.type == MOUSEBUTTONDOWN: # Se mexer o mouse
                if event.button == 1: 
                    mX, mY = pygame.mouse.get_pos()
                    click = 1
            elif event.type == MOUSEBUTTONUP:
                mX, mY = 0, 0
                click = 0

        # Começa chegando o valor da mão do jogador, então ela pode ser exibida e definido se
        # O jogador quebrou/fez blackjack, ou não
        if fim_rodada == 0:
            # Quando o jogo está em curso
            playerValue = bj_func.contar_pontos(mao_jogador)
            dealerValue = bj_func.contar_pontos(mao_dealer)

            if playerValue == 21 and len(mao_jogador) == 2:
                # Se o jogador fizer um blacjkack
                display_fonte, mao_jogador, mao_dealer, cemiterio, fichas, fim_rodada = bj_func.blackJack(baralho, cemiterio, mao_jogador, mao_dealer, fichas,  aposta, cartas, cardSprite)
                
            if dealerValue == 21 and len(mao_dealer) == 2:
                # Se o dealer fizer um blackjack
                display_fonte, mao_jogador, mao_dealer, cemiterio, fichas, fim_rodada = bj_func.blackJack(baralho, cemiterio, mao_jogador, mao_dealer, fichas,  aposta, cartas, cardSprite)

            if playerValue > 21:
                # Se o jogador quebrar a mão
                baralho, mao_jogador, mao_dealer, cemiterio, fichas, fim_rodada, display_fonte = bj_func.quebrar(baralho, mao_jogador, mao_dealer, cemiterio, fichas, 0, aposta, cartas, cardSprite)
         
        # Atyaliza os botões
        # jogar 
        baralho, cemiterio, mao_jogador, mao_dealer, d_carta_pos, j_carta_pos, fim_rodada, display_fonte, click, maos_jogadas = jogarB.update(mX, mY, baralho, cemiterio, fim_rodada, cardSprite, cartas, mao_jogador, mao_dealer, d_carta_pos, j_carta_pos, display_fonte, cartas_jogador, click, maos_jogadas)   
        # puxar    
        baralho, cemiterio, mao_jogador, j_carta_pos, click = puxarB.update(mX, mY, baralho, cemiterio, mao_jogador, cartas_jogador, j_carta_pos, fim_rodada, cardSprite, click)
        # parar    
        baralho, cemiterio, fim_rodada, fichas, mao_jogador, cemiterio, j_carta_pos,  display_fonte  = pararB.update(mX, mY,   baralho, cemiterio, mao_jogador, mao_dealer, cartas, j_carta_pos, fim_rodada, cardSprite, fichas, aposta, display_fonte)
        # dobrar
        baralho, cemiterio, fim_rodada, fichas, mao_jogador, cemiterio, j_carta_pos, display_fonte, aposta  = dobrarB.update(mX, mY,   baralho, cemiterio, mao_jogador, mao_dealer, cartas_jogador, cartas, j_carta_pos, fim_rodada, cardSprite, fichas, aposta, display_fonte)
        # Botões de aposta
        aposta, click = aAB.update(mX, mY, aposta, fichas, click, fim_rodada)
        aposta, click = aRB.update(mX, mY, aposta, click, fim_rodada)
        # Desenha-os na tela
        buttons.draw(SCREEN)
         
        # Se tem cartas na tela, desenha elas
        if len(cartas) is not 0:
            cartas_jogador.update()
            cartas_jogador.draw(SCREEN)
            cartas.update()
            cartas.draw(SCREEN)

        # Atualiza o conteúdo de exibição
        pygame.display.flip()
    # LOOP PRINCIPAL ENCERRA
# FUNÇÕES DO JOGO PRINCIPAL ACABAM

def exibicao_final(pontos):
    '''Função apenas para receber os pontos do jogador e:
    - Registrar seu nome.
    - Adicionar ele no Ranking, e exibir o top3 do Ranking.
    - AVISO: SE O JOGADOR ZERAR, NÃO APARECE NO RANKING.'''
    print(f'Pontuação final: {int(pontos)} pontos.')
    nome = bj_func.registrar_nome()
    ranking = bj_func.fazer_ranking(nome=nome, pontuacao=int(pontos)) # Pontuação final = qtd de fichas restantes
    bj_func.exibir_ranking(ranking)

if __name__ == "__main__":
    pontos = inicializar() # Pontuação do jogador = pontuação completa em todo o jogo, até fechar
    exibicao_final(pontos) # Processo de nome e ranking
    sys.exit() # Fecha o jogo e o terminal.