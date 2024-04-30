import tkinter as tk
from tkinter import messagebox, simpledialog, font
import time
import pyautogui
import threading
import webbrowser
from PIL import Image, ImageTk
from automation import StopAutomationException


class WindowsGui:
    def __init__(self, root, automation_sequence):
        self.root = root
        # configure root
        self.root.title("Automation Control")
        self.root.geometry("540x460")
        
        # pin the gui to top
        root.attributes('-topmost', True)

        self.defaultFont = font.nametofont("TkDefaultFont") 
        self.defaultFont.configure(family="Roboto") 


        self.photos_taken = 0
        self.total_photos = 0
        self.is_running = False

        self.resize_logo()
        self.create_widgets()

        self.stop_event = threading.Event()
        self.automation_sequence = automation_sequence

    def resize_logo(self):
        logo = Image.open("logo.png")
        factor = 1.5
        new_width = int(logo.width / factor)
        new_height = int(logo.height / factor)
        resized_logo = logo.resize((new_width, new_height), Image.Resampling.LANCZOS)
        self.logo_image = ImageTk.PhotoImage(resized_logo)

    def open_website(self):
        url = "https://doofront-app-ai-v1-fv2jh7djwq-uc.a.run.app/"
        webbrowser.open_new(url)

    def create_widgets(self):
        #Frame for Heading and Logo
        frame = tk.Frame(self.root, bg='#D6974D')
        frame.pack(fill='x', pady=5) 

        logo_label = tk.Label(frame, image=self.logo_image, bg='#D6974D')
        logo_label.pack(side='left', padx=10, pady=10, anchor='nw')

        welcome_message = "Welcome to DoorFront Automation!"
        welcome_label = tk.Label(frame, text=welcome_message, bg='#D6974D', fg='white', font=("Roboto", 12, "bold"))
        welcome_label.pack(side="left", padx=5)

        #Instructions
        message1 = "How to Use:\n\nStep 1. Log into the DoorFront and navigate to Explore page.\n\nStep 2. Please make sure that the Google Street View is facing one side of the street.\n\nStep 3. Click Start Automation button and Select the total images you want to capture."
        messsage_label = tk.Label(self.root, text=message1, font=("Roboto", 10))
        messsage_label.pack(padx=2, pady=5)

        #Buttons
        self.DoorFront_button = tk.Button(self.root, text="Open DoorFront", command=self.open_website, bg='#D6974D', fg='black')
        self.DoorFront_button.pack(padx=10, pady=10)

        self.start_button = tk.Button(self.root, text="Start Automation", command=self.start_automation, bg='green', fg='white')
        self.start_button.pack(padx=10, pady=10)

        self.stop_button = tk.Button(self.root, text="Stop Automation", command=self.stop_automation, bg='red', fg='white')
        self.stop_button.pack(padx=10, pady=10)

        self.status_label = tk.Label(self.root, text="No photos requested yet.")
        self.status_label.pack(pady=20)

    def start_automation(self):
        #ask how many photos to be taken
        valid_input = self.ask_question()

        if valid_input and not self.is_running:
            self.is_running = True
            self.stop_event.clear()

            automation_thread = threading.Thread(target=self.automation_sequence, args=(self, self.total_photos, self.stop_event))
            automation_thread.start()

    def ask_question(self):
        answer = simpledialog.askinteger("Input", "Enter the number of photos you want to take (Integer)", parent=self.root)
        if answer is not None:
            if answer > 0:
                self.total_photos = answer
                self.update_status()
                return True
            else:
                messagebox.showerror("Error", "Please enter a positive integer.")
                return False
        return None

    def stop_automation(self):
        self.is_running = False
        self.stop_event.set()  # Set the stop event
        messagebox.showinfo("Info", "Stopping Automation...")

    def get_user_confirmed_position(self, target):
        messagebox.showinfo(
            "Move Cursor",
            f"Program is unable to locate the {target} location on screen.\nPlease confirm that you will move the cursor to the {target} button location."
        )

        countdown_label = tk.Label(self.root, text="10", font=("Roboto", 24))
        countdown_label.pack()
        for i in range(10, 0, -1):
            if self.stop_event.is_set():
                countdown_label.pack_forget()
                raise StopAutomationException
            countdown_label.config(text=str(i))
            self.root.update()
            time.sleep(1)
        countdown_label.pack_forget()
        return pyautogui.position()
            
    def update_status(self):
        self.remaining = self.total_photos - self.photos_taken
        self.status_label.config(text=f"Captured: {self.photos_taken} photos. Remaining: {self.remaining}.")
