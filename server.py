import socketserver
import socket
import pickle
import data
import time
import sys

from ChessBoard import *

HEADER_SIZE = 10


class MyServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class MyHandler(socketserver.StreamRequestHandler):

    def handle(self):
        addr = self.request.getpeername()
        print(addr, 'connected.')

        color = ''
        data.playerCount += 1
        if data.playerCount == 1:
            print('white')
            color = 'white'

            dataToSend = {'playerColor': color,
                          'turn': data.turn, 'board': data.board}

            mymsg = pickle.dumps(dataToSend)
            mymsg = bytes(f'{len(mymsg):<{HEADER_SIZE}}', 'utf-8') + mymsg

            print("sending data")
            self.wfile.write(mymsg)
        elif data.playerCount == 2:
            print('black')
            color = 'black'

            data.turn = 'white'

            dataToSend = {'playerColor': color,
                          'turn': data.turn, 'board': data.board}

            mymsg = pickle.dumps(dataToSend)
            mymsg = bytes(f'{len(mymsg):<{HEADER_SIZE}}', 'utf-8') + mymsg
            print("sending data")

            self.wfile.write(mymsg)

        while data.playerCount != 2:
            time.sleep(1)

        while data.turn != color:
            # Sleep until its connected client's turn
            time.sleep(.25)

        # Main game loop
        while data.turn == color and data.playerCount == 2:

            print(data.turn)
            dataToSend = {'playerColor': color,
                          'turn': data.turn, 'board': data.board}

            print(data.board)
            mymsg = pickle.dumps(dataToSend)
            mymsg = bytes(f'{len(mymsg):<{HEADER_SIZE}}', 'utf-8') + mymsg
            print("sending data")

            self.wfile.write(mymsg)

            complete_info = b''
            rec_msg = True
            while True:
                receivedPackage = self.request.recv(16)
                if rec_msg:
                    x = int(receivedPackage[:HEADER_SIZE])
                    rec_msg = False
                complete_info += receivedPackage
                if len(complete_info) - HEADER_SIZE == x:
                    data.board = pickle.loads(complete_info[HEADER_SIZE:])
                    if data.turn == 'white':
                        data.turn = 'black'
                    else:
                        data.turn = 'white'
                    rec_msg = True
                    break

            while data.turn != color:
                # Sleep until its connected client's turn
                time.sleep(.25)


HOST = sys.argv[1] if len(sys.argv) == 2 else ''
PORT = 28635

server = MyServer((HOST, PORT), MyHandler)
print('Started')
print(HOST + ":" + str(PORT))
server.serve_forever()
