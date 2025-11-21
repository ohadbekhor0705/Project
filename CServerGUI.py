try:
    import customtkinter as CTk
    from tkinter import ttk
    from CServerBL import CServerBL
    import threading
    from protocol import *
except ModuleNotFoundError:
    print("please run command on the terminal: pip install -r requirements.txt")

class CServerGUI(CServerBL):
    def __init__(self) -> None:
        super().__init__()
        CTk.set_appearance_mode("Dark")
        self.master = CTk.CTk()
        self.FONT: tuple[str, int] = ("Helvetica",24)
        self._ipLabel = None
        self._portLabel = None
        self.serverSwitch = None
        self.height, self.width = 750, 1300
        ###Treeview Customization (theme colors are selected)
        self.bg_color: str = self.master._apply_appearance_mode(CTk.ThemeManager.theme["CTkFrame"]["fg_color"])
        self.text_color: str = self.master._apply_appearance_mode(CTk.ThemeManager.theme["CTkLabel"]["text_color"])
        self.selected_color: str = self.master._apply_appearance_mode(CTk.ThemeManager.theme["CTkButton"]["fg_color"])



        self.create_ui()
    
    def create_ui(self) -> None:
        self.master.geometry(f"{self.width}x{self.height/2}")
        self.master.resizable(False, False)
        self.master.title("Server GUI")

        CTk.CTkLabel(self.master, text= "Server Graphical User Interface",anchor="center",font=self.FONT).place(relx = 0, rely=0.1, relheight=0.06, relwidth=1)
        #####
        # Code from https://github.com/TomSchimansky/CustomTkinter/discussions/431
        #style = ttk.Style() 
        #style.theme_use("default")
        #
        #style.configure("Treeview",
        #                    background="#2a2d2e",
        #                    foreground="white",
        #                    rowheight=30,
        #                    fieldbackground="#343638",
        #                    bordercolor="#343638",
        #                    borderwidth=0, font=("Helvetica",16))
        #style.map('Treeview', background=[('selected', '#22559b')])
    #
        #style.configure("Treeview.Heading",background="#565b5e",foreground="white",relief="flat", font=self.FONT)
        #style.map("Treeview.Heading",background=[('active', '#3484F0')])
        ######
#
        #columns = ("Hostname", "IP Address", "Username")
        #self.clients_table = ttk.Treeview(self.master, columns=columns, show="headings")
        #for col in columns:
            #self.clients_table.heading(col, text=col,anchor="center")
            #self.clients_table.column(col, width=int(0.9*self.width/len(columns)), anchor="center", stretch=False)
        #self.clients_table.place(relx = 0.05, rely=0.35, relheight=0.6, relwidth=0.9)

        #self.clients_table.insert("", "end", values=("Hostname", "xxx.xxx.xxx.xxx", "None","❌"))
        #self.clients_table.insert("", "end", values=("Hostname", "xxx.xxx.xxx.xxx", "username","✅"))

        self.serverSwitch = CTk.CTkSwitch(self.master, variable=CTk.StringVar(value="off"),switch_width=250,switch_height=50, text= "Toggle on/off",
                                          font=self.FONT,onvalue="on", offvalue="off", command=self.toggle_server )
        self.serverSwitch.place(relx = 0.05, rely = 0.25)

    def toggle_server(self):
        if self.serverSwitch.get() == "on":
            write_to_log("on")
            self.main_thread = threading.Thread(target=self.start_server)
            self.main_thread.start()
        if self.serverSwitch.get() == "off":
            write_to_log("off")
            self.stop_server()

    def run(self) -> None:
        self.master.mainloop()


if __name__ == "__main__":
    App = CServerGUI()
    App.run()
    exit()
