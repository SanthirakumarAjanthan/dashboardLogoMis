from tkinter import filedialog
from tkinter import Tk
from tkinter import messagebox

path = filedialog.askdirectory()
import os

cur_frmts = []

print(os.listdir(path))

os.chdir(path)

for x in os.listdir(path):
    lis = x.split('.')
    if len(lis) < 2:
        pass
        # unrecognised format
    else:
        frmt = lis[-1]
        if frmt in cur_frmts:
            os.system(f'move "{x}" "{frmt}_files"')
        else:
            cur_frmts.append(frmt)
            os.makedirs(f"{frmt}_files")
            os.system(f'move "{x}" "{frmt}_files"')

messagebox.showinfo("Done!", "Files Sorted successfully!!")



