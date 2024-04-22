import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import cv2
import requests
import wmi as wmi
import pythoncom
import os
from datetime import datetime
from PIL import ImageTk, Image
from tkcalendar import DateEntry
from ultralytics import YOLO
import time
import warnings
import subprocess
import shutil
import webbrowser
import sys
from pycomm3 import LogixDriver
# Creating database ----------------------------------------------------------------------------------------------------

def create_database_and_tables():
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='users' ''')
    users_table_exists = cursor.fetchone()
    cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='cameras' ''')
    cameras_table_exists = cursor.fetchone()
    check = 0
    if not users_table_exists:
        cursor.execute('''CREATE TABLE users (
                            id INTEGER PRIMARY KEY,
                            username TEXT UNIQUE,
                            password TEXT,
                            uuid TEXT DEFAULT 0,
                            initial_state INTEGER DEFAULT 0
                        )''')
    if not cameras_table_exists:
        cursor.execute('''CREATE TABLE cameras (
                            id INTEGER PRIMARY KEY,
                            ip1 TEXT,
                            plcip TEXT,
                            plcport INTEGER,
                            jam_check_time INTEGER
                        )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS records
                      (id INTEGER PRIMARY KEY,
                       camera TEXT,
                       screenshot_location TEXT,
                       timestamp TEXT,
                       PLC_ID INTEGER(20))''')
    cursor.execute('''SELECT name FROM sqlite_master WHERE type='table' AND name='model' ''')

    model_table_exists = cursor.fetchone()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS model (
                        model_1 TEXT
                    )''')
    if not model_table_exists:
        model_data = ('models\\1.pt',)
        cursor.execute('''INSERT INTO model (model_1) VALUES (?)''', model_data,)
    conn.commit()
    conn.close()


def create_table():
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO records (camera, screenshot_location, timestamp, PLC_ID)
                      VALUES ('Camera 1', 'location1.jpg', '2024-03-08 10:00:00', 3)''')
    cursor.execute('''INSERT INTO records (camera, screenshot_location, timestamp, PLC_ID)
                      VALUES ('Camera 2', 'location2.jpg', '2024-03-08 10:05:00', 2)''')
    cursor.execute('''INSERT INTO records (camera, screenshot_location, timestamp, PLC_ID)
                      VALUES ('Camera 3', 'location3.jpg', '2024-03-08 10:10:00', 1)''')
    cursor.execute('''INSERT INTO records (camera, screenshot_location, timestamp, PLC_ID)
                      VALUES ('Camera 4', 'https://sqliteviewer.app/#/config.db/table/users/', '2024-03-08 10:15:00', 4)''')

    conn.commit()
    conn.close()


def get_db_connection():
    conn = sqlite3.connect('config.db')
    conn.row_factory = sqlite3.Row
    return conn


def login_post(user, password_1):
    username = user
    password = password_1

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_row = cursor.fetchone()

        if user:
            user_password = user_row['password']
            if user_password == password:
                print("Password correct")
                return True
            else:
                return False
        else:
            print("User not found in the database")
            return False
    except Exception as e:
        print("Error:", e)
        return False
    finally:
        conn.close()


def get_system_id():
    try:
        pythoncom.CoInitialize()
        c = wmi.WMI()
        for system in c.Win32_ComputerSystemProduct():
            system_info = system.UUID
            print(system_info)

    except Exception as e:
        print(f"Error: {e}")
        system_info = "0"

    finally:
        pythoncom.CoUninitialize()

    return system_info


def add_uuid_to_users(uuid, username):
    print("added uuid")
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    cursor.execute('''UPDATE users SET uuid = ?, initial_state = 0 WHERE username = ?''', (uuid, username))
    conn.commit()
    conn.close()

    print(f"UUID '{uuid}' added to users table for username '{username}' with initial state 0.")


def check_uuid_and_initial_state(uuid, username):
    print("Checking uuid.........")
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    print(uuid)
    cursor.execute('''SELECT uuid, initial_state FROM users WHERE uuid = ?''', (uuid,))
    user_data = cursor.fetchone()
    conn.close()

    if user_data is None:
        add_uuid_to_users(uuid, username)
        return "Load"
    else:
        _, initial_state = user_data
        if initial_state == 1:
            return "Live"
        else:
            return "Load"  


def update_initial_state(uuid, new_state):
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    cursor.execute('''UPDATE users SET initial_state = ? WHERE uuid = ?''', (new_state, uuid))
    conn.commit()
    conn.close()

    print(f"Initial state for user '{uuid}' updated successfully.")


