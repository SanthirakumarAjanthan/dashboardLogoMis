from tkinter import *
from tkinter import font
from tkinter import Tk
import threading
import time
root=Tk()
def start_time():
    global hr_bx,min_bx,sec_bx
    seconds=int(hr_bx.get())*60**2+int(min_bx.get())*60+int(sec_bx.get())
    print(seconds)
    while(seconds>0):
        ttl=seconds
        hr=ttl//(60**2)
        ttl%=(60**2)
        min=ttl//60
        ttl%=60
        sec=ttl
        print(hr,min,sec)
        time.sleep(1)
        seconds-=1

def func():
    t=threading.Thread(target=start_time)
    t.start()

ff=font.Font(size=30)
title=Label(root,text="CountDown Timer",font=ff)
title.pack()
f1=Frame(root)
hr_bx=Spinbox(f1,from_=0,to=24,font=ff,width=5)
# hr_bx.pack()
hr_bx.grid(row=0,column=0)

min_bx=Spinbox(f1,from_=0,to=59,font=ff,width=5)
min_bx.grid(row=0,column=1)

sec_bx=Spinbox(f1,font=ff,width=5,values=['am','pm'])
sec_bx.grid(row=0,column=2)

f1.pack()
btn=Button(root,text="Start Counting",font=ff,command=func)
btn.pack()

root.mainloop()