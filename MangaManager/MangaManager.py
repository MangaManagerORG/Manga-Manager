#!/usr/bin/env python3
import tkinter as tk

from MangaTaggerLib.MangaTagger import MangataggerApp
from CoverManagerLib.CoverManager import CoverManagerApp
# Todo: Add cover setter
tools = [CoverManagerApp, MangataggerApp]
def main():
    selected_tool = False
    print("Select Tool")
    print("1 - Cover Setter")
    print("2 - Manga Tagger")
    print("3 - Volume Setter")
    while not selected_tool:
        selection = input("Select Number >")
        try:
            selection = int(selection)-1
        except:
            print("Wrong input. Select the number of the tool")
        selected_tool = True
    print(selection)

    root = tk.Tk()
    if selection == 3:
        print("Not implemented yet")

    app = tools[selection](root)
    app.start_ui()
    app.run()

if __name__ == "__main__":
    while True:
        main()
