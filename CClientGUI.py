import customtkinter as Ctk
from tkinter import ttk
from tkinter import filedialog as fd
from CClientBL import CClientBL
import threading
import json
import os
from time import sleep
import bcrypt
from protocol import write_to_log
class CClientGUI(CClientBL):
    
    def __init__(self) -> None:
        super().__init__()
        # Load a custom color theme file for customtkinter. This points to the bundled theme JSON.
        # If the path is wrong the library will fall back to defaults, so keep the file with the project.
        Ctk.set_default_color_theme("./themes/rime.json")
        Ctk.set_appearance_mode("Light")
        self.master = Ctk.CTk()
        self.FONT: tuple[str, int] = ("Helvetica",24)
        # Login Frame widgets
        self._usernameLabel = None
        self._usernameEntry = None
        self._passwordLabel = None
        self._passwordEntry = None
        self._loginButton = None
        # Storage Frame widgets
        self._savefile_button = None
        self._deletefile_button = None
        self._uploadfile_button = None
        self._filestbl = None
        self._searchbar = None
        self._search_button = None  

        self._title = None  

        self.StorageFrame: Ctk.CTkFrame = None
        self.LoginFrame: Ctk.CTkFrame = None 
        
        self.height, self.width = 750, 1300
        self.SAVE = "SAVE"
        self.GET = "GET"
        
        self.create_ui()
    

    def create_ui(self) -> None:
        
        self.master.geometry(f"{self.width}x{self.height}")
        # Create Tabs
        self.master.resizable(False, False)

        self.LoginFrame = self.create_LoginFrame()
        self.LoginFrame.pack(fil="both", expand=True, padx=10, pady=10)
        self.StorageFrame: Ctk.CTkFrame = self.create_StorageFrame()

    def create_StorageFrame(self) -> Ctk.CTkFrame:
        # creating STORAGE UI widgets:

        StorageFrame: Ctk.CTkFrame = Ctk.CTkFrame(self.master)

        self._title = Ctk.CTkLabel(StorageFrame, text="Hi, {username}", anchor="center",font=self.FONT)
        self._title.place(relx=0.5, rely=0.04, anchor="center") 

        self._searchbar = Ctk.CTkEntry(StorageFrame, placeholder_text= "Search for files...", font = self.FONT)
        self._searchbar.place(relx = 0.1, rely=0.1, relheight=0.06, relwidth=0.65)

        self._search_button = Ctk.CTkButton(StorageFrame, text="🔍", font=self.FONT, command=lambda: self.StorageFrame.forget())
        self._search_button.place(relx= 0.77, rely=0.1, relheight=0.06, relwidth=0.2)  

        self._uploadfile_button = Ctk.CTkButton(StorageFrame, text= "Upload 📤", font = self.FONT, anchor="center", command=self.on_click_Upload)
        self._uploadfile_button.place(relx= 0.1, rely=0.22, relheight=0.06, relwidth=0.15) 

        self._savefile_button = Ctk.CTkButton(StorageFrame, text="Save 💾", font=self.FONT, anchor="center", state="disabled")
        self._savefile_button.place(relx= 0.35, rely=0.22, relheight=0.06, relwidth=0.15)  

        self._deletefile_button = Ctk.CTkButton(StorageFrame, text="Delete 🗑️", font=self.FONT, anchor="center", state="disabled")
        self._deletefile_button.place(relx=0.6, rely=0.22, relheight=0.06, relwidth=0.15)

        style = ttk.Style() 
        style.theme_use("default")
        # https://github.com/TomSchimansky/CustomTkinter/discussions/431
        style.configure("Treeview",
                            background="#2a2d2e",
                            foreground="white",
                            rowheight=30,
                            fieldbackground="#6E8BA4",
                            bordercolor="#6E8BA4",
                            borderwidth=0, font=("Helvetica",16))
        style.map('Treeview', background=[('selected', '#22559b')])
    
        style.configure("Treeview.Heading",background="#009dff",foreground="white",relief="flat", font=self.FONT)
        style.map("Treeview.Heading",background=[('active', '#3484F0')])
        columns = ("file name", "file size (MB)", "Date modified")
        self._filestbl = ttk.Treeview(StorageFrame, columns=columns, show="headings")
        for col in columns:
            self._filestbl.heading(col, text=col,anchor="center")
            self._filestbl.column(col, width=int(0.65*self.width/len(columns)), anchor="center", stretch=False)
        self._filestbl.place(relx = 0.1, rely=0.34, relheight=0.6, relwidth=0.65)


        return StorageFrame
    
    def create_LoginFrame(self) ->Ctk.CTkFrame:
        
        # creating Login UI widgets:

        LoginFrame: Ctk.CTkFrame = Ctk.CTkFrame(self.master)

        self._messageBox = Ctk.CTkLabel(LoginFrame, text="",font=self.FONT)
        self._messageBox.place(relx = 0.07, rely = 0.05, relheight=0.06, relwidth=0.4)
        
        self._usernameLabel = Ctk.CTkLabel(LoginFrame, text="Username:", font=self.FONT, anchor="center")
        self._usernameLabel.place(relx = 0.1, rely = 0.15, relheight=0.06, relwidth=0.15)

        self._usernameEntry = Ctk.CTkEntry(LoginFrame, placeholder_text="Username", font=self.FONT)
        self._usernameEntry.place(relx=0.24, rely=0.15, relheight=0.06, relwidth=0.15)

        self._passwordLabel = Ctk.CTkLabel(LoginFrame,text= "Password:", font = self.FONT, anchor="center")
        self._passwordLabel.place(relx = 0.1, rely=0.27, relheight=0.06, relwidth=0.15)

        self._passwordEntry = Ctk.CTkEntry(LoginFrame, placeholder_text="Password", font= self.FONT, show="*")
        self._passwordEntry.place(relx = 0.24, rely = 0.27, relheight=0.06, relwidth=0.15)
        
        self._checkBox = Ctk.CTkCheckBox(LoginFrame, text="Remember me?",offvalue="False", onvalue="True" ,font=self.FONT)
        self._checkBox.place(relx=0.12, rely=0.37, relheight=0.06,relwidth= 0.3)
        # Attempt to pre-fill username/password from a local file if the user previously
        # selected "Remember me". This reads ./user.json and inserts values in the fields.
        # If the file doesn't exist nothing happens.
        self.remember_action(self.GET)

        # Run login in a background thread so the UI stays responsive during network calls.
        # Using lambda to create and start a Thread avoids blocking the mainloop.
        self._loginButton = Ctk.CTkButton(LoginFrame, text="Login", font=self.FONT, anchor="center",command=lambda: threading.Thread(target=self.on_click_login).start())
        self._loginButton.place(relx=0.1, rely=0.47, relheight=0.06,relwidth= 0.135)
        
        self._registerButton = Ctk.CTkButton(LoginFrame, text="Register", font=self.FONT, anchor="center", command=lambda: threading.Thread(target=self.on_click_register).start())
        self._registerButton.place(relx=0.24, rely=0.47, relheight=0.06,relwidth= 0.135)


        return LoginFrame

    def run(self) -> None: self.master.mainloop()

    def on_click_login(self) -> None:
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
        response , self.client_socket = self.connect(username,password,"login")
        if self.client_socket:
            # Create Storage Frame:
            self.LoginFrame.forget()
            self.StorageFrame.pack(expand=True, fill="both", padx=10, pady=10)
            self._title.configure(text = response)
           # threading.Thread(target=self.check_connection).start()
        else:
            self._loginButton.configure(state=Ctk.NORMAL)
            self._registerButton.configure(state=Ctk.NORMAL)
        self._messageBox.configure(text=response)
    def on_click_register(self):
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
        response , self.client_socket = self.connect(username,password,"register")
        if self.client_socket:
            write_to_log(self.client_socket)
            # Create Storage Frame and adding to tab view:
            self.LoginFrame.forget()
            self.StorageFrame: Ctk.CTkFrame = self.create_StorageFrame()
            self.StorageFrame.pack(expand=True, fill="both", padx=10, pady=10)
            #threading.Thread(target=self.check_connection, daemon=True).start()
        else:
            self._loginButton.configure(state=Ctk.NORMAL)
            self._registerButton.configure(state=Ctk.NORMAL)
        self._messageBox.configure(text=response)
        self._title.configure(text=response)
        
    def on_click_Upload(self):
        
        filename = fd.askopenfilename(
        title="Open a file",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )   
        with open(filename,"rb") as f:
            self._filestbl.insert("","end",
                    values=(
                    f.name.split("/")[-1] ,
                    int(os.path.getsize(filename)/ (1024 * 1024)),
                    "")
                                )   
    
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

        except Exception as e:
            write_to_log(e)

    def check_connection(self):
        while True:
            try:
                # Send a test message to server
                write_to_log("Checking Server connection....")
                self.client_socket.send(b"ping")
                sleep(5)  # Check every 5 seconds
            except (ConnectionAbortedError):
                
                # If connection fails, return to login screen
                self.StorageFrame.forget()
                self.LoginFrame.pack(fill="both", expand=True, padx=10, pady=10)
                self._messageBox.configure(text="Connection lost")
                self._loginButton.configure(state=Ctk.NORMAL)
                self._registerButton.configure(state=Ctk.NORMAL)
                break

if __name__ == "__main__":
    try:
        write_to_log("Press Ctrl + C to exit.")
        App = CClientGUI()
        App.run()
    except KeyboardInterrupt: # Ctrl + C
        exit()