def store_camera_ips(ip1, plcip, plcport):
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO cameras (ip1, plcip, plcport)
                      VALUES (?, ?, ?)''', (ip1, plcip, plcport))
    conn.commit()
    conn.close()


def retrieve_ip(camera):
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    if camera == 0:
        cursor.execute("""
                SELECT ip1  
                FROM cameras
                LIMIT 1
            """)
    

    ip = cursor.fetchone()
    print(ip)  
    conn.close()
    return ip[0] if ip else None


def insert_record(camera, no_of_tyres_jammed, screenshot_location=""):
    if camera == "" or no_of_tyres_jammed == "":
        return
    conn = sqlite3.connect('config.db')
    cursor = conn.cursor()
    timestamp = datetime.now()
    sql_command = '''INSERT INTO records (camera, screenshot_location, timestamp, No_of_Tyres_Jammed)
                        VALUES (?, ?, ?, ?)'''
    cursor.execute(sql_command, (camera, screenshot_location, timestamp, no_of_tyres_jammed))
    conn.commit()
    conn.close()


def retrieve_jam_check_time():
    try:
        conn = sqlite3.connect('config.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM cameras LIMIT 1")
        row = cursor.fetchone()
        if row:
            index_of_jam_check_time = cursor.description.index(('jam_check_time', None, None, None, None, None, None))
            jam_check_time = row[index_of_jam_check_time]
            print(jam_check_time, "adaf")
            if (jam_check_time == None or jam_check_time == ''):
                jam_check_time = 40
            return int(jam_check_time)
        else:
            return 40
    except sqlite3.Error as e:
        print("SQLite error:", e)
    finally:
        if conn:
            conn.close()


# ----------------------------------------------------------------------------------------------------------------------
create_database_and_tables()
create_table()

def visit_ip(ip_address):
    print("sds")
    try:
        response = requests.get(f"http://{ip_address}")
        if response.status_code == 200:
            print(f"Successfully visited {ip_address}")
        else:
            print(f"Failed to visit {ip_address}. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Failed to visit {ip_address}. Error: {e}")

def main1():
    ip_addresses = ["192.168.234.74/3", "192.168.234.74/0"]  # Replace x.x.x.x and y.y.y.y with your actual IP addresses
    for ip in ip_addresses:
        visit_ip(ip)

def main2():
    ip_addresses = ["192.168.234.74/1", "192.168.234.74/0"]  # Replace x.x.x.x and y.y.y.y with your actual IP addresses
    for ip in ip_addresses:
        visit_ip(ip)

def main3():
    ip_addresses = ["192.168.234.74/5", "192.168.234.74/0"]  # Replace x.x.x.x and y.y.y.y with your actual IP addresses
    for ip in ip_addresses:
        visit_ip(ip)
count = 0

class Detection:
    def __init__(self, video_path):
        self.video_path = "videos\\video4.ts"
        ip = retrieve_ip(0)
        print("The ip address is",ip)
        conn = sqlite3.connect('config.db')
        cursor = conn.cursor()
        cursor.execute('''SELECT model_1 FROM model LIMIT 1''')
        first_row = cursor.fetchone()
        conn.close()
        if first_row:
            model_name = first_row[0]
            print(model_name)
        else:
            print("No data found in the 'model' table.")


        self.cap = cv2.VideoCapture(1)

    def get_frame(self):
        global count
        ret, frame = self.cap.read()
        if ret:
            model = YOLO('main_sorter.pt')
            results = model(frame)
            annotated_frame = results[0].plot()
            lis = results[0].verbose().split(',')
            print(lis)

            if len(lis) == 8:
                cv2.rectangle(annotated_frame, (30, 20), (200, 70), (0, 0, 0), -1)
                cv2.putText(annotated_frame, "ALL OK", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                if ' 1 regulator' not in lis:
                    cv2.rectangle(annotated_frame, (30, 20), (400, 70), (0, 0, 0), -1)
                    cv2.putText(annotated_frame, "Regulator Missing", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    if count==0:
                        count+=1
                        main1()
                    

                elif ' 1 capacitor' not in lis:
                    cv2.rectangle(annotated_frame, (30, 20), (400, 70), (0, 0, 0), -1)
                    cv2.putText(annotated_frame, "Capacitor Missing", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    if count==0:
                        count+=1
                        main2()
                elif ' 1 transistor' not in lis:
                    cv2.rectangle(annotated_frame, (30, 20), (400, 70), (0, 0, 0), -1)
                    cv2.putText(annotated_frame, "Transistor Missing", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    if count==0:
                        count+=1
                        main3()
        return cv2.cvtColor(annotated_frame, cv2.COLOR_BGR2RGB)

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
        self.welcome_frame = WelcomePage(self)
        self.show_frame("login")

    def show_frame(self, frame_name):
        if frame_name == "login":
            self.login_frame.pack(fill='both', expand=True)
            self.ip_address_frame.pack_forget()
            self.welcome_frame.pack_forget()
        elif frame_name == "ip_address":
            self.login_frame.pack_forget()
            self.ip_address_frame.pack(fill='both', expand=True)
            self.welcome_frame.pack_forget()

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
        label.pack(pady=(const2, const3))  

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
        username = self.username_entry.get()  # Retrieve username
        password = self.password_entry.get()  # Retrieve password
        print("Username:", username)
        print("Password:", password)
        login_status = login_post(username, password)
        if login_status:
            messagebox.showinfo("Login Successful", "Welcome, " + username + "!")
            current_uuid = get_system_id()
            print(current_uuid)
            val = check_uuid_and_initial_state(current_uuid, username)
            if val == "Load":
                self.master.show_frame("ip_address")
            elif val == "Live":
                self.master.show_frame("welcome")
            else:
                print("Problem in database or getting ip ")

        else:
            print("invalid username and password")
            messagebox.showerror("Login Failed", "Invalid username or password.")

class IPAddressPage(ttk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.count = 2  # 2- indicates null 
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
            plcip = "172.16.200"
            plcport = 5000
            store_camera_ips(ip1,plcip, plcport)
            sys_uuid = get_system_id()
            update_initial_state(sys_uuid, 1)
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

        self.video_file = retrieve_ip(0)
        self.start_camera_feed()

    def stop_camera_feed(self):
        if self.playing:
            self.playing = False

    def start_camera_feed_button(self):
        if not self.playing:
            self.playing = True
            self.start_camera_feed()

    def restart_camera_feed(self):
        global count
        count = 0
        

    def start_camera_feed(self):
        self.capture_object = Detection(self.video_file)
        t = threading.Thread(target=self.update_image)
        t.daemon = True
        t.start()

    def update_image(self):
        while self.playing:
            frame = self.capture_object.get_frame()
            if frame is not None:
                resized_frame = cv2.resize(frame, (1000,700))
                img = ImageTk.PhotoImage(image=Image.fromarray(resized_frame))
                self.label.config(image=img)
                self.label.image = img
                # time.sleep(0.01)

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
            self.file_menu.add_separator()
            self.file_menu.add_command(label="Plc Trigger", command=self.plc_trigger)
            self.file_menu.add_separator()
            self.menubar.add_cascade(label="Tools", menu=self.file_menu)
        else:
            self.master.config(menu=None)


    def visit_ip(self,ip_address):
        try:
            response = requests.get(f"http://{ip_address}")
            if response.status_code == 200:
                print(f"Successfully visited {ip_address}")
            else:
                print(f"Failed to visit {ip_address}. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Failed to visit {ip_address}. Error: {e}")

    def plc_trigger(self):
        self.ip_addresses = ["192.168.234.74/6", "192.168.234.74/0"]  # Replace x.x.x.x and y.y.y.y with your actual IP addresses
        for ip in self.ip_addresses:
            self.visit_ip(ip)

    def configuration(self):
        script_path = os.path.abspath('configuration.py')
        if os.path.exists(script_path):
            try:
                subprocess.Popen(['Python', script_path]) # Temporarily not working,having issue in system.
            except Exception as e:
                print("An error occurred:", e)
        else:
            print("Script 'configuration.py' not found in the current directory.")

    def show_records(self):
        records_page = self.create_records_page(self.master)
        records_page.grid(row=1, column=0, padx=self.const4, pady=self.const4)


    def create_records_page(self, master):
        self.master.withdraw()
        self.newwindow = tk.Toplevel(master)

        ht1 = self.winfo_screenheight()
        const1 = int(ht1 / 54)  # 16
        const2 = int(ht1 / 43.2)  # 20
        const3 = int(ht1 / 86.4)  # 10
        const4 = int(ht1 / 72)  # 12
        const5 = int(ht1 / 432)  # 2
        const6 = int(ht1 / 172.8)  # 5

        self.newwindow.overrideredirect(True)
        screen_width = self.newwindow.winfo_screenwidth()
        screen_height = self.newwindow.winfo_screenheight()
        self.newwindow.geometry(f"{screen_width}x{screen_height}")

        records_frame = ttk.Frame(self.newwindow)
        records_frame.pack(expand=True, fill='both')
        
        label = ttk.Label(records_frame, text="Records", font=('Helvetica', const1))
        label.grid(row=0, column=0, pady=const2, columnspan=3)

        filter_criteria = ttk.Combobox(records_frame, values=["Date", "Month", "Camera"])
        filter_criteria.grid(row=1, column=2, pady=const3, padx=const3)
        filter_criteria.set("Date") 
        filter_criteria.bind("<<ComboboxSelected>>", lambda event: self.toggle_filter_options(filter_criteria, date_entry, camera_combobox))

        date_entry = DateEntry(records_frame, width=const4, background='blue', foreground='white', borderwidth=const5)
        date_entry.grid(row=2, column=2, pady=const3, padx=const3)
        date_entry.grid_remove()  

        camera_combobox = ttk.Combobox(records_frame, values=["Camera 1", "Camera 2", "Camera 3", "Camera 4"])
        camera_combobox.grid(row=2, column=2, pady=const3, padx=const3)
        camera_combobox.grid_remove() 

        filter_button = ttk.Button(records_frame, text="Filter", style="filter.TButton",
                                command=lambda: self.filter_records(tree, filter_criteria, camera_combobox, date_entry))
        filter_button.grid(row=1, column=1, pady=const3)

        back_button = ttk.Button(records_frame, text="Back", style="back.TButton", command=self.back)
        back_button.grid(row=1, column=0, pady=const5)

        tree = ttk.Treeview(records_frame, columns=("Camera", "Screenshot Location", "Timestamp", "PLC_ID"))
        tree.grid(row=4, column=0, columnspan=3, sticky="nsew")
        records_frame.grid_rowconfigure(4, weight=1) 
        records_frame.grid_columnconfigure((0, 1, 2), weight=1) 

        tree.heading("#0", text="ID")
        tree.heading("Camera", text="Camera")
        tree.heading("Screenshot Location", text="PCB_ID")
        tree.heading("Timestamp", text="Timestamp")
        tree.heading("PLC_ID", text="No of Defected Components")

        vsb = ttk.Scrollbar(records_frame, orient="vertical", command=tree.yview)
        vsb.grid(row=4, column=3, sticky="ns")
        tree.configure(yscrollcommand=vsb.set)

        tree.bind("<ButtonRelease-1>", lambda event: self.open_link(event, tree))

        self.fetch_and_display_all_records(tree)

    def fetch_and_display_all_records(self, tree):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM records")
        records = cursor.fetchall()
        conn.close()

        for item in tree.get_children():
            tree.delete(item)

        for record in records:
            tree.insert("", "end", text=record[0], values=(record[1], record[2], record[3], record[4]))

    def open_link(self, event, tree):

        item = tree.selection()[0]
        screenshot_location = tree.item(item, "values")[1]
        webbrowser.open_new_tab(screenshot_location)

    def toggle_filter_options(self, filter_criteria, date_entry, camera_combobox):
        criteria = filter_criteria.get()
        if criteria == "Date" or criteria == "Month":
            # date_entry.flex()
            date_entry.grid()
            camera_combobox.grid_remove()
        elif criteria == "Camera":
            camera_combobox.grid()
            date_entry.grid_remove()

    def filter_records(self, tree, filter_criteria, camera_combobox, date_entry):
        criteria = filter_criteria.get()

        conn = get_db_connection()
        cursor = conn.cursor()

        if criteria == "Date":
            selected_date = date_entry.get_date().strftime("%Y-%m-%d")
            cursor.execute("SELECT * FROM records WHERE DATE(timestamp) = ?", (selected_date,))
        elif criteria == "Month":
            selected_month = date_entry.get_date().strftime("%Y-%m")
            cursor.execute("SELECT * FROM records WHERE strftime('%Y-%m', timestamp) = ?", (selected_month,))
        elif criteria == "Camera":
            selected_camera = int(camera_combobox.get().split()[1])
            cursor.execute("SELECT * FROM records WHERE camera = ?", (f"Camera {selected_camera}",))

        records = cursor.fetchall()
        for item in tree.get_children():
            tree.delete(item)
        for record in records:
            tree.insert("", "end", text=record[0], values=(record[1], record[2], record[3], record[4]))

        conn.close()

    def back(self):
        self.newwindow.destroy()
        self.master.deiconify()


if __name__ == "__main__":
    app = Application()
    app.mainloop()