from tkinter import *
from TileButton import TiledButton

class TabbedWidget(Frame):
    def __init__(self,parent,h,w,tab_dir=None,font=None):
        self.h,self.w=h,w
        self.font=font
        super(TabbedWidget, self).__init__(parent)
        self.frames={} # frames storage
        self.main_frame=Frame(self,bg='yellow')
        self.button_frame=Frame(self,bg='blue')
        self.button_frame.pack(side=tab_dir)
        self.main_frame.pack(side=tab_dir)
        # bb=Button(self.main_frame,text="tthis").pack()
        # bb1=Button(self.button_frame,text="tthis").pack()
        self.buttons={}
        self.current_frame=None

    def get_tab_area(self):
        # returns a tab area so that we can use it declaration of the to-be-inserted-tab
        return self.main_frame

    def add_tab(self,name,frame):
        self.temp=self.current_frame
        if self.temp is not None:
            self.temp.pack_forget()
        but = TiledButton(self.button_frame, text=name, command=self.resolve_click(name), h=self.h, w=self.w,
                          font=self.font)
        self.buttons[name] = but
        self.frames[name] =frame
        but.pack()
        self.current_frame=self.frames[name]
        self.current_frame.pack()
        # but=Button(self.button_frame,text=name,command=self.resolve_click(name))

    def resolve_click(self,name):
        # a function factory to create ease-of-use
        print("resolve click called")
        def return_click():
            print("Name given is ",name)
            # to not load an aldready loaded window
            if self.current_frame is not self.frames[name]:
                self.current_frame.pack_forget()
                self.frames[name].pack()
                self.current_frame=self.frames[name]
        return return_click

# driver code
root=Tk()
from tkinter import font
w=TabbedWidget(root,h=25,w=70,font=font.Font(size=20))
w.pack()
f=Frame(w.get_tab_area())
# f=Frame(root)
f2=Frame(w.get_tab_area())
Label(f2,text="Label in frame 2").pack()
Entry(f2).pack()
Button(f,text="Button in frame 1").pack()
w.add_tab(name="f1 frame",frame=f)
w.add_tab(name="f2 frame",frame=f2)
root.mainloop()



