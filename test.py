import tkinter as tk
root = tk.Tk()
canvas = tk.Canvas(root, width=500, height=500)
canvas.pack()
img = tk.PhotoImage(file='wall.png')
canvas.create_image(250, 250, image=img)
# img = tk.PhotoImage(file='wall.png')
# canvas.create_image(500, 500, image=img)
root.mainloop()
