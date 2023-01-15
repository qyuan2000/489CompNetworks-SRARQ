import socket
import os
import time
import random
import string

def server_program():
    #host = socket.gethostname() # for test, should change to server ip
    host = "127.0.0.1"
    port = 1234
    server_socket = socket.socket()
    server_socket.bind((host, port)) 
    server_socket.listen(2)
    conn, address = server_socket.accept()  # accept new connection
    print ("Connection from: ", str(address))

    receivingWindow = [1, 2, 3, 4]
    buffer = []

    while(True):
        receivedMsg = conn.recv(1024).decode()
        if not receivedMsg:
            break
        ack, text = receivedMsg.split(' ; ', 2)
        print ("received sequence number is ", ack)
        expected_frame = receivingWindow[0]
        if(int(ack.strip()) == expected_frame):
            conn.send(str(ack).encode())
            print ("send ack ", ack)
            receivingWindow.remove(expected_frame)
            receivingWindow.append(receivingWindow[2]+1)
            expected_frame = receivingWindow[0]
        elif(int(ack.strip()) in receivingWindow):
            buffer.append(text)
            nak = "NAK" + str(expected_frame)
            conn.send(nak.encode())
            print("send nak ", nak)
            expected_frame = receivingWindow[1]
        else:
            continue

    
    server_socket.close()
    print ("close server")

if __name__ == '__main__':
    server_program()
