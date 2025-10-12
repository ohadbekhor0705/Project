import customtkinter as Ctk
from tkinter import ttk
from CClientBL import CClientBL
import threading
import json
import os

class CClientGUI(CClientBL):

    def __init__(self) -> None:
        super().__init__()
        Ctk.set_default_color_theme("./themes/rime.json")
        Ctk.set_appearance_mode("Light")
        self.tab_view = None
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
        
        self.create_ui()
    

    def create_ui(self) -> None:
        
        self.master.geometry(f"{self.width}x{self.height}")
        # Create Tabs
        self.tab_view = Ctk.CTkTabview(master=self.master)
        self.tab_view._segmented_button.configure(font=Ctk.CTkFont(size=32, weight="bold"))
        self.tab_view.pack(expand=True, fill="both")
        self.tab_view.add("Login") 
        self.tab_view.add("StorageGUI") 
        # Create Frames
        self.StorageFrame: Ctk.CTkFrame = self.create_StorageFrame()
        self.StorageFrame.pack(expand=True, fill="both", padx=10, pady=10)

        self.LoginFrame: Ctk.CTkFrame = self.create_LoginFrame()
        self.LoginFrame.pack(expand=True, fill="both", padx=10, pady=10)

        self.master.resizable(False, False)

    def create_StorageFrame(self) -> Ctk.CTkFrame:
        # creating STORAGE UI widgets:

        StorageFrame: Ctk.CTkFrame = Ctk.CTkFrame(self.tab_view.tab("StorageGUI"))

        self._title = Ctk.CTkLabel(StorageFrame, text="Hi, {username}", anchor="center",font=self.FONT)
        self._title.place(relx=0.5, rely=0.04, anchor="center") 

        self._searchbar = Ctk.CTkEntry(StorageFrame, placeholder_text= "Search for files...", font = self.FONT)
        self._searchbar.place(relx = 0.1, rely=0.1, relheight=0.06, relwidth=0.65)

        self._search_button = Ctk.CTkButton(StorageFrame, text="🔍", font=self.FONT)
        self._search_button.place(relx= 0.77, rely=0.1, relheight=0.06, relwidth=0.2)  

        self._uploadfile_button = Ctk.CTkButton(StorageFrame, text= "Upload 📤", font = self.FONT, anchor="center")
        self._uploadfile_button.place(relx= 0.1, rely=0.22, relheight=0.06, relwidth=0.15) 

        self._savefile_button = Ctk.CTkButton(StorageFrame, text="Save 💾", font=self.FONT, anchor="center")
        self._savefile_button.place(relx= 0.35, rely=0.22, relheight=0.06, relwidth=0.15)  

        self._deletefile_button = Ctk.CTkButton(StorageFrame, text="Delete 🗑️", font=self.FONT, anchor="center")
        self._deletefile_button.place(relx=0.6, rely=0.22, relheight=0.06, relwidth=0.15)

        # Create Custom styling
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 15))    # Table font
        style.configure("Treeview.Heading", font=("Arial", 25, "bold"))  # Header styling
        columns = ("file name", "file size (MB)", "Date modified")
        self._filestbl = ttk.Treeview(StorageFrame, columns=columns, show="headings")
        for col in columns:
            self._filestbl.heading(col, text=col,anchor="center")
            self._filestbl.column(col, width=int(0.65*self.width/len(columns)), anchor="center", stretch=False)
        self._filestbl.place(relx = 0.1, rely=0.34, relheight=0.6, relwidth=0.65)


        return StorageFrame
    
    def create_LoginFrame(self) ->Ctk.CTkFrame:
        
        # creating Login UI widgets:

        LoginFrame: Ctk.CTkFrame = Ctk.CTkFrame(self.tab_view.tab("Login"))

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
        self.remember_action("SET")

        self._loginButton = Ctk.CTkButton(LoginFrame, text="Login", font=self.FONT, anchor="center",command=lambda: threading.Thread(target=self.on_click_login).start())
        self._loginButton.place(relx=0.1, rely=0.47, relheight=0.06,relwidth= 0.135)
        
        self._registerButton = Ctk.CTkButton(LoginFrame, text="Register", font=self.FONT, anchor="center")
        self._registerButton.place(relx=0.24, rely=0.47, relheight=0.06,relwidth= 0.135)


        return LoginFrame

    def run(self) -> None: self.master.mainloop()

    def on_click_login(self) -> None:
        username: str = self._usernameEntry.get().lstrip()
        password: str = self._passwordEntry.get().lstrip()
        
        if not username or not password:
            self._messageBox.configure(text="You must fill all the fields!")
            return
        self.remember_action("SAVE",username=username,password=password)
        self._messageBox.configure(text="Connecting....")
        response , self.client_socket = self.connect(username,password)
        if self.client_socket:
            self._messageBox.configure(state=Ctk.DISABLED)
        self._messageBox.configure(text=response)
        
    def remember_action(self, action: str, **user_data)  -> None:
        remember: bool = self._checkBox.get() == True
        print(remember)
        try:
            if action == "SAVE":
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
            elif action == "SET" and os.path.exists("./user.json"):
                with open("./user.json", "r") as json_file:
                    values: dict = json.load(json_file)
                    print(values["remember"])
                    if values["remember"]:
                        self._usernameEntry.insert(0,values["username"])
                        self._passwordEntry.insert(0, values["password"])
                        self._checkBox.select()
            else:
                raise Exception("WRONG CHECKBOX COMMAND!")

        except Exception as e:
            print(e)

if __name__ == "__main__":
    try:
        App = CClientGUI()
        App.run()
    except KeyboardInterrupt: # Ctrl + C
        exit()