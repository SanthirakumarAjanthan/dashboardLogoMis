from tkinter import Tk
from tkinter import font
from tkinter import *
import threading
import time
from tkinter.ttk import Progressbar
from tkinter import messagebox
import random
from tkinter import filedialog
# name,i=filedialog.askopenfile()

def do():
	global l,hack_bar,name
	l.pack()
	# lines=open("C:\\Users\\Balarubinan\\Desktop\\Random files\\total_base_env_pakages_list.txt", 'r').read()
	lines=open("C:\\Users\\Balarubinan\\Documents\\StackNQueue.cpp",'r').read()
	for x,y in enumerate(lines):
		l.insert(END, y) # for inserting line by line
		# print(random.randrange(0,1))
		time.sleep(random.choice([0.05,0.1])) # for slow loading effect typing speed
		l.see("end") # for autoscroll to end
		hack_bar['value']=x/len(lines)*100
		hack_bar.pack()
	messagebox.showinfo("Hacked","Access granted")


root=Tk()
root.title("HackSploit Terminal")
# root.iconbitmap()
l=Text(root,fg="limegreen",bg="black")
l.pack()
t=threading.Thread(target=do) # doing threading
t.start()
hack=Label(root,text="Hack in progress:")
hack.pack()
hack_bar=Progressbar(root,orient=HORIZONTAL,length=500)

root.configure(bg="black")
# butt=Button(root,text="start hack!",command=do)
# butt.pack()
root.mainloop()