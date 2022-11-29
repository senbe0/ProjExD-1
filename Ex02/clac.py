import tkinter as tk
import tkinter.messagebox as tkm

root = tk.Tk
root.title("tk")
root.geometry("300x500")


for i in range(9):
    button =tk.Button(root, text=i)
    button.width(4)