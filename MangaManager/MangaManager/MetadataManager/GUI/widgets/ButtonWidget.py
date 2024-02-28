import tkinter
from idlelib.tooltip import Hovertip


class ButtonWidget(tkinter.Button):
    def __init__(self, tooltip=None,image=None, *args, **kwargs):
        super(ButtonWidget, self).__init__(image=image, *args, **kwargs)

        if tooltip:
            self.configure(text=self.cget('text') + '  ⁱ')
            self.tooltip = Hovertip(self, tooltip, 20)