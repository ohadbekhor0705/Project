import customtkinter as Ctk
from tkinter import ttk
from CServerBL import CServerBL
class StorageGUI(CServerBL):


    def __init__(self, parent_wnd):
        self.this_wnd = Ctk.CTkToplevel(parent_wnd)
        #Ctk.set_default_color_theme("./themes/rime.json")
        #Ctk.set_appearance_mode("System")
        self._savefile_button = None
        self._deletefile_button = None
        self._uploadfile_button = None
        self._filestbl = None
        self._searchbar = None
        self._search_button = None 
        self.FONT = ("Arial",24)
        self.create_ui()
        self.this_wnd.mainloop()
        self._title = None
       
        
    def create_ui(self):
        self.this_wnd.title("Browse Files")
        height, width = 750, 1300
        self.this_wnd.geometry(f"{width}x{height}")
        self.this_wnd.resizable(False, False)
        
        # creating UI widgets:
        self._title = Ctk.CTkLabel(self.this_wnd, text="Hi, {username}", anchor="center",font=self.FONT)
        self._title.place(relx=0.5, rely=0.04, anchor="center")

        self._searchbar = Ctk.CTkEntry(self.this_wnd, placeholder_text= "Search for files...", font = self.FONT)
        self._searchbar.place(relx = 0.1, rely=0.1, relheight=0.06, relwidth=0.65)
        

        self._search_button = Ctk.CTkButton(self.this_wnd, text="⌕", font=self.FONT)
        self._search_button.place(relx= 0.77, rely=0.1, relheight=0.06, relwidth=0.2)

        self._uploadfile_button = Ctk.CTkButton(self.this_wnd, text= "Upload File", font = self.FONT, anchor="center")
        self._uploadfile_button.place(relx= 0.1, rely=0.22, relheight=0.06, relwidth=0.15)

        self._savefile_button = Ctk.CTkButton(self.this_wnd, text="Save File", font=self.FONT, anchor="center")
        self._savefile_button.place(relx= 0.35, rely=0.22, relheight=0.06, relwidth=0.15)

        self._deletefile_button = Ctk.CTkButton(self.this_wnd, text="Delete File", font=self.FONT, anchor="center")
        self._deletefile_button.place(relx=0.6, rely=0.22, relheight=0.06, relwidth=0.15)

        # Create Custom styling
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 15))          # Table font
        style.configure("Treeview.Heading", font=("Arial", 25, "bold"), foreground="#490012")  # Header styling
        columns = ("file name", "file size (MB)", "Date")
        self._filestbl = ttk.Treeview(self.this_wnd, columns=columns, show="headings", )
        
        for col in columns:
            self._filestbl.heading(col, text=col)
            self._filestbl.column(col, width=int(0.65*width/len(columns)), anchor="center", stretch=False)
        self._filestbl.place(relx = 0.1, rely=0.34, relheight=0.6, relwidth=0.65)
        # Sample data 

        for row in range(300):
            self._filestbl.insert("", "end", values=(f"File{row+1}.txt", f"{row*5+3}", "2024-06-01 12:00:00"))


if __name__ == '__main__':
    GUI = StorageGUI(None)