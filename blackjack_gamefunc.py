import random
import os
import sys

import pygame
from pygame.locals import *
import blackjack as bj_main
import blackjack as bj

# FUNÇÕES DE JOGO 
def embaralhar(baralho:list[str]) -> list[str]:
    """ Embaralha o baralho usando uma implementação do algoritmo de embaralhamento, de Fisher-Yates.
    - n = len(baralho) - 1. Enquanto n é maior que 0, um número aleatório k entre 0 e n é gerado. 
    - A carta no baralho representada pelo índice n é trocada pela carta no baralho representada pelo índice k.
    - DEPOIS, n é = n - 1, e o loop continua."""
    
    n = len(baralho) - 1
    while n > 0:
        k = random.randint(0, n)
        baralho[k], baralho[n] = baralho[n], baralho[k]
        n -= 1

    return baralho        
                        
def fazer_baralho() -> list[str]:
    """ Cria um baralho padrão de 52 cartas, e retorna ele mesmo. """

    baralho = ['sj', 'sq', 'sk', 'sa', 'hj', 'hq', 'hk', 'ha', 'cj', 'cq', 'ck', 'ca', 'dj', 'dq', 'dk', 'da']
    values = range(2,11)
    for x in values:
        espadas = "s" + str(x)
        copas = "h" + str(x)
        paus = "c" + str(x)
        ouros = "d" + str(x)
        baralho.append(espadas)
        baralho.append(copas)
        baralho.append(paus)
        baralho.append(ouros)
    return baralho

def retornar_cemiterio(baralho:list[str], cemiterio:list[str]) -> list[str]:
    """ Append das cartas do cemitério para o baralho que está em jogo. 
    - É chamada quando o baralho principal está vazio.
    - Retorna o baralho, e o cemitério."""
    
    for carta in cemiterio:
        baralho.append(carta)
    del cemiterio[:]
    baralho = embaralhar(baralho)

    return baralho, cemiterio
    
def dar_cartas(baralho:list[str], cemiterio:list[str]) -> list[str]:
    """ Embaralha o baralho, pega 4 cartas, adiciona 2 à mão do jogador e 2 à mão do dealer.
    - Retorna ambas as mãos. """

    baralho = embaralhar(baralho)
    mao_dealer, mao_jogador = [], []

    cartas_a_dar = 4

    while cartas_a_dar > 0:
        if len(baralho) == 0:
            baralho, cemiterio = retornar_cemiterio(baralho, cemiterio)

        # 1a carta ao jogador, 2a ao dealer, 3a ao jogador, 4a ao dealer
        if cartas_a_dar % 2 == 0:
            mao_jogador.append(baralho[0])
        else: 
            mao_dealer.append(baralho[0])
        
        del baralho[0]
        cartas_a_dar -= 1
        
    return baralho, cemiterio, mao_jogador, mao_dealer

def hit(baralho:list[str], cemiterio:list[str], mao:list[str]) -> list[str]:
    """ Checa se o baralho já acabou, e se for o caso, pega as cartas do cemitério e embaralha-as para o baralho.
    - Se o jogador está puxando uma carta, dá a carta ao jogador.
    - Mesma coisa com o dealer."""

    # Se o baralho está vazio
    if len(baralho) == 0:
        baralho, cemiterio = retornar_cemiterio(baralho, cemiterio)

    mao.append(baralho[0])
    del baralho[0]

    return baralho, cemiterio, mao

def contar_pontos(mao:list[str]) -> int:
    """ Checa a pontuação do jogador e do dealer, a partir de sua mão.
    - Retorna a pontuação."""

    pontuacao = 0

    for carta in mao:
        valor = carta[1:]

        # valetes(j), reis(k) e rainhas(q) valem todos 10, e ás(a) vale 11 ou 1  
        if valor == 'j' or valor == 'q' or valor == 'k': 
            valor = 10
        elif valor == 'a': 
            valor = 11
        else: 
            valor = int(valor)

        pontuacao += valor
        

    if pontuacao > 21:
        for carta in mao:
            # Se o jogador tem ás na mão, e iria quebrar caso o Ás valesse 10, o Ás passa a valer 1.
            # Em casos de múltiplos ás na mão, checa se o valor total é 21, ou se é menor  
            if carta[1] == 'a': 
                pontuacao -= 10
            if pontuacao <= 21:
                break
            else: # o jogador mesmo assim, quebrou
                continue

    return pontuacao
    
