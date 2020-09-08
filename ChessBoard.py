from tkinter import *
import copy
import sys

PIECES = 'pnbrqk'


class ChessBoard(Frame):
    def __init__(self, master=None):
        self.row = 8
        self.column = 8
        self.WhiteColor = "white"
        self.BlackColor = "black"
        self.width = 64
        self.height = 64
        self.pieces = {}
        self.boardC = {}
        self.XYCoords = {}
        self.Min_MaxNums = {}
        self.Min_MaxLetters = {}
        self.OriginalColor = None
        self.CurrentUserLocation = None
        self.ChosenPiece = None
        self.ChosenPieceLoc = {}
        self.ChosenPieceLocation = None
        self.moved = False
        self.color = "W"

        colors = [self.WhiteColor, self.BlackColor]

        Frame.__init__(self, master)
        self.pack()
        self.canvas = Canvas(self, width=self.width*8, height=self.height*8)

        for x, y in enumerate(list('87654321')):
            for n, m in enumerate(list('abcdefgh')):
                color = colors[(x-n) % 2]
                tags = [m+y, color, 'square']
                self.boardC[m+y] = (self.canvas.create_rectangle(n*self.width, x*self.height, n *
                                                                 self.width+self.width, x*self.height+self.height, outline=color, fill=color, tag=tags))
                self.Min_MaxLetters[m] = [self.getCoordinates(
                    m+y)[0], self.getCoordinates(m+y)[2]]
                self.Min_MaxNums[y] = [self.getCoordinates(
                    m+y)[1], self.getCoordinates(m+y)[3]]
        self.canvas.grid(row=0, column=0)

        self.piecesImg = {}
        for p in PIECES:
            self.piecesImg[p] = PhotoImage(file='./images/%s.gif' % p)

        self.key_list = list(self.boardC.keys())
        self.values_list = list(self.boardC.values())
        self.setXY()
        self.canvas.bind('<Button-1>', self.GetUserCoordinates)

    def addPiece(self, piece, state):
        XY = self.getXY(state)
        img = self.canvas.create_image(
            XY[0], XY[1], image=self.piecesImg[piece[2]], anchor='c')
        self.placePiece(piece, state)
        self.ChosenPieceLoc[piece] = img

    def placePiece(self, piece, state):
        self.pieces[state] = piece

    def getCoordinates(self, square):
        return self.canvas.coords(self.boardC[square])

    def initalBoard(self):
        self.addPiece('W_r1', 'a1')
        self.addPiece('W_r2', 'h1')
        self.addPiece('W_n1', 'b1')
        self.addPiece('W_n2', 'g1')
        self.addPiece('W_b1', 'c1')
        self.addPiece('W_b2', 'f1')
        self.addPiece('W_q', 'd1')
        self.addPiece('W_k', 'e1')

        self.addPiece('B_r1', 'a8')
        self.addPiece('B_r2', 'h8')
        self.addPiece('B_n1', 'b8')
        self.addPiece('B_n2', 'g8')
        self.addPiece('B_b1', 'c8')
        self.addPiece('B_b2', 'f8')
        self.addPiece('B_q', 'd8')
        self.addPiece('B_k', 'e8')

        for val, x in enumerate(list('abcdefgh')):
            self.addPiece('W_p'+str(val+1), x+'2')
            self.addPiece('B_p'+str(val+1), x+'7')

    # sets to X and Y values for each state on board
    def setXY(self):
        for index, val in enumerate(self.values_list):
            co = self.canvas.coords(val)
            X = (co[2] + co[0]) / 2
            Y = (co[3] + co[1]) / 2
            self.XYCoords[self.key_list[index]] = [X, Y]

    def getXY(self, state):
        return self.XYCoords[state]

    def getState(self, XY):
        for index, letterCo in enumerate(self.Min_MaxLetters.values()):
            if XY[0] in range(int(letterCo[0]), int(letterCo[1])):
                letter = list(self.Min_MaxLetters.keys())[index]

        for index, numCo in enumerate(self.Min_MaxNums.values()):
            if XY[1] in range(int(numCo[0]), int(numCo[1])):
                number = list(self.Min_MaxNums.keys())[index]
        return letter + number

    def GetUserCoordinates(self, event):
        global x, y
        x = float(event.x)
        y = float(event.y)
        if self.OriginalColor is not None and self.CurrentUserLocation is not None:
            self.canvas.itemconfig(
                self.CurrentUserLocation, fill=self.OriginalColor)

        self.OriginalColor = self.canvas.itemcget(
            self.getState([x, y]), 'fill')
        self.CurrentUserLocation = self.getState([x, y])
        self.canvas.itemconfig(self.CurrentUserLocation, fill='red')
        piece = self.PieceChecker()
        if piece is not None and self.ChosenPiece is None and piece[0] == self.color:
            self.ChosenPiece = piece
            self.ChosenPieceLocation = self.CurrentUserLocation
        elif self.ChosenPiece is not None:
            if self.pieceValidMove(self.ChosenPiece, self.ChosenPieceLocation, self.CurrentUserLocation, self.pieces) and not self.willBeInCheck(self.ChosenPiece):
                del self.pieces[self.ChosenPieceLocation]
                self.movePiece()
                self.canvas.itemconfig(
                    self.CurrentUserLocation, fill=self.OriginalColor)
                self.moved = True
            self.ChosenPiece = None

    def PieceChecker(self):
        if self.CurrentUserLocation in self.pieces.keys():
            return self.pieces[self.CurrentUserLocation]
        return None

    def movePiece(self):
        self.canvas.delete(self.ChosenPieceLoc[self.ChosenPiece])
        if self.CurrentUserLocation in self.pieces.keys():
            self.canvas.delete(
                self.ChosenPieceLoc[self.pieces[self.CurrentUserLocation]])
        self.addPiece(self.ChosenPiece, self.CurrentUserLocation)

    def pieceValidMove(self, pType, cPos, dPos, pieces):
        if pType[2] == "p":
            return self.pawnValidMove(cPos, dPos, pType[0], pieces)
        elif pType[2] == "r":
            return self.rookValidMove(cPos, dPos, pType[0], pieces)
        elif pType[2] == "n":
            return self.knightValidMove(cPos, dPos, pType[0], pieces)
        elif pType[2] == "q":
            return self.queenValidMove(cPos, dPos, pType[0], pieces)
        elif pType[2] == "b":
            return self.bishopValidMove(cPos, dPos, pType[0], pieces)
        else:
            return self.kingValidMove(cPos, dPos, pType[0], pieces)

    def pawnValidMove(self, cPos, dPos, color, pieces):
        moves = []
        if color == self.color:
            if chr(ord(cPos[1])+1) <= '8' and not cPos[0]+chr(ord(cPos[1])+1) in pieces:
                moves.append(cPos[0]+chr(ord(cPos[1])+1))
            if chr(ord(cPos[1])) == '2' and not cPos[0]+chr(ord(cPos[1])+2) in pieces:
                moves.append(cPos[0]+chr(ord(cPos[1])+2))
            if chr(ord(cPos[0])+1) <= 'h' and chr(ord(cPos[1])+1) <= '8' and chr(ord(cPos[0])+1)+chr(ord(cPos[1])+1) in pieces and pieces[chr(ord(cPos[0])+1)+chr(ord(cPos[1])+1)][0] != self.color:
                moves.append(chr(ord(cPos[0])+1)+chr(ord(cPos[1])+1))
            if chr(ord(cPos[0])-1) >= 'a' and chr(ord(cPos[1])+1) <= '8' and chr(ord(cPos[0])-1)+chr(ord(cPos[1])+1) in pieces and pieces[chr(ord(cPos[0])-1)+chr(ord(cPos[1])+1)][0] != self.color:
                moves.append(chr(ord(cPos[0])-1)+chr(ord(cPos[1])+1))
        else:
            if chr(ord(cPos[1])-1) >= '1' and not cPos[0]+chr(ord(cPos[1])-1) in pieces:
                moves.append(cPos[0]+chr(ord(cPos[1])-1))
            if chr(ord(cPos[1])) == '7' and not cPos[0]+chr(ord(cPos[1])-2) in pieces:
                moves.append(cPos[0]+chr(ord(cPos[1])-2))
            if chr(ord(cPos[0])+1) <= 'h' and chr(ord(cPos[1])-1) >= '1' and chr(ord(cPos[0])+1)+chr(ord(cPos[1])-1) in pieces and pieces[chr(ord(cPos[0])+1)+chr(ord(cPos[1])-1)][0] == self.color:
                moves.append(chr(ord(cPos[0])+1)+chr(ord(cPos[1])-1))
            if chr(ord(cPos[0])-1) >= 'a' and chr(ord(cPos[1])-1) >= '1' and chr(ord(cPos[0])-1)+chr(ord(cPos[1])-1) in pieces and pieces[chr(ord(cPos[0])-1)+chr(ord(cPos[1])-1)][0] == self.color:
                moves.append(chr(ord(cPos[0])-1)+chr(ord(cPos[1])-1))
        if dPos in moves:
            return True
        else:
            return False

    def rookValidMove(self, cPos, dPos, color, pieces):
        moves = []
        k = None
        x = ord(cPos[0])
        while k is None and x > ord('a'):
            x -= 1
            if chr(x)+cPos[1] in pieces.keys():
                k = pieces[chr(x)+cPos[1]]
            else:
                k = None
            if k is None or k[0] != color:
                moves.append(chr(x)+cPos[1])
        k = None
        x = ord(cPos[0])
        while k is None and x < ord('h'):
            x += 1
            if chr(x)+cPos[1] in pieces.keys():
                k = pieces[chr(x)+cPos[1]]
            else:
                k = None
            if k is None or k[0] != color:
                moves.append(chr(x)+cPos[1])
        k = None
        y = ord(cPos[1])
        while k is None and y > ord('0'):
            y -= 1
            if cPos[0]+chr(y) in pieces.keys():
                k = pieces[cPos[0]+chr(y)]
            else:
                k = None
            if k is None or k[0] != color:
                moves.append(cPos[0]+chr(y))
        k = None
        y = ord(cPos[1])
        while k is None and y < ord('8'):
            y += 1
            if cPos[0]+chr(y) in pieces.keys():
                k = pieces[cPos[0]+chr(y)]
            else:
                k = None
            if k is None or k[0] != color:
                moves.append(cPos[0]+chr(y))
        if dPos in moves:
            return True
        else:
            return False

    def knightValidMove(self, cPos, dPos, color, pieces):
        moves = []
        if chr(ord(cPos[0])-1) >= 'a' and chr(ord(cPos[1])-2) >= '1' and (not chr(ord(cPos[0])-1)+chr(ord(cPos[1])-2) in pieces or pieces[chr(ord(cPos[0])-1)+chr(ord(cPos[1])-2)][0] != color):
            moves.append(chr(ord(cPos[0])-1)+chr(ord(cPos[1])-2))
        if chr(ord(cPos[0])+1) <= 'h' and chr(ord(cPos[1])-2) >= '1' and (not chr(ord(cPos[0])+1)+chr(ord(cPos[1])-2) in pieces or pieces[chr(ord(cPos[0])+1)+chr(ord(cPos[1])-2)][0] != color):
            moves.append(chr(ord(cPos[0])+1)+chr(ord(cPos[1])-2))
        if chr(ord(cPos[0])-1) >= 'a' and chr(ord(cPos[1])+2) <= '8' and (not chr(ord(cPos[0])-1)+chr(ord(cPos[1])+2) in pieces or pieces[chr(ord(cPos[0])-1)+chr(ord(cPos[1])+2)][0] != color):
            moves.append(chr(ord(cPos[0])-1)+chr(ord(cPos[1])+2))
        if chr(ord(cPos[0])+1) <= 'h' and chr(ord(cPos[1])+2) <= '8' and (not chr(ord(cPos[0])+1)+chr(ord(cPos[1])+2) in pieces or pieces[chr(ord(cPos[0])+1)+chr(ord(cPos[1])+2)][0] != color):
            moves.append(chr(ord(cPos[0])+1)+chr(ord(cPos[1])+2))
        if chr(ord(cPos[0])-2) >= 'a' and chr(ord(cPos[1])-1) >= '1' and (not chr(ord(cPos[0])-2)+chr(ord(cPos[1])-1) in pieces or pieces[chr(ord(cPos[0])-2)+chr(ord(cPos[1])-1)][0] != color):
            moves.append(chr(ord(cPos[0])-2)+chr(ord(cPos[1])-1))
        if chr(ord(cPos[0])+2) <= 'h' and chr(ord(cPos[1])-1) >= '1' and (not chr(ord(cPos[0])+2)+chr(ord(cPos[1])-1) in pieces or pieces[chr(ord(cPos[0])+2)+chr(ord(cPos[1])-1)][0] != color):
            moves.append(chr(ord(cPos[0])+2)+chr(ord(cPos[1])-1))
        if chr(ord(cPos[0])-2) >= 'a' and chr(ord(cPos[1])+1) <= '8' and (not chr(ord(cPos[0])-2)+chr(ord(cPos[1])+1) in pieces or pieces[chr(ord(cPos[0])-2)+chr(ord(cPos[1])+1)][0] != color):
            moves.append(chr(ord(cPos[0])-2)+chr(ord(cPos[1])+1))
        if chr(ord(cPos[0])+2) <= 'h' and chr(ord(cPos[1])+1) <= '8' and (not chr(ord(cPos[0])+2)+chr(ord(cPos[1])+1) in pieces or pieces[chr(ord(cPos[0])+2)+chr(ord(cPos[1])+1)][0] != color):
            moves.append(chr(ord(cPos[0])+2)+chr(ord(cPos[1])+1))
        if dPos in moves:
            return True
        else:
            return False

    def bishopValidMove(self, cPos, dPos, color, pieces):
        moves = []
        k = None
        x = ord(cPos[0])
        y = ord(cPos[1])
        while k is None and x > ord('a') and y > ord('0'):
            x -= 1
            y -= 1
            if chr(x)+chr(y) in pieces.keys():
                k = pieces[chr(x)+chr(y)]
            else:
                k = None
            if k is None or k[0] != color:
                moves.append(chr(x)+chr(y))
        k = None
        x = ord(cPos[0])
        y = ord(cPos[1])
        while k is None and x < ord('h') and y > ord('0'):
            x += 1
            y -= 1
            if chr(x)+chr(y) in pieces.keys():
                k = pieces[chr(x)+chr(y)]
            else:
                k = None
            if k is None or k[0] != color:
                moves.append(chr(x)+chr(y))
        k = None
        x = ord(cPos[0])
        y = ord(cPos[1])
        while k is None and x > ord('a') and y < ord('8'):
            x -= 1
            y += 1
            if chr(x)+chr(y) in pieces.keys():
                k = pieces[chr(x)+chr(y)]
            else:
                k = None
            if k is None or k[0] != color:
                moves.append(chr(x)+chr(y))
        k = None
        x = ord(cPos[0])
        y = ord(cPos[1])
        while k is None and x < ord('h') and y < ord('8'):
            x += 1
            y += 1
            if chr(x)+chr(y) in pieces.keys():
                k = pieces[chr(x)+chr(y)]
            else:
                k = None
            if k is None or k[0] != color:
                moves.append(chr(x)+chr(y))
        if dPos in moves:
            return True
        else:
            return False

    def queenValidMove(self, cPos, dPos, color, pieces):
        return self.bishopValidMove(cPos, dPos, color, pieces) or self.rookValidMove(cPos, dPos, color, pieces)

    # does not take moving into check or castling
    def kingValidMove(self, cPos, dPos, color, pieces):
        moves = []
        if chr(ord(cPos[1])-1) >= '1' and (not cPos[0]+chr(ord(cPos[1])-1) in pieces or pieces[cPos[0]+chr(ord(cPos[1])-1)][0] != color):
            moves.append(cPos[0]+chr(ord(cPos[1])-1))
        if chr(ord(cPos[0])+1) <= 'h' and (not chr(ord(cPos[0])+1)+cPos[1] in pieces or pieces[chr(ord(cPos[0])+1)+cPos[1]][0] != color):
            moves.append(chr(ord(cPos[0])+1)+cPos[1])
        if chr(ord(cPos[0])-1) >= 'a' and (not chr(ord(cPos[0])-1)+cPos[1] in pieces or pieces[chr(ord(cPos[0])-1)+cPos[1]][0] != color):
            moves.append(chr(ord(cPos[0])-1)+cPos[1])
        if chr(ord(cPos[1])+1) <= '8' and (not cPos[0]+chr(ord(cPos[1])+1) in pieces or pieces[cPos[0]+chr(ord(cPos[1])+1)][0] != color):
            moves.append(cPos[0]+chr(ord(cPos[1])+1))
        if chr(ord(cPos[0])-1) >= 'a' and chr(ord(cPos[1])-1) >= '1' and (not chr(ord(cPos[0])-1)+chr(ord(cPos[1])-1) in pieces or pieces[chr(ord(cPos[0])-1)+chr(ord(cPos[1])-1)][0] != color):
            moves.append(chr(ord(cPos[0])-1)+chr(ord(cPos[1])-1))
        if chr(ord(cPos[0])+1) <= 'h' and chr(ord(cPos[1])-1) >= '1' and (not chr(ord(cPos[0])+1)+chr(ord(cPos[1])-1) in pieces or pieces[chr(ord(cPos[0])+1)+chr(ord(cPos[1])-1)][0] != color):
            moves.append(chr(ord(cPos[0])+1)+chr(ord(cPos[1])-1))
        if chr(ord(cPos[0])-1) >= 'a' and chr(ord(cPos[1])+1) <= '8' and (not chr(ord(cPos[0])-1)+chr(ord(cPos[1])+1) in pieces or pieces[chr(ord(cPos[0])-1)+chr(ord(cPos[1])+1)][0] != color):
            moves.append(chr(ord(cPos[0])-1)+chr(ord(cPos[1])+1))
        if chr(ord(cPos[0])+1) <= 'h' and chr(ord(cPos[1])+1) <= '8' and (not chr(ord(cPos[0])+1)+chr(ord(cPos[1])+1) in pieces or pieces[chr(ord(cPos[0])+1)+chr(ord(cPos[1])+1)][0] != color):
            moves.append(chr(ord(cPos[0])+1)+chr(ord(cPos[1])+1))
        if dPos in moves:
            return True
        else:
            return False

    def inCheck(self, color, pieces):
        for k in pieces.keys():
            if pieces[k][0] == color and pieces[k][2] == 'k':
                kingPos = k
                break
        check = False
        for k in pieces.keys():
            if pieces[k][0] != color:
                check = check or self.pieceValidMove(
                    pieces[k], k, kingPos, pieces)
        return check

    def willBeInCheck(self, piece):
        futureBoard = copy.deepcopy(self.pieces)
        del futureBoard[self.ChosenPieceLocation]
        futureBoard[self.CurrentUserLocation] = piece
        return self.inCheck(piece[0], futureBoard)

    def flipBoard(self):
        flipped = {}
        for k in self.pieces.keys():
            x = chr(abs((ord(k[0])-ord('h')))+ord('a'))
            y = chr(abs((ord(k[1])-ord('8')))+ord('1'))
            p = self.pieces[k]
            flipped[x+y] = p
        for k in self.pieces.keys():
            self.canvas.delete(self.ChosenPieceLoc[self.pieces[k]])
        self.pieces = copy.deepcopy(flipped)
        for k in self.pieces.keys():
            self.addPiece(self.pieces[k], k)

    def makeMove(self, color):
        self.moved = False
        self.color = color
        while not self.moved:
            self.update()

    def initBoard(self):
        self.update()

    def winState(self, color):
        openMoves = False
        for piece in self.pieces.keys():
            if self.pieces[piece][0] == color:
                validMoves = []
                for x in range(ord('a'), ord('h')+1):
                    x = chr(x)
                    for y in range(ord('1'), ord('8')+1):
                        y = chr(y)
                        if self.pieceValidMove(self.pieces[piece], piece, x+y, self.pieces):
                            validMoves.append(x+y)
                for loc in validMoves:
                    futureBoard = copy.deepcopy(self.pieces)
                    del futureBoard[piece]
                    futureBoard[loc] = self.pieces[piece]
                    openMoves = openMoves or not self.inCheck(
                        color, futureBoard)
                    if openMoves:
                        return None
        if self.inCheck(color, self.pieces):
            return "Checkmate"
        else:
            return "Stalemate"


if __name__ == "__main__":
    # create the chessboard
    board = ChessBoard()

    # here are method calls to the window manager class
    board.master.title("ChessBoard")
    board.master.maxsize(1000, 1000)
    board.initalBoard()
    board.bind('<Button-1>', board.GetUserCoordinates)

    # start the program
    while True:
        board.update()
