from socket import socket
from pickle import loads,dumps
from tkinter import *
import sys
import time
from Custom_Scrollable_Frame_widget import ScrollableFrame

# bugs noticed
# 1) hangs on close button
# 2) download file doesn't work
# 3) random U commands fail

x=None
contents=[]
holder=[]
current_dir="root"
def set_up_connection():
    global x
    x=socket()
    x.connect(('127.0.0.1',5000))
    print("Connection succes!!")

def recieve_file(file_name):
    global x
    f=open(f'client_folder/{file_name}','wb')
    data=True
    while data:
        # file requests loops indefinetly fix it!
        data = x.recv(1024)
        if data==b"FILE_END":
            break
        f.write(data)
    f.close()
    print("file saved succesfully")

def send_command_to_server(c,arg):
    global x,contents,current_dir
    if c==1:
        x.sendall(dumps("U"))
    if c==2:
        x.sendall(dumps(f"D,{arg}"))
        current_dir['text']="folder: "+arg
    if c==3:
        x.sendall(dumps(f"S,{arg}"))
        recieve_file(arg)
        return
    if c==4:
        x.sendall(dumps("C"))
        return
    data=x.recv(2048)
    data=loads(data)
    print("recieved value")
    print(data)
    contents=data

def ret_start_command(op,nm=""):
    # print("Staart commad")
    def start_commanding():
        # print("Start commanding called ",op,nm)
        # while True:
        # print('select an option to command to server!')
        # print("1 -> move up a dir")
        # print("2 -> move down a dir")
        # print("3 -> request for file download")
        # print("4 -> close")
        # option=int(input())
        option=op
        # name=""
        name=nm
        # if option in [2,3]:
        #     name=input("Enter name")
        send_command_to_server(option,name)

    return start_commanding

def update_content_frame():
    global contents,content_frame
    while True:
        content_copy=contents
        time.sleep(0.5)
        if content_copy!=contents:
            for x in holder:
                # x.destroy()
                content_frame.remove_frame(x)
            for x in contents:
                print("in for loop")
                if len(x.split('.'))>1:
                    d=Frame()
                    t=Label(d,text=x)
                    t.grid(row=0,column=0)
                    b=Button(d,text="Download",command=ret_start_command(3,x))
                    b.grid(row=0,column=1)
                    content_frame.insert_frame_end(d)
                else:
                    d = Frame()
                    t = Label(d, text=x)
                    t.grid(row=0,column=0)
                    b = Button(d, text="Open",command=ret_start_command(2,x))
                    b.grid(row=0,column=1)
                    content_frame.insert_frame_end(d)
                holder.append(d)



# from threading import Thread
# t=Thread(target=start_commanding)
# t.start()

from threading import Thread
from tkinter import font
# tkinter UI
root=Tk()
set_up_connection()
root.geometry('500x500')
title_frame=Frame(root)
title_frame.pack()
ff=font.Font(size=15)
Label(title_frame,text="FTP browser",font=font.Font(size=25)).pack()
current_dir=Label(title_frame,text=current_dir,font=font.Font(size=20))
current_dir.pack()
content_frame=ScrollableFrame(root,5,100)
content_frame.pack()
bot_frame=Frame(root)
bot_frame.pack()
back_btn=Button(bot_frame,text="Back",font=ff,command=ret_start_command(1))
back_btn.pack(side=LEFT)
cls_btn=Button(bot_frame,text="close",font=ff,command=lambda :sys.exit(0))
cls_btn.pack(side=LEFT)
t=Thread(target=update_content_frame)
t.start()
root.mainloop()