import socket
import pickle
import time
from ChessBoard import *

HOST = sys.argv[1] if len(sys.argv) == 2 else 'localhost'
PORT = 28635

HEADER_SIZE = 10

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

# data = {'playerColor': color,'turn': data.turn, 'board': data.board}
data = {}
board = ChessBoard()
board.master.title("ChessBoard")
board.master.maxsize(1000, 1000)
board.initalBoard()
board.bind('<Button-1>', board.GetUserCoordinates)
isInitialized = False
while True:
    complete_info = b''
    rec_msg = True
    if len(data) > 0:
        print(data['board'])
        print(data['turn'])

        if(not isInitialized):
            isInitialized = True
            board.initBoard()
        if data['board'] == "Checkmate":
            print("Congratulations! You Win!")
            break
        if data['board'] == "Stalemate":
            print("Stalemate")
        if (data['playerColor'] == 'white' and data['turn'] == 'white') or (data['playerColor'] == 'black' and data['turn'] == 'black'):
            board.pieces = data['board']
            board.flipBoard()
            if board.winState(data['playerColor'][0].upper()):
                packageWithoutHeader = pickle.dumps(
                    board.winState(data['playerColor'][0].upper()))
                packageWithHeader = bytes(
                    f'{len(packageWithoutHeader):<{HEADER_SIZE}}', 'utf-8') + packageWithoutHeader
                client_socket.send(packageWithHeader)
                print(packageWithoutHeader)
                break
            board.makeMove(data['playerColor'][0].upper())
            packageWithoutHeader = pickle.dumps(board.pieces)
            packageWithHeader = bytes(
                f'{len(packageWithoutHeader):<{HEADER_SIZE}}', 'utf-8') + packageWithoutHeader
            client_socket.send(packageWithHeader)
        else:
            print('not my turn')

    # RECEIVE THE DATA FROM THE SERVER
    while True:
        mymsg = client_socket.recv(256)
        if(mymsg == b''):
            print('empty')
            break
        if rec_msg:
            x = int(mymsg[:HEADER_SIZE])
            rec_msg = False
        complete_info += mymsg
        # BREAK FROM THE LOOP WHEN WHOLE MESSAGE IS RECEIVED
        if len(complete_info) - HEADER_SIZE == x:
            data = pickle.loads(complete_info[HEADER_SIZE:])
            rec_msg = True
            break