def blackJack(baralho:list[str], cemiterio:list[str], mao_jogador:list[str], mao_dealer:list[str], fichas:float, aposta:float, cartas:pygame.sprite.Group, cardSprite:bj_main.cardSprite) -> pygame.font.Font | list[str] | float | int:
    """ Chamada quando o jogador ou o dealer, estão aptos a ter um blackjack.
    - Mãos são comparadas para determinar a saída."""

    textFont = pygame.font.Font(None, 28)

    pontos_jogador = contar_pontos(mao_jogador)
    pontos_dealer = contar_pontos(mao_dealer)
    
    if pontos_jogador == 21 and pontos_dealer == 21:
        # Empate, jogador e dealer fizeram blackjack
        # Nenhum dinheiro é perdido
        display_fonte = bj.exibir(textFont, "Blackjack do jogador, e do Dealer! EMPATE!")
        baralho, mao_jogador, mao_dealer, cemiterio, fichas, fim_rodada = acabar_rodada(baralho, mao_jogador, mao_dealer, cemiterio, fichas, 0, aposta, cartas, cardSprite)
            
    elif pontos_jogador == 21 and pontos_dealer != 21:
        # Dealer perdeu
        display_fonte = bj.exibir(textFont, "Blackjack! Você GANHOU R$%.2f." %(aposta*1.5))
        baralho, mao_jogador, mao_dealer, cemiterio, fichas, fim_rodada = acabar_rodada(baralho, mao_jogador, mao_dealer, cemiterio, fichas, aposta, 0, cartas, cardSprite)
        
    elif pontos_dealer == 21 and pontos_jogador != 21:
        # Jogador perde a rodada e o dinheiro apostado
        baralho, mao_jogador, mao_dealer, cemiterio, fichas, fim_rodada = acabar_rodada(baralho, mao_jogador, mao_dealer, cemiterio, fichas, 0, aposta, cartas, cardSprite)
        display_fonte = bj.exibir(textFont, "Blackjack do Dealer! Você PERDEU R$%.2f." %(aposta))
        
    return display_fonte, mao_jogador, mao_dealer, cemiterio, fichas, fim_rodada

def quebrar(baralho:list[str], mao_jogador:list[str], mao_dealer:list[str], cemiterio:list[str], fichas:float, dinheiro_ganho:float, dinheiro_perdido:float, cartas:pygame.sprite.Group, cardSprite:bj_main.cardSprite) -> list[str] | float | int | pygame.font.Font:
    """ Só é chamada quando o jogador ou o dealer, quebram a mão e passam dos 21 pontos. """
    
    font = pygame.font.Font(None, 28)
    display_fonte = bj.exibir(font, "Você quebrou, passou de 21 pontos! PERDEU R$%.2f." %(dinheiro_perdido))
    
    baralho, mao_jogador, mao_dealer, cemiterio, fichas, fim_rodada = acabar_rodada(baralho, mao_jogador, mao_dealer, cemiterio, fichas, dinheiro_ganho, dinheiro_perdido, cartas, cardSprite)
    
    return baralho, mao_jogador, mao_dealer, cemiterio, fichas, fim_rodada, display_fonte

