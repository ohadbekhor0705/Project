import customtkinter as Ctk
from tkinter import ttk
from CClientBL import CClientBL


FONT: tuple[str, int] = ("Helvetica",24)

class CClientGUI(CClientBL):


    def __init__(self) -> None:
        super().__init__()
        #Ctk.set_default_color_theme("./themes/rime.json")
        #Ctk.set_appearance_mode("System")
        self.tab_view = None
        self.master = Ctk.CTk()
        self.create_ui()
        
        self.StorageFrame: CStorageGUI = None
        self.LoginFrame: CLoginGUI = None

        
    def create_ui(self) -> None:
        height, width = 750, 1300
        global FONT
        self.master.geometry(f"{width}x{height}")
        # Create Tabs
        self.tab_view = Ctk.CTkTabview(master=self.master)
        self.tab_view._segmented_button.configure(font=Ctk.CTkFont(size=32, weight="bold"))
        self.tab_view.pack(expand=True, fill="both")
        self.tab_view.add("Login") 
        self.tab_view.add("StorageGUI") 

        self.StorageFrame = CStorageGUI(self.tab_view.tab("StorageGUI"))
        self.StorageFrame.pack(expand=True, fill="both", padx=10, pady=10)
        self.LoginFrame = CLoginGUI(self.tab_view.tab("Login"), )
        self.LoginFrame.pack(expand=True, fill="both", padx=10, pady=10)

        self.master.resizable(True, True)


    def on_click_login(self):
        username = self.LoginFrame._usernameEntry.get()
        password = self.LoginFrame._passwordEntry().get()

        self.client_socket = self.connect(username,password)
        if self.connected:
            print("WORKED")


    def run(self) -> None: 
        self.master.mainloop()





class CStorageGUI(Ctk.CTkFrame):
    def __init__(self, parent) -> None:
        super().__init__(parent)
       
        self._savefile_button = None
        self._deletefile_button = None
        self._uploadfile_button = None
        self._filestbl = None
        self._searchbar = None
        self._search_button = None  

        self._title = None  

        self.create_widgets()
    
    def create_widgets(self) -> None:
        global FONT 
        height, width = 750, 1300
        # creating UI widgets:
        self._title = Ctk.CTkLabel(self, text="Hi, {username}", anchor="center",font=FONT)
        self._title.place(relx=0.5, rely=0.04, anchor="center") 

        self._searchbar = Ctk.CTkEntry(self, placeholder_text= "Search for files...", font = FONT)
        self._searchbar.place(relx = 0.1, rely=0.1, relheight=0.06, relwidth=0.65)

        self._search_button = Ctk.CTkButton(self, text="⌕", font=FONT)
        self._search_button.place(relx= 0.77, rely=0.1, relheight=0.06, relwidth=0.2)   

        self._uploadfile_button = Ctk.CTkButton(self, text= "Upload File", font = FONT, anchor="center")
        self._uploadfile_button.place(relx= 0.1, rely=0.22, relheight=0.06, relwidth=0.15)  

        self._savefile_button = Ctk.CTkButton(self, text="Save File", font=FONT, anchor="center")
        self._savefile_button.place(relx= 0.35, rely=0.22, relheight=0.06, relwidth=0.15)   

        self._deletefile_button = Ctk.CTkButton(self, text="Delete File", font=FONT, anchor="center")
        self._deletefile_button.place(relx=0.6, rely=0.22, relheight=0.06, relwidth=0.15)

        # Create Custom styling
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 15))          # Table font
        style.configure("Treeview.Heading", font=("Arial", 25, "bold"))  # Header styling
        columns = ("file name", "file size (MB)", "Date")
        self._filestbl = ttk.Treeview(self, columns=columns, show="headings")

        for col in columns:
            self._filestbl.heading(col, text=col,anchor="center")
            self._filestbl.column(col, width=int(0.65*width/len(columns)), anchor="center", stretch=False)
        self._filestbl.place(relx = 0.1, rely=0.34, relheight=0.6, relwidth=0.65)
        # Sample data   
        for row in range(3):
            self._filestbl.insert("", "end", values=(f"File{row+1}.txt", f"{row*5+3}", "2024-06-01 12:00:00"))

class CLoginGUI(Ctk.CTkFrame):
    def __init__(self,parent, on_click_login) -> None:
        super().__init__(parent)
        
        self.on_click_login = on_click_login

        self._usernameLabel = None
        self._usernameEntry = None
        self._passwordLabel = None
        self._passwordEntry = None
        self._loginButton = None
        self.create_widgets()

    def create_widgets(self) -> None:
        global FONT
        



        self._usernameLabel = Ctk.CTkLabel(self, text="Username:", font=FONT, anchor="center")
        self._usernameLabel.place(relx = 0.1, rely = 0.15, relheight=0.06, relwidth=0.15)

        self._usernameEntry = Ctk.CTkEntry(self, placeholder_text="Username", font=FONT)
        self._usernameEntry.place(relx=0.24, rely=0.15, relheight=0.06, relwidth=0.15)


        self._passwordLabel = Ctk.CTkLabel(self,text= "Password:", font = FONT, anchor="center")
        self._passwordLabel.place(relx = 0.1, rely=0.27, relheight=0.06, relwidth=0.15)

        self._passwordEntry = Ctk.CTkEntry(self, placeholder_text="Password", font= FONT)
        self._passwordEntry.place(relx = 0.24, rely = 0.27, relheight=0.06, relwidth=0.15)

        self._loginButton = Ctk.CTkButton(self, text="Login", font=FONT, anchor="center",command=self.on_click_login)
        self._loginButton.place(relx=0.1, rely=0.37, relheight=0.06,relwidth= 0.30)


        
        

if __name__ == '__main__':
    try:
        App = CClientGUI()
        App.run()
    except KeyboardInterrupt: 
        exit()