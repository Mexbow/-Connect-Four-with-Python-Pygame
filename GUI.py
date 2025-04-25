import tkinter as tk
import subprocess

def open_connect4_game():
    root.destroy()
    subprocess.run(["python", "C:/Users\mexbow/connect4/lvl.py"])
    
def quit_game():
    root.destroy()


root = tk.Tk()
root.title("Connect Four Main Menu")


root.geometry("910x780")


root.configure(bg="#1e7df0")


main_menu_frame = tk.Frame(root, width=910, height=780, padx=20, pady=20, bg="#1e7df0")
main_menu_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)


title_label = tk.Label(main_menu_frame, text="Connect Four", font=("Helvetica", 80, "bold"), bg="#1e7df0", fg="white")
title_label.grid(row=0, column=0, pady=(0, 200))  # Use pady=(20, 0) to add space above the title

play_button = tk.Button(main_menu_frame, width=8, height=1, text="Play", font=("Helvetica", 30, "bold"), bg="#ff8164", fg="white", command=open_connect4_game,  relief=tk.GROOVE, borderwidth=10)
play_button.grid(row=1, column=0, pady=30)

quit_button = tk.Button(main_menu_frame, width=8, height=1, text="Quit", font=("Helvetica", 30, "bold"), bg="#ece75f", fg="white", command=quit_game,  relief=tk.GROOVE, borderwidth=10)
quit_button.grid(row=2, column=0, pady=10)


root.mainloop()