def acabar_rodada(baralho:list[str], mao_jogador:list[str], mao_dealer:list[str], cemiterio:list[str], fichas:float, dinheiro_ganho:float, dinheiro_perdido:float, cartas:pygame.sprite.Group, cardSprite:bj_main.cardSprite) -> list[str] | float | int:
    '''Chamada ao fim de uma rodada, para determinar o que acontece com as cartas, e dinheiro ganhou ou perdido.
    - Mostra a mão completa do dealer ao jogador, apagando os sprites antigos e mostrando todas as cartas'''
    
    if len(mao_jogador) == 2 and "a" in mao_jogador[0] or "a" in mao_jogador[1]:
        # Se o jogador já fez blackjack com 2 cartas na mão, elas sendo 2 ás 
        dinheiro_ganho += (dinheiro_ganho/2.0)
        
    # Remove as cartas antigas do dealer
    cartas.empty()
    
    d_carta_pos = (50, 70)
                
    for x in mao_dealer:
        carta = cardSprite(x, d_carta_pos)
        d_carta_pos = (d_carta_pos[0] + 80, d_carta_pos [1])
        cartas.add(carta)

    # Remove as cartas de ambas as mãos
    for carta in mao_jogador:
        cemiterio.append(carta)
    for carta in mao_dealer:
        cemiterio.append(carta)

    del mao_jogador[:]
    del mao_dealer[:]

    fichas += dinheiro_ganho
    fichas -= dinheiro_perdido
    
    textFont = pygame.font.Font(None, 28)
    
    if fichas <= 0:
        bj.gameOver() # acabaram as fichas
    
    fim_rodada = 1

    return baralho, mao_jogador, mao_dealer, cemiterio, fichas, fim_rodada 
    
def comparar_maos(baralho:list[str], cemiterio:list[str], mao_jogador:list[str], mao_dealer:list[str], fichas:float, aposta:float, cartas:pygame.sprite.Group, cardSprite:bj_main.cardSprite) -> list[str] | int | float | pygame.font.Font:
    """ Chamada ao fim de uma rodada (botão parar), ou no começo da rodada se o dealer fez blackjack.
    - Essa função comparar o valor das respectivas mãos de dealer/jogador.
    - Determina quem ganha."""

    textFont = pygame.font.Font(None, 28)
    # Quanto dinheir o jogador ganhou ou perdeu. 0 Por padrão, podendo mudar dependendo da saída
    dinheiro_ganho = 0
    dinheiro_perdido = 0

    pontos_dealer = contar_pontos(mao_dealer)
    pontos_jogador = contar_pontos(mao_jogador)
        
    # Dealer puxa cartas até pontos < 17 pontos        
    while 1:
        if pontos_dealer < 17:
            # Para de puxar cartas, se tiver 17 ou mais pontos
            baralho, cemiterio, mao_dealer = hit(baralho, cemiterio, mao_dealer)
            pontos_dealer = contar_pontos(mao_dealer)
        else:   
            # dealer para
            break
        
    if pontos_jogador > pontos_dealer and pontos_jogador <= 21:
        # Jogador pontuou mais que o dealer, e não quebrou, então GANHOU
        dinheiro_ganho = aposta
        baralho, mao_jogador, mao_dealer, cemiterio, fichas, fim_rodada = acabar_rodada(baralho, mao_jogador, mao_dealer, cemiterio, fichas, aposta, 0, cartas, cardSprite)
        display_fonte = bj.exibir(textFont, "Você GANHOU R$%.2f." %(aposta))
    elif pontos_jogador == pontos_dealer and pontos_jogador <= 21:
        # Empate
        baralho, mao_jogador, mao_dealer, cemiterio, fichas, fim_rodada = acabar_rodada(baralho, mao_jogador, mao_dealer, cemiterio, fichas, 0, 0, cartas, cardSprite)
        display_fonte = bj.exibir(textFont, "EMPATE, mesma pontuação!")
    elif pontos_dealer > 21 and pontos_jogador <= 21:
        # Dealer quebrou, e o jogador não
        baralho, mao_jogador, mao_dealer, cemiterio, fichas, fim_rodada = acabar_rodada(baralho, mao_jogador, mao_dealer, cemiterio, fichas, aposta, 0, cartas, cardSprite)
        display_fonte = bj.exibir(textFont, "Dealer quebrou, passou de 21 pontos! Você GANHOU R$%.2f." %(aposta))
    else:
        # Dealer ganha em qualquer outra situação
        baralho, mao_jogador, mao_dealer, cemiterio, fichas, fim_rodada = acabar_rodada(baralho, mao_jogador, mao_dealer, cemiterio, fichas, 0, aposta, cartas, cardSprite)
        display_fonte = bj.exibir(textFont, "Dealer venceu! Você PERDEU R$%.2f." %(aposta))
        
    return baralho, cemiterio, fim_rodada, fichas, display_fonte

