import tkinter as tk
import maze_maker as mm

def key_down(event):
    global key
    key = event.keysym


def key_up(event):
    global key
    key = ""


def main_proc():
    global cx, cy, mx, my, tori
    if key == "Up": 
        my -= 1
        tori = tk.PhotoImage(file=gazou[1])#移動時の画像の指定
        canvas.create_image(cx, cy, image=tori, tag="kokaton") 
    if key == "Down": 
        my += 1
        tori = tk.PhotoImage(file=gazou[1])#移動時の画像の指定
        canvas.create_image(cx, cy, image=tori, tag="kokaton")
    if key == "Left": 
        mx -= 1
        tori = tk.PhotoImage(file=gazou[1])#移動時の画像の指定
        canvas.create_image(cx, cy, image=tori, tag="kokaton")
    if key == "Right": 
        mx += 1
        tori = tk.PhotoImage(file=gazou[1])#移動時の画像の指定
        canvas.create_image(cx, cy, image=tori, tag="kokaton")
    if maze_lst[mx][my] == 1:
        tori = tk.PhotoImage(file=gazou[2])#衝突時の画像の指定
        canvas.create_image(cx, cy, image=tori, tag="kokaton")
        if key == "Up": my += 1
        if key == "Down": my -= 1
        if key == "Left": mx += 1
        if key == "Right": mx -= 1
    cx, cy = mx*100+50, my*100+50
    canvas.coords("kokaton", cx, cy)
    root.after(100, main_proc)


if __name__ == "__main__":
    root = tk.Tk()
    root.title("迷えるこうかとん")
    canvas = tk.Canvas(root, width=1500, height=900, bg="black")
    canvas.pack()

    maze_lst = mm.make_maze(15, 9)
    mm.show_maze(canvas, maze_lst)

    mx, my = 1, 1
    cx, cy = mx*100+50, my*100+50
    gazou = ["fig/0.png", "fig/3.png", "fig/8.png"] #画像のリスト
    tori = tk.PhotoImage(file=gazou[0])#初期画像の指定
    canvas.create_image(cx, cy, image=tori, tag="kokaton")
    key = ""
    root.bind("<KeyPress>", key_down)
    root.bind("<KeyRelease>", key_up)
    main_proc()
    root.mainloop()