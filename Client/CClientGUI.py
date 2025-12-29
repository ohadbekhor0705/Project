import itertools
from customtkinter.windows.widgets.ctk_frame import CTkFrame
import tkinter as tk
import customtkinter as Ctk
from tkinter import ttk
from tkinter import filedialog as fd
from CClientBL import CClientBL
import threading
import json
import os
import datetime
from time import sleep
class CClientGUI(CClientBL):
    
    def __init__(self) -> None: 
        super().__init__()
        # Load a custom color theme file for customtkinter. This points to the bundled theme JSON.
        # If the path is wrong the library will fall back to defaults, so keep the file with the project.
        Ctk.set_default_color_theme("./themes/rime.json")
        Ctk.set_appearance_mode("Dark")
        self.master = Ctk.CTk()
        self.FONT: tuple[str, int] = ("Roboto",17.8)
        self.BOLD: tuple[str, int] = ("Aria;",19, "bold")
        # Login Frame widgets
        self._usernameLabel: Ctk.CTkLabel | None = None
        self._usernameEntry: Ctk.CTkEntry| None= None
        self._passwordLabel: Ctk.CTkLabel| None= None
        self._passwordEntry: Ctk.CTkEntry| None= None
        self._loginButton = None
        # Storage Frame widgets
        self._savefile_button: Ctk.CTkLabel | None = None
        self._deletefile_button: Ctk.CTkButton | None = None
        self._uploadfile_button: Ctk.CTkButton | None = None
        self.dis_button: Ctk.CTkButton | None = None
        self.files_table = None
        self._searchbar = None
        self._search_button = None  
        self.progress_bar = None
        self.response_title = None  
        self.tabview = Ctk.CTkTabview(self.master)
        self.login_tab: CTkFrame   = self.tabview.add("Login")
        self.height, self.width = 750, 1500
        self.SAVE = "SAVE"
        self.GET = "GET"
        self.operation_thread: threading.Thread | None = None
        self.work_event: threading.Event = threading.Event()
        self.create_ui()
    
    def create_ui(self) -> None:
        """Assembling UI elements
        """        
        self.master.geometry(f"{self.width}x{self.height}")
        # Create Tabs
        self.master.resizable(False, False)
        self.tabview.pack(fill="both", expand=True)
        self.create_LoginFrame()

    def create_StorageFrame(self):
        # Greeting Label
        self.response_title = Ctk.CTkLabel(self.storage_tab, text=f"Hi, {self.username}", anchor="center", font=self.FONT)
        self.response_title.place(relx=0.5, rely=0.04, anchor="center")

        # Progress Bar
        # self.progress_bar = Ctk.CTkProgressBar(
        #     self.storage_tab,
        #     corner_radius=10,
        #     border_width=2,
        #     orientation="horizontal",
        #     mode="determinate",
        #     determinate_speed=5,
        #     indeterminate_speed=0.5
        # )
        # self.progress_bar.place(relx=0.1, rely=0.15, relheight=0.03, relwidth=0.87)
        # self.progress_bar.set(0)   
        # Button Frame for better organization
        self.button_frame = Ctk.CTkLabel(self.storage_tab, text="", fg_color=None)
        self.button_frame.place(relx=0.1, rely=0.22, relwidth=0.87)
        # Buttons
        self._uploadfile_button = Ctk.CTkButton(self.button_frame, text="Upload 📤", font=self.FONT, anchor="center", command=self.on_click_Upload)
        self._savefile_button = Ctk.CTkButton(self.button_frame, text="Save 💾", font=self.FONT, anchor="center", command=self.save_file)
        self._deletefile_button = Ctk.CTkButton(self.button_frame, text="Delete 🗑️", font=self.FONT, anchor="center", command=self.on_click_delete)  
        self._create_link_button = Ctk.CTkButton(
            self.button_frame,
            text="Create Link 🔗",
            font=self.FONT,
            anchor="center",
            compound="left"
        )
        # Pack buttons with spacing
        buttons = [self._uploadfile_button, self._savefile_button, self._deletefile_button, self._create_link_button]
        for i, btn in enumerate(buttons):
            btn.grid(row=0, column=i, padx=(0 if i == 0 else 10, 0), sticky="w") 
        # Treeview styling
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#2a2d2e",
                        foreground="white",
                        rowheight=30,
                        fieldbackground="#6E8BA400",
                        bordercolor="#6E8BA4",
                        borderwidth=0,
                        font=("Roboto", 12))
        style.map('Treeview', background=[('selected', "#454950")])
        style.configure("Treeview.Heading", background="#2a2d2e", foreground="white", relief="flat", font=self.FONT)
        style.map("Treeview.Heading", background=[('active', "#2a2d2e")])  
        columns = ("#", "file name", "size", "Date modified")
        self.files_table = ttk.Treeview(self.storage_tab, columns=columns, show="headings")
        for col in columns:
            self.files_table.heading(col, text=col, anchor="w")
            self.files_table.column(col, anchor="w", stretch=False)
        self.files_table.column("#", width=int(0.1*0.87*self.width))
        self.files_table.column("Date modified", width=int(0.2*0.87*self.width))
        self.files_table.column("file name", width=int(0.6*0.87*self.width))
        self.files_table.column("size", width=int(0.1*0.87*self.width))
        self.files_table.place(relx=0.1, rely=0.34, relheight=0.6, relwidth=0.87)

    def create_LoginFrame(self):
        # Make login_tab fully stretch
        self.login_tab.grid_rowconfigure(0, weight=1)
        self.login_tab.grid_columnconfigure(0, weight=1)
        # Full-screen container
        self.login_container = Ctk.CTkFrame(self.login_tab, corner_radius=0)
        self.login_container.grid(row=0, column=0, sticky="nsew")
        # Add a background color or gradient
        self.login_container.configure(fg_color="#1E1E1E")  # dark gray background
        # Top section for welcome message or logo
        self.top_section = Ctk.CTkFrame(self.login_container, fg_color="transparent")
        self.top_section.pack(fill="both", expand=True)
        self.welcome_label = Ctk.CTkLabel(
            self.top_section, text="Welcome to SkyVault!", font=("Arial", 36), anchor="center"
        )
        self.welcome_label.pack(expand=True)
        # Center section for username/password
        self.center_section = Ctk.CTkFrame(self.login_container, fg_color="#2E2E2E", corner_radius=10)
        self.center_section.pack(pady=20, padx=40, fill="both", expand=True)
        # Message box
        self._messageBox = Ctk.CTkLabel(self.center_section, text="", font=self.FONT, anchor="center")
        self._messageBox.pack(pady=(10, 20))
        # Username
        username_frame = Ctk.CTkFrame(self.center_section, fg_color="transparent")
        username_frame.pack(fill="x", padx=20, pady=(0, 10))
        self._usernameLabel = Ctk.CTkLabel(username_frame, text="Username:", font=self.FONT, width=100, anchor="w")
        self._usernameLabel.pack(side="left")
        self._usernameEntry = Ctk.CTkEntry(username_frame, placeholder_text="Username", font=self.FONT)
        self._usernameEntry.pack(side="right", fill="x", expand=True)
        # Password
        password_frame = Ctk.CTkFrame(self.center_section, fg_color="transparent")
        password_frame.pack(fill="x", padx=20, pady=(0, 10))
        self._passwordLabel = Ctk.CTkLabel(password_frame, text="Password:", font=self.FONT, width=100, anchor="w")
        self._passwordLabel.pack(side="left")
        self._passwordEntry = Ctk.CTkEntry(password_frame, placeholder_text="Password", font=self.FONT, show="*")
        self._passwordEntry.pack(side="right", fill="x", expand=True)
        # Remember me
        self._checkBox = Ctk.CTkCheckBox(self.center_section, text="Remember me?", offvalue="False", onvalue="True", font=self.FONT)
        self._checkBox.pack(pady=(0, 20))
        # Buttons
        button_frame = Ctk.CTkFrame(self.center_section, fg_color="transparent")
        button_frame.pack(pady=(0, 20))
        self._loginButton = Ctk.CTkButton(button_frame, text="Login", font=self.FONT, command=lambda: threading.Thread(target=self.on_click_button_connect, args=("login",)).start())
        self._loginButton.pack(side="left", padx=10, expand=True, fill="x")
        self._registerButton = Ctk.CTkButton(button_frame, text="Register", font=self.FONT, command=lambda: threading.Thread(target=self.on_click_button_connect, args=("register",)).start())
        self._registerButton.pack(side="right", padx=10, expand=True, fill="x")
        # Bottom section (can add extra info, copyright, etc.)
        self.bottom_section = Ctk.CTkFrame(self.login_container, fg_color="transparent")
        self.bottom_section.pack(fill="both", expand=True)
        self.info_label = Ctk.CTkLabel(self.bottom_section, text="All rights reserved.", font=("Arial", 12))
        self.info_label.pack(side="bottom", pady=10)
        # Pre-fill username/password if "Remember me"
        self.remember_action(self.GET)
    
    def create_UserDataTab(self) -> None:
        """
        Populates self.usertab with user information and storage usage.
        Assumes self.usertab is an existing CTkFrame (tab).
        """

        # Title
        title_label = Ctk.CTkLabel(
            self.usertab,
            text="User Information",
            font=self.TITLE_FONT if hasattr(self, "TITLE_FONT") else self.FONT
        )
        title_label.pack(pady=(20, 10))

        # Username
        username_label = Ctk.CTkLabel(
            self.usertab,
            text=f"Username: {self.username}",
            font=self.FONT,
            anchor="w"
        )
        username_label.pack(fill="x", padx=30, pady=5)

        # Storage text
        storage_label = Ctk.CTkLabel(
            self.usertab,
            text=f"Storage: {self.current_storage} MB / {self.max_storage} MB",
            font=self.FONT,
            anchor="w"
        )
        storage_label.pack(fill="x", padx=30, pady=5)

        # Progress calculation
        progress = (
            min(self.current_storage / self.max_storage, 1.0)
            if self.max_storage > 0 else 0
        )

        # Progress bar
        storage_bar = Ctk.CTkProgressBar(
            self.usertab,
            height=18,
            corner_radius=10
        )
        storage_bar.set(progress)
        storage_bar.pack(fill="x", padx=30, pady=(10, 5))

        # Percentage label
        percent_label = Ctk.CTkLabel(
            self.usertab,
            text=f"{progress * 100:.1f}% used",
            font=self.FONT
        )
        percent_label.pack(pady=(0, 30))

        # Logout button
        logout_button = Ctk.CTkButton(
            self.usertab,
            text="Logout 🚪",
            font=self.FONT,
            fg_color="#C0392B",        
            hover_color="#A93226",     
            text_color="white",
            corner_radius=12,
            command=self.logout
        )
        logout_button.pack(pady=(10, 25))

    def run(self) -> None: self.master.mainloop()
    
    def on_click_button_connect(self, cmd: str) -> None:
        username: str = self._usernameEntry.get().lstrip()
        password: str = self._passwordEntry.get().lstrip()
        
        if not username or not password:
            self._messageBox.configure(text="You must fill all the fields!")
            return
        self.remember_action(self.SAVE,username=username,password=password)
        self._messageBox.configure(text="Connecting....")
        self._loginButton.configure(state=Ctk.DISABLED)
        self._registerButton.configure(state=Ctk.DISABLED)
        # We call it from the background thread started by the button command above.
        response , self.client = self.connect(username,password,cmd)
        if self.client:
            # Create Storage Frame:
            self.storage_tab: CTkFrame   = self.tabview.add("Storage")
            self.create_StorageFrame()
            self.tabview.set("Storage")
            self.usertab: CTkFrame = self.tabview.add("UserData")
            self.create_UserDataTab()
            
            self.response_title.configure(text = response["message"])
            for file in response["files"]:
                datetime_obj: datetime = datetime.datetime.fromtimestamp(file["modified"])
                # Extract only the date part
                date_obj = datetime_obj.date()

                # Output can also be formatted as a string (e.g., YYYY-MM-DD)
                formatted_date = date_obj.strftime("%Y-%m-%d")
                self.files_table.insert("","end",values= (file["file_id"],file["filename"],str(round(file["filesize"]/1048576,2))+" MB",formatted_date))
            threading.Thread(target=self.check_connection, daemon=True).start()

        else:
            self._loginButton.configure(state=Ctk.NORMAL)
            self._registerButton.configure(state=Ctk.NORMAL)
        self._messageBox.configure(text=response["message"])

    def on_click_Upload(self) -> None:
        # if other tasks are running then prevent from user from sending other network requests
        if self.operation_thread  and self.operation_thread.is_alive():
            print("Another task is running!")
            return 
        filename: str = fd.askopenfilename(
        title="Open a file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:

            f = open(filename,"rb")
            tbl = self.files_table
            res_text = self.response_title
            self.operation_thread = threading.Thread(target=lambda: self.sendfile(f,"upload" , table = tbl, response_text=res_text))
            self.operation_thread.start()
            threading.Thread(target=self.animate, args=("Uploading file",)).start()
        else:
            self.response_title.configure(text="File not found! Please select a file again.") 

    def remember_action(self, action: str, **user_data)  -> None:
        try: 
            if action == self.SAVE:
                remember: bool = self._checkBox.get() == "True"
                if remember:
                    # Store credentials locally in a simple JSON file so they can be
                    with open ("./user.json","w") as json_file:
                        json.dump(
                            {
                                "remember": remember,
                                "username": user_data["username"],
                                "password": user_data["password"]
                            },
                            json_file,
                            indent=4
                        )
                if not remember:
                    if os.path.exists("./user.json"): 
                        os.remove("./user.json")
            elif action == self.GET and os.path.exists("./user.json"):
                with open("./user.json", "r") as json_file:
                    values: dict = json.load(json_file)
                    if values["remember"]:
                        # Insert saved credentials into the entry widgets and check the box.
                        # Using insert(0, ...) places the text at the start of the field.
                        self._usernameEntry.insert(0,values["username"])
                        self._passwordEntry.insert(0, values["password"])
                        self._checkBox.select()
                        threading.Thread(target=self.on_click_button_connect,args=("login",)).start()

        except Exception as e:
            print(e)
    
    def save_file(self):
        if self.operation_thread and self.operation_thread.is_alive():
            return 
        if not self.files_table.selection:
            return
        selected_row = self.files_table.selection()[0]
        values: list[str] = self.files_table.item(selected_row)["values"]
        file_id, filename, file_size, _ = values

        self.operation_thread = threading.Thread(target=self.ReceiveFile, args=(file_id, filename))
        self.operation_thread.start()
        threading.Thread(target=self.animate, args=("fetching file",)).start()

    def on_click_delete(self) -> None:
        if self.operation_thread and self.operation_thread.is_alive():
            return 
        if not self.files_table.selection():
            return
        # Trying to get selected rows and stop if no rows were selected:
        selected_rows: tuple[str, ...]= self.files_table.selection()
        
        selected_files = [ self.files_table.item(row)["values"][0] for row in selected_rows]
        self.operation_thread = threading.Thread(target=lambda: self.delete_files(selected_files, self.files_table, selected_rows, response_text=self.response_title))
        self.operation_thread.start()
    
    def logout(self) -> None:
        self.connection_event.clear() # clearing the event flag
        if self.client:
            self.send_message("!DIS")
            self.client.close()
        self.client = None
        self.files_table.delete(*self.files_table.get_children()) # get all rows and extract them in the function
        self.tabview.delete("Storage")
        self.tabview.delete("UserData")
        self.tabview.set("Login")
        self._messageBox.configure(text="")
        self._loginButton.configure(state=Ctk.ACTIVE)
        self._registerButton.configure(state=Ctk.ACTIVE)
        self.username = ""
        self.max_storage = 0
        self.current_storage = 0
    
    def check_connection(self) ->None:
        while self.connection_event.is_set():
            try:
                self.client.send(b'')
            except OSError:
                self.client = None
                self.logout()
                break
            sleep(2)
                
    def animate(self, name: str):
        self.response_title.configure(font=self.BOLD)
        for c in itertools.cycle(['.','..', '...', '....', '.....', ]):
            if self.work_event.is_set():
                self.response_title.configure(text=c)
                sleep(0.5)
            else: break
if __name__ == "__main__":
    try:
        print("Press Ctrl + C to exit.")
        App = CClientGUI()
        App.run()
        exit()
    except KeyboardInterrupt: # Ctrl + C
        exit()