# FUNÇÕES DE JOGO ACABAM
def registrar_nome() -> str:
    '''Função apenas para guardar o nome do jogador, após o jogo.
    - Retorna o nome salvo, para o ranking.'''
    nome = input('Nome: ')
    return nome

def fazer_ranking(nome: str, pontuacao: int) -> list[str]:
    '''Monta o Ranking, reunindo todas as funções que realizam a sua montagem.

    Parâmetros:
        nome: o nome do Jogador
        pontuacao: A pontuação do Jogador
    Retorna o ranking do jogo
    '''
    # Daqui pra baixo vai ficar dentro do laço
    # Lê do arquivo
    arq = open('ranking.txt', encoding='utf-8')
    linhas = arq.readlines()
    arq.close()
    ranking = []
    
    ordenar_posicoes(linhas, ranking)

    salvar_pontuacao_jogador(arq, nome, pontuacao)
        
    arq = open('ranking.txt', encoding='utf-8')
    linhas = arq.readlines()
    arq.close()
    ranking = []
    
    ordenar_posicoes(linhas, ranking)
    return ranking
        
def ordenar_posicoes(linhas: list[str], ranking: list[str]) -> list[str]:
    '''Ordena as posições dos jogadores
       
       Parâmetros:
        linhas: A lista de string com as linhas do arquivo
        ranking: A lista com o ranking desordenado dos jogadores

    Retorna o ranking atualizado do jogo com as posições ordenadas'''
    
    for i in range(0, len(linhas), 2):
        nome = linhas[i][:-1]
        pontuacao = int(linhas[i+1][:-1])
        nome_pontuacao = [pontuacao, nome]
        ranking.append(nome_pontuacao)
    return ranking
    
def salvar_pontuacao_jogador(arq, nome: str, pontuacao: int) -> None: #O 'arq' está sem tipo pois ele é um documento de texto, e seu tipo segundo o python seria "TextIOWrapper", mas não estava aceitando
    '''Registra o `nome` e a `pontuacao` no arquivo do ranking.
       
       Parâmetros: 
        arq: O arquivo em que o ranking está guardado
        nome: O nome do jogador 
        pontuacao: A pontuação final do jogador(O valor de fichas que ele tinha ao parar de jogar)
    Sem retornos'''
    arq = open('ranking.txt', 'a', encoding='utf-8')
    arq.write(nome + '\n')
    arq.write(str(pontuacao)  + '\n')
    arq.close()

def exibir_ranking(ranking: list[str]) -> None:
    '''Exibe o ranking do jogo, baseado em quem conseguiu mais fichas ao jogar

       Parâmetros:
       ranking: O ranking do jogo
    Sem retornos, é uma função de saída de exibição
    '''
    ranking_ordenado = sorted(ranking, reverse=True)
    print('Ranking - Top 3: ')
    if len(ranking) >= 3:
        for i in range(3):
            posicao_ranking = ranking_ordenado[i]
            print(f'{posicao_ranking[0]} fichas - ', end='')
            print(posicao_ranking[1])
    else:
        for i in range(len(ranking)):
            posicao_ranking = ranking_ordenado[i]
            print(f'{posicao_ranking[0]} fichas - ', end='')
            print(posicao_ranking[1])