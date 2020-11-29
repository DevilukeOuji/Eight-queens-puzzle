from random import randint

class chess():
    def __init__(self):
        self.board = []
        self.analyzed = []
        self.h = 0
        for i in range(0,8):
            row = randint(0,7)
            tupla = (row,i)
            self.board += [tupla]
        
        
    def initialize(self):
        self.h = chess.refresh(self.h, self.board)
        self.analyzed = []
    
    def analyze(self):
        for i in range(1000):
            h = 0
            queen = chess.chooseQueen()
            rand = randint(0,7)
            while rand == queen[0]: rand = randint(0,7)  
            new_queen = (rand,queen[1])

            new_board = self.board.copy()
            pos_queen = self.board.index(queen)
            new_board[pos_queen] = new_queen
            
            h = chess.refresh(h,new_board)

            if self.h > h:
                self.h = h
                self.board[pos_queen] = new_queen
            
            if self.h == 0:
                print(f'O número de iterações foi: {i}')
                return h
        return h
             
    def refresh(self, he, board):
        for queen in board:
            self.analyzed += [queen]
            he = chess.checkHorizontal(board,queen, he)
            he = chess.checkDiagonal(board,queen, he)
        self.analyzed = []
        return he

    def chooseQueen(self):
        rand = randint(0,7)
        queen = self.board[rand]
        self.analyzed += [queen]
        return queen

    def checkHorizontal(self,board, queen, h):
        for i in board: 
            if i != queen:
                if i not in self.analyzed:
                    if i[0] == queen[0]: h += 1
        return h

    def checkDiagonal(self,board, queen, h):
        row1 = queen[0];row2 = queen[0];column = queen[1]
        while column >= 0:
            column -= 1
            row1 -= 1
            row2 += 1
            if (row1,column) not in self.analyzed:
                if (row1,column) in board: h += 1
            if (row2,column) not in self.analyzed:
                if (row2,column) in board: h += 1
        row1 = queen[0];row2 = queen[0];column = queen[1]
        while column <= 7:
            column += 1
            row1 -= 1
            row2 += 1
            if (row1,column) not in self.analyzed:
                if (row1,column) in board: h += 1
            if (row2,column) not in self.analyzed:
                if (row2,column) in board: h += 1
        return h

    def printing(self):
        for i in self.board:
            print(i)

chess = chess()
chess.initialize()
h = chess.analyze()
print(f'h é {h}')
chess.printing()