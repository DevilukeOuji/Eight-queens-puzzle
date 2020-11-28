from random import randint
import timeit

class chess():
    def __init__(self):
        self.tabuleiro = []
        self.analisado = []
        self.h = 0
        for i in range(0,8):
            linha = randint(0,7)
            tupla = (linha,i)
            self.tabuleiro += [tupla]
        
        
    def inicializa(self):
        self.h = chess.atualizaH(self.h, self.tabuleiro)
        self.analisado = []
    
    def analisa(self):
        for i in range(1000):
            h = 0
            queen = chess.chooseQueen()
            rand = randint(0,7)
            while rand == queen[0]: rand = randint(0,7)  
            new_queen = (rand,queen[1])

            new_tabuleiro = self.tabuleiro.copy()
            pos_queen = self.tabuleiro.index(queen)
            new_tabuleiro[pos_queen] = new_queen
            
            h = chess.atualizaH(h,new_tabuleiro)

            if self.h > h:
                self.h = h
                self.tabuleiro[pos_queen] = new_queen
            
            if self.h == 0:
                print(f'O número de iterações foi: {i}')
                return h
        return h
             
    def atualizaH(self, he, tabuleiro):
        for queen in tabuleiro:
            self.analisado += [queen]
            he = chess.checkHorizontal(tabuleiro,queen, he)
            he = chess.checkD1(tabuleiro,queen, he)
        self.analisado = []
        return he

    def chooseQueen(self):
        rand = randint(0,7)
        queen = self.tabuleiro[rand]
        self.analisado += [queen]
        return queen

    def checkHorizontal(self,tabuleiro, queen, h):
        for i in tabuleiro: 
            if i != queen:
                if i not in self.analisado:
                    if i[0] == queen[0]: h += 1
        return h

    def checkD1(self,tabuleiro, queen, h):
        linha1 = queen[0];linha2 = queen[0];coluna = queen[1]
        while coluna >= 0:
            coluna -= 1
            linha1 -= 1
            linha2 += 1
            if (linha1,coluna) not in self.analisado:
                if (linha1,coluna) in tabuleiro: h += 1
            if (linha2,coluna) not in self.analisado:
                if (linha2,coluna) in tabuleiro: h += 1
        linha1 = queen[0];linha2 = queen[0];coluna = queen[1]
        while coluna <= 7:
            coluna += 1
            linha1 -= 1
            linha2 += 1
            if (linha1,coluna) not in self.analisado:
                if (linha1,coluna) in tabuleiro: h += 1
            if (linha2,coluna) not in self.analisado:
                if (linha2,coluna) in tabuleiro: h += 1
        return h

    def imprime(self):
        for i in self.tabuleiro:
            print(i)

chess = chess()
chess.inicializa()
h = chess.analisa()
print(f'h é {h}')
chess.imprime()