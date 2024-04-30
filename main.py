from automation import automation_sequence
from window_gui import WindowsGui
import tkinter as tk

def main():
    root = tk.Tk()
    gui = WindowsGui(root, automation_sequence)
    root.mainloop()

if __name__ == "__main__":
    main()