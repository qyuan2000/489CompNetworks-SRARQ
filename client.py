import socket
import os
import time
import random
import string
import math


def client_program():
    host = socket.gethostname() # for test, should change to server ip
    port = 1234
    client_socket = socket.socket()
    client_socket.connect((host, port)) # connect to server

    print ("Client-Server Connect")
    windowSize = 4
    win_start = 1 # = ack_expected
    win_last = 4 # last frame in window
    ack_expected = 1 # store received ack
    sendingWindow = []
    filePath = "./shakespeare.txt"
    repeatFlag = 0 # flag=1 means resend win_start frame
    with open(filePath) as f:
        data = f.read()
    frameSize = math.floor(len(data)/200)# 1000 bytes per frame
    dataCnt = 0 # count the start byte index of data

    while(1):
        # check if there is sending request
        if (dataCnt < 200) and (len(sendingWindow) <= 4):
            # check if resend
            if (repeatFlag == 1): # resend win_start frame
                # check EOF
                if(len(data) - frameSize*(win_start-1) < frameSize):
                    frame = data[(win_start-1)*frameSize : len(data)]
                else:
                    frame = data[(win_start-1)*frameSize : win_start*frameSize]
                frame = str(win_start) + ' ; ' + frame  # sequence number = dataCnt+1
                client_socket.send(frame.encode())
                print ("resend frame ", win_start)
    
            else: # send new frame
                # check EOF
                if(len(sendingWindow) < 4):
                    if(len(data) - frameSize*dataCnt < frameSize):
                        frame = data[dataCnt*frameSize : len(data)]
                    else:
                        frame = data[dataCnt*frameSize : (dataCnt+1)*frameSize]
                    dataCnt+=1
                    frame = str(dataCnt) + ' ; ' + frame  # sequence number = dataCnt
                    if(random.random() < 0.9): # drop frame at 10% possibility
                        client_socket.send(frame.encode())
                    if(dataCnt > 4): win_last+=1
                    sendingWindow.append(dataCnt)
                    print ("send frame ", dataCnt)
                    print ("sending window now is ", sendingWindow)
                else:
                    repeatFlag = 1
                    win_start = sendingWindow[0]
        elif (dataCnt >= 200): # all data transmitted
            break
                         
        
        time.sleep(0.5)
        # receive respond
        client_socket.settimeout(1)
        try:
            ack_received = client_socket.recv(1024).decode()
        except socket.timeout:
            continue
        print ("receive ack", ack_received)
        ack_expected = sendingWindow[0]
        # check if nak
        ack_received = str(ack_received).strip()
        if(ack_received[0:3] == 'NAK'):
            repeatFlag = 1
            win_start = int(ack_received[3: len(ack_received)])
            sendingWindow = [win_start]
        else:
            if(int(ack_received.strip()) != ack_expected) and (win_last-win_start == 4): # win_start frame is lost
                repeatFlag = 1
                sendingWindow = [win_last+1]
            elif (int(ack_received.strip()) != ack_expected) and (win_last-win_start < 4):
                continue
            else: # correct ack is received
                if(repeatFlag == 1): 
                    win_start = win_last+1
                    sendingWindow = []
                else:
                    del(sendingWindow[0])
                    if(len(sendingWindow) > 0):
                        win_start = sendingWindow[0]
                    else:
                        win_start = dataCnt+1
                repeatFlag = 0

                

    client_socket.close() 
    print ("Socket closed")

if __name__ == '__main__':
    client_program()




