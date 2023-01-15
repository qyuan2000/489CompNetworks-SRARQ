import socket
import os
import time
import random
import string
import math


def client_program():
    host = '10.12.160.2' # for test, should change to server ip
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
        #判断是否需要传输，如果是，send frame
        if (dataCnt < 200) and (len(sendingWindow) <= 4):
            # 判断是否resend, 并send一个frame：win_start / win_last
            if (repeatFlag == 1): # resend win_start frame
                # 判断是否到文件结尾
                if(len(data) - frameSize*(win_start-1) < frameSize):
                    frame = data[(win_start-1)*frameSize : len(data)]
                else:
                    frame = data[(win_start-1)*frameSize : win_start*frameSize]
                frame = str(win_start) + ' ; ' + frame  # sequence number = dataCnt+1
                client_socket.send(frame.encode())
                print ("resend frame ", win_start)
            else: # send new frame
                # 判断是否到文件结尾
                if(len(sendingWindow) < 4):
                    if(len(data) - frameSize*dataCnt < frameSize):
                        frame = data[dataCnt*frameSize : len(data)]
                    else:
                        frame = data[dataCnt*frameSize : (dataCnt+1)*frameSize]
                    dataCnt+=1
                    frame = str(dataCnt) + ' ; ' + frame  # sequence number = dataCnt
                    if(random.random() < 0.9): # drop frame at 10% possibility
                        client_socket.send(frame.encode())
                    win_last+=1
                    sendingWindow.append(dataCnt)
                    print ("send frame ", dataCnt)
                    print ("sending window now is ", sendingWindow)
        elif (dataCnt >= 200): # data 全部传输
            break
                         
        
        time.sleep(0.5)
        # 接收ack
        client_socket.settimeout(1)
        try:
            ack_received = client_socket.recv(1024).decode()
        except socket.timeout:
            continue
        print ("receive ack", ack_received)
        ack_expected = sendingWindow[0]
        # 判断是否为nak
        if(str(ack_received).strip()[0:3] == 'NAK'):
            repeatFlag = 1
        else:
            if(int(ack_received.strip()) != ack_expected) and (len(sendingWindow) == 4): # win_start frame is lost
                repeatFlag = 1
                sendingWindow.remove(int(ack_received.strip()))
            else: # correct ack is received
                repeatFlag = 0
                del(sendingWindow[0])
                if(len(sendingWindow) > 0):
                    win_start = sendingWindow[0]
                else:
                    win_start = dataCnt

    client_socket.close() 
    print ("Socket closed")

if __name__ == '__main__':
    client_program()




