import tkinter as tk

app = tk.Tk()
app.title("factsearch")
logo = tk.PhotoImage(file='factoorium.gif')
logoLabel = tk.Label(app, image=logo)
logoLabel.pack(side='left')
app.mainloop()
