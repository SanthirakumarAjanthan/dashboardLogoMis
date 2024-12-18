from tkinter import *
from socket import socket
from pickle import loads, dumps
from os import system
import os

host, port = '127.0.0.1', 5000
x = socket()
x.bind((host, port))
x.listen(1)
con, addr = x.accept()

# commands
# U-> go one directory up
# D,name -> go one directory down
# S,file_name -> send the given file name
# C-> end the connection

def wait_for_commands():
    global con, addr
    while True:
        command = con.recv(1024)
        if command:
            command = loads(command)
            code = command[0]
            print(command)
            if code is "U":
                os.chdir("..")
                data = dumps(os.listdir())
                con.sendall(data)
            elif code is "D":
                print(command[1:])
                os.chdir(f"{command[2:]}")
                data = dumps(os.listdir())
                con.sendall(data)
            elif code is "S":
                send_file(command[2:])
            elif code is "C":
                print('client ended connection!')
                con.close()
                x.close()
            else:
                print("Unidentified command code received!!")
                return
        else:
            pass


def send_file(name):
    global con
    f = open(f"{name}", "rb")
    # make sure to use rb option as you are transfering over  byte stream
    print(len(f.read()))
    data = f.read(1024)
    while data:
        con.sendall(data)
        data = f.read(1024)
    con.sendall(b"FILE_END")
    print("file sent!!")


# send_file("Typing_game.py")
import threading

t = threading.Thread(target=wait_for_commands)
t.start()