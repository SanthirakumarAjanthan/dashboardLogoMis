# work in progress!!
from tkinter import Tk
from tkinter import *
from tkinter import font
import time
import random

root=Tk()
last_pressed=None
cnt=0
wait_press=False
aldready_pressed=[]
def random_blinken_lights():
    global lights,last_pressed,wait_press,aldready_pressed
    while(cnt!=4):
        for x in aldready_pressed:
            x['bg'] = 'lightblue'
            time.sleep(0.5)
            x['bg'] = 'blue'
        last_pressed=random.choice(buttons)
        aldready_pressed.append(last_pressed)
        last_pressed['bg']='lightblue'
        time.sleep(0.7)
        last_pressed['bg']='blue'
        while wait_press is False:
            pass
        wait_press=False

    print('end')

def all_blinken_red():
    global buttons
    for x in buttons:
        x['bg']='red'
    time.sleep(0.7)
    for x in buttons:
        x['bg']='blue'

def pressed(x):
    global last_pressed,buttons,cnt,wait_press
    if buttons[x]==last_pressed:
        cnt+=1
    else:
        cnt=0
        all_blinken_red()
    wait_press=True

root.geometry('500x400')
f1=Frame(root)
f2=Frame(root)
f1.pack()
f2.pack()
lights=[Button(f1,text=f'   {x}    ',bg='lightgrey') for x in range(4)]
for x in lights:
    x.pack(side=LEFT)
buttons=[Button(f2,text=f' '*5,bg='blue',font=font.Font(size=35),command=lambda :pressed(x)) for x in range(16)]
cnt=0
for x in range(4):
    for y in range(4):
        buttons[cnt].grid(row=x,column=y)
        cnt+=1
import threading
t=threading.Thread(target=random_blinken_lights)
t.start()
root.mainloop()