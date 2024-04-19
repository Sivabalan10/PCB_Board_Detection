import threading
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import cv2
import sys
import subprocess
import os
from PIL import ImageTk, Image

class Detection:
    def __init__(self, video_path):
        self.cap = cv2.VideoCapture("C:/Users/SIVA/Downloads/WhatsApp Video 2024-04-19 at 9.34.26 PM.mp4")

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PCB_DETECTOR")
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        frame_width = int(screen_width)  
        frame_height = int(screen_height)  
        print(frame_height)
        print(frame_width)
        x_coordinate = (screen_width - frame_width) // 2
        y_coordinate = (screen_height - frame_height) // 2
        self.geometry(f"{frame_width}x{frame_height}+{x_coordinate}+{y_coordinate}")
        self.frames = {}
        self.login_frame = LoginPage(self)
        self.ip_address_frame = IPAddressPage(self)

    def show_frame(self, frame_name):
        if frame_name == "login":
            self.login_frame.pack(fill='both', expand=True)
            self.ip_address_frame.pack_forget()
            self.welcome_frame.pack_forget()
        elif frame_name == "ip_address":
            self.login_frame.pack_forget()
            self.ip_address_frame.pack(fill='both', expand=True)
          

        elif frame_name == "welcome":
            self.login_frame.pack_forget()
            self.ip_address_frame.pack_forget()
            self.welcome_frame.pack(fill='both', expand=True)
            self.welcome_frame.show_menu()



class LoginPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.create_widgets()

    def create_widgets(self):
        height = self.winfo_screenheight()
        const1 = int(height / 33.23)  # 26
        const2 = int(height / 8.64)  # 100
        const3 = int(height / 43.2)  # 20
        const4 = int(height / 54)  # 16
        const5 = int(height / 21.6)  # 40

        label = ttk.Label(self, text="Login Page", font=('Times New Roman', const1))  
        label.pack(pady=(const2, const3))  # Increased top padding

        username_label = ttk.Label(self, text="Username:", font=('Times New Roman', const4)) 
        username_label.pack()
        self.username_entry = ttk.Entry(self, font=('Times New Roman', const4))  
        self.username_entry.pack()

        password_label = ttk.Label(self, text="Password:", font=('Times New Roman', const4))  
        password_label.pack()
        self.password_entry = ttk.Entry(self, show="*", font=('Times New Roman', const4))  
        self.password_entry.pack()

        self.login_button = ttk.Button(self, text="Login", command=self.handle_login, style='Login.TButton', width=14, )
        self.login_button.pack(pady=(const3, const5))
        button_font = ("Arial", const4)
        style = ttk.Style()
        style.configure('Login.TButton', font=button_font)

    def handle_login(self):
        username = self.username_entry.get() 
        password = self.password_entry.get()  
        if username == "demo":
            login_status = True
        if login_status:
            messagebox.showinfo("Login Successful", "Welcome, " + username + "!")
            self.master.show_frame("ip_address")
        else:
            print("invalid username and password")
            messagebox.showerror("Login Failed", "Invalid username or password.")

class IPAddressPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.count = 2  
        height = self.winfo_screenheight()
        const1 = int(height / 72)  # 12
        const3 = int(height / 43.2)  # 20
        const2 = int(height / 57.6)  # 15
        const4 = int(height / 54)  # 16
        label = ttk.Label(self, text="IP Address", font=('Helvetica', 20)) 
        label.pack(pady=(100, 20))
        ip_frame = ttk.Frame(self)
        ip_frame.pack(pady=10)
        ip_labels = ["IP Address 1:"]
        self.ip_entries = []
        self.success_labels = [] 


        for i in range(1):
            ip_label = ttk.Label(ip_frame, text=ip_labels[i], font=("Times New Roman", const1))
            ip_label.grid(row=i, column=0, padx=const2, pady=const2)

            ip_entry = ttk.Entry(ip_frame, font=('Helvetica', const4), width=const3)
            ip_entry.grid(row=i, column=1, padx=const2, pady=const2)
            self.ip_entries.append(ip_entry)

            test_button = ttk.Button(ip_frame, text="Test", width=const2, style="test.TButton",
                                     command=lambda i=i: self.handle_test(i))
            test_button.grid(row=i, column=2, padx=const2, pady=const2)
            button_font = ("Times New Roman", const1)
            style = ttk.Style()
            style.configure('test.TButton', font=button_font)
            success_label = ttk.Label(ip_frame, text="", font=const1)
            success_label.grid(row=i, column=3, padx=const2, pady=const2)
            self.success_labels.append(success_label)

            self.proceed_button = ttk.Button(self, text="Proceed", style="proceed.TButton", width=const3,
                                         command=self.handle_proceed)
            self.proceed_button.pack(pady=const2)
            button_font = ("Times New Roman", const2)
            style = ttk.Style()
            style.configure('proceed.TButton', font=button_font)

        

    def handle_proceed(self):
        print(self.count)
        if self.count == 1:
            ip1 = self.ip_entries[0].get()
            self.master.show_frame("welcome")
        elif self.count == 0:
            messagebox.showerror("IP Failed", "Check the ip address")



    def handle_test(self, index):
        ip_address = self.ip_entries[index].get()  
        print("Testing IP:", ip_address)
        camera_url = ip_address
        try:
            cap = cv2.VideoCapture(camera_url)
            print(self.count)

            while True:
                ret, frame = cap.read()

                if ret:
                    self.count = 1
                    break
                else:
                    self.count = 0
                    break
        except Exception as e:
            self.count = 0

        
        if self.count == 1:
            self.success_labels[index].config(text="Success", foreground="green")
        elif self.count == 0:
            self.success_labels[index].config(text="Failed", foreground="red")
        else:
            print("Database couldn't be read")

class WelcomePage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master

        ht = self.winfo_screenheight()
        const2 = int(ht / 86.4)
        const3 = int(ht / 172.8)
        self.const4 = int(ht / 21.6)
        self.playing = True

        self.frame = tk.Frame(self)
        self.frame.grid(row=1, column=0, padx=const2, pady=const2)

        self.label = tk.Label(self.frame)
        self.label.grid(row=0, column=0, padx=const3, pady=const3)

        self.video_file = "C:/Users/SIVA/OneDrive/Pictures/Icecream Screen Recorder/ps - 2.mp4"
        self.start_camera_feed()

    def stop_camera_feed(self):
        if self.playing:
            self.playing = False

    def start_camera_feed_button(self):
        if not self.playing:
            self.playing = True
            self.start_camera_feed()

    def restart_camera_feed(self):
        python = sys.executable
        os.execl(python, python, *sys.argv)

    def start_camera_feed(self):
        self.capture_object = Detection(self.video_file)
        t = threading.Thread(target=self.update_image)
        t.daemon = True
        t.start()

    def update_image(self):
        while self.playing:
            frame = self.capture_object.get_frame()
            if frame is not None:
                resized_frame = cv2.resize(frame, (1400,650))
                img = ImageTk.PhotoImage(image=Image.fromarray(resized_frame))
                self.label.config(image=img)
                self.label.image = img
                time.sleep(0.05)

    def show_menu(self, show=True):
        if show:
            self.menubar = tk.Menu(self.master)
            self.master.config(menu=self.menubar)
            self.file_menu = tk.Menu(self.menubar, tearoff=0)
            self.file_menu.add_command(label="Start", command=self.start_camera_feed_button)
            self.file_menu.add_command(label="Stop", command=self.stop_camera_feed)
            self.file_menu.add_command(label="Restart", command=self.restart_camera_feed)
            self.file_menu.add_separator()
            self.file_menu.add_command(label="Show Records", command=self.show_records)
            self.file_menu.add_separator()
            self.file_menu.add_command(label="Configuration", command=self.configuration)
            self.menubar.add_cascade(label="Tools", menu=self.file_menu)
        else:
            self.master.config(menu=None)

    def configuration(self):
        return "config"

    def show_records(self):
        return "record"


if __name__ == "__main__":
    app = Application()
    app.mainloop()
