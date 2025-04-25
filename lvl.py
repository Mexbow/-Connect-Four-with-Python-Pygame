import tkinter as tk
import subprocess

def open_connect4_game(lvl):
    root.destroy()
    if lvl == 1:
        subprocess.run(["python", "C:/Users/mexbow/connect4/easy.py"])
    elif lvl == 2:
        subprocess.run(["python", "C:/Users/mexbow/connect4/medium.py"])
    else:
        subprocess.run(["python", "C:/Users/mexbow/connect4/hard.py"])
    
    subprocess.run(["python", "C:/Users/mexbow/connect4/GUI.py"])


root = tk.Tk()
root.title("Connect Four Levels")
root.geometry("910x780")
root.configure(bg="#1e7df0")


main_menu_frame = tk.Frame(root, width=910, height=780, padx=20, pady=20, bg="#1e7df0")
main_menu_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)


title_label = tk.Label(main_menu_frame, text="Select Level", font=("Helvetica", 80, "bold"), bg="#1e7df0", fg="white")
title_label.grid(row=0, column=0, pady=(0, 200))

play_button = tk.Button(main_menu_frame, width=8, height=1, text="Easy", font=("Helvetica", 30, "bold"), bg="#ff8164", fg="white", command=lambda: open_connect4_game(1),  relief=tk.GROOVE, borderwidth=10)
play_button.grid(row=1, column=0, pady=30)

play1_button = tk.Button(main_menu_frame, width=8, height=1, text="Medium", font=("Helvetica", 30, "bold"), bg="#ff8164", fg="white", command=lambda: open_connect4_game(2),  relief=tk.GROOVE, borderwidth=10)
play1_button.grid(row=2, column=0, pady=30)

play2_button = tk.Button(main_menu_frame, width=8, height=1, text="Hard", font=("Helvetica", 30, "bold"), bg="#ff8164", fg="white", command=lambda: open_connect4_game(3),  relief=tk.GROOVE, borderwidth=10)
play2_button.grid(row=3, column=0, pady=10)


root.mainloop()
