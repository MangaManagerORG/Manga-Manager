import tkinter

from MangaManager_ThePromidius.Common.GUI.widgets import TreeviewWidget


class App:
    def __init__(self):
        self.app = tkinter.Tk()
        self.tv = TreeviewWidget(self.app)
        self.tv.pack()
        self.tv.insert("end", text="texto1")
        self.tv.insert("end1", text="texto1")
        self.tv.insert("end2", text="texto1")
        self.tv.insert("end3", text="texto1")
        self.tv.insert("end4", text="texto1")
        self.tv.insert("end5", text="texto1")



        button = tkinter.Button(self.app, command=self.run)
        button.pack()

        self.app.mainloop()

    def run(self, event=None):
        print("dasdd")

if __name__ == '__main__':

    app = App()