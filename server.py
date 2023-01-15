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
    win_last = 4
    buffer = []

    while(True):
        receivedMsg = conn.recv(1024).decode()
        if not receivedMsg:
            break
        ack, text = receivedMsg.split(' ; ', 2)
        print ("received sequence number is ", ack)
        expected_frame = receivingWindow[0]
        if(int(ack.strip()) == expected_frame):
            if(random.random() < 0.9): 
                conn.send(str(ack).encode())
            print ("send ack ", ack)
            receivingWindow.remove(expected_frame)
            win_last += 1
            receivingWindow.append(win_last)
            expected_frame = receivingWindow[0]
        else:
            nak = "NAK" + str(expected_frame)
            conn.send(nak.encode())
            print("send nak ", nak)
            if(int(ack.strip()) in receivingWindow): 
                receivingWindow.remove(int(ack.strip()))
                buffer.append(text)
            win_last += 1
            receivingWindow.append(win_last)
	
    
    server_socket.close()
    print ("close server")

if __name__ == '__main__':
    server_program()
