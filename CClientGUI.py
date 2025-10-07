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
       
        

        self._usernameLabel = None
        self._usernameEntry = None
        self._passwordLabel = None
        self._passwordEntry = None
        self._loginButton = None

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
        
        global FONT
        self.master.geometry(f"{self.width}x{self.height}")
        # Create Tabs
        self.tab_view = Ctk.CTkTabview(master=self.master)
        self.tab_view._segmented_button.configure(font=Ctk.CTkFont(size=32, weight="bold"))
        self.tab_view.pack(expand=True, fill="both")
        self.tab_view.add("Login") 
        self.tab_view.add("StorageGUI") 

        self.StorageFrame: Ctk.CTkFrame = self.create_StorageFrame()
        self.StorageFrame.pack(expand=True, fill="both", padx=10, pady=10)

        self.LoginFrame: Ctk.CTkFrame = self.create_LoginFrame()
        self.LoginFrame.pack(expand=True, fill="both", padx=10, pady=10)

        self.master.resizable(True, True)

    def create_StorageFrame(self) -> Ctk.CTkFrame:
        # creating STORAGE GUI UI widgets:
        frame  = Ctk.CTkFrame(self.tab_view.tab("StorageGUI"))
        self._title = Ctk.CTkLabel(frame, text="Hi, {username}", anchor="center",font=FONT)
        self._title.place(relx=0.5, rely=0.04, anchor="center") 

        self._searchbar = Ctk.CTkEntry(frame, placeholder_text= "Search for files...", font = FONT)
        self._searchbar.place(relx = 0.1, rely=0.1, relheight=0.06, relwidth=0.65)

        self._search_button = Ctk.CTkButton(frame, text="⌕", font=FONT)
        self._search_button.place(relx= 0.77, rely=0.1, relheight=0.06, relwidth=0.2)  

        self._uploadfile_button = Ctk.CTkButton(frame, text= "Upload File", font = FONT, anchor="center")
        self._uploadfile_button.place(relx= 0.1, rely=0.22, relheight=0.06, relwidth=0.15) 

        self._savefile_button = Ctk.CTkButton(frame, text="Save File", font=FONT, anchor="center")
        self._savefile_button.place(relx= 0.35, rely=0.22, relheight=0.06, relwidth=0.15)  

        self._deletefile_button = Ctk.CTkButton(frame, text="Delete File", font=FONT, anchor="center")
        self._deletefile_button.place(relx=0.6, rely=0.22, relheight=0.06, relwidth=0.15)

        # Create Custom styling
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 15))          # Table font
        style.configure("Treeview.Heading", font=("Arial", 25, "bold"))  # Header styling
        columns = ("file name", "file size (MB)", "Date")
        self._filestbl = ttk.Treeview(frame, columns=columns, show="headings")
        for col in columns:
            self._filestbl.heading(col, text=col,anchor="center")
            self._filestbl.column(col, width=int(0.65*self.width/len(columns)), anchor="center", stretch=False)
        self._filestbl.place(relx = 0.1, rely=0.34, relheight=0.6, relwidth=0.65)
        # Sample data   
        for row in range(3):
            self._filestbl.insert("", "end", values=(f"File{row+1}.txt", f"{row*5+3}", "2024-06-01 12:00:00"))


        return frame
    

    def create_LoginFrame(self) ->Ctk.CTkFrame:
        global FONT
        
        # creating Login GUI UI widgets:

        frame = Ctk.CTkFrame(self.tab_view.tab("Login"))

        self._usernameLabel = Ctk.CTkLabel(frame, text="Username:", font=FONT, anchor="center")
        self._usernameLabel.place(relx = 0.1, rely = 0.15, relheight=0.06, relwidth=0.15)

        self._usernameEntry = Ctk.CTkEntry(frame, placeholder_text="Username", font=FONT)
        self._usernameEntry.place(relx=0.24, rely=0.15, relheight=0.06, relwidth=0.15)


        self._passwordLabel = Ctk.CTkLabel(frame,text= "Password:", font = FONT, anchor="center")
        self._passwordLabel.place(relx = 0.1, rely=0.27, relheight=0.06, relwidth=0.15)

        self._passwordEntry = Ctk.CTkEntry(frame, placeholder_text="Password", font= FONT)
        self._passwordEntry.place(relx = 0.24, rely = 0.27, relheight=0.06, relwidth=0.15)

        self._loginButton = Ctk.CTkButton(frame, text="Login", font=FONT, anchor="center",command=lambda: print("LOGIN COMMAND!!!"))
        self._loginButton.place(relx=0.1, rely=0.37, relheight=0.06,relwidth= 0.30)


        return frame

    def run(self) -> None: 
        self.master.mainloop()




class CLoginGUI(Ctk.CTkFrame):
    def __init__(self,parent) -> None:
        super().__init__(parent)



        
        

if __name__ == '__main__':
    try:
        App = CClientGUI()
        App.run()
    except KeyboardInterrupt: 
        exit()