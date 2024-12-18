from threading import Thread
from tkinter import *
from tkinter import font
from tkinter import Tk
import time
import random
import string
text_lis={}
import sys
root=Tk()
let_entry=None
t=None
game_not_over=True
letter_cnt=0
got_cnt=0
start_time=None
def keep_checking():
    global  let_entry,text_lis,letter_cnt,start_time
    while(game_not_over):
        letter=let_entry.get().lower()
        print("THread checked and got letter :",letter)
        # print("got ltter is",letter)
        for x in text_lis.keys():
            if text_lis[x]['text']==letter:
                text_lis[x]['text']=random.choice(string.ascii_lowercase)
                letter_cnt+=1
                let_entry.delete(0, END)
                # let_entry.pack()
                break
        if(letter_cnt==got_cnt):
            frame1.destroy()
            let_entry.destroy()
            l=Label(root,text=f"Game Over \n Your speed is {round((time.clock()-start_time)/got_cnt,2)} letter/sec",font=ff)
            l.pack()
            time.sleep(5)
            sys.exit(0)


def start_game():
    global frame1,text_lis,let_entry,got_cnt,start_time
    got_cnt=int(letters.get())
    frame1.destroy()
    frame1=Frame(root)
    start_time=time.clock()
    frame1.pack()
    lis=['a','b','c','d']
    cnt=0
    bigfont=font.Font(size=50)
    for x in range(len(lis)):
        text_lis[lis[x]]=Label(frame1,text=lis[x],font=bigfont,relief=RAISED)
        text_lis[lis[x]].grid(row=0,column=cnt,padx=30,pady=30)
        cnt+=1
    let_entry = Entry(root,font=ff)
    let_entry.pack()
    t=Thread(target=keep_checking)
    t.start()




ff=font.Font(size=20)
root.geometry("500x300")
heading=Label(root,text="Typing Game",font=ff)
heading.pack()
frame1=Frame(root)
frame1.pack()

start=Button(frame1,text="Start Game",font=ff,command=start_game)
start.pack()
l=Label(frame1,text="Letters:",font=ff)
l.pack()
letters=Entry(frame1,font=ff,text="25")
letters.pack()
exit=Button(root,text="Exit Game",font=ff,command=lambda:(root.destroy()))
exit.pack()
root.mainloop()