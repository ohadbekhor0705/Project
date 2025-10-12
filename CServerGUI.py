import customtkinter as CTk
from tkinter import ttk
from CServerBL import CServerBL


class CServerGUI(CServerBL):
    def __init__(self) -> None:
        super().__init__()
        CTk.set_appearance_mode("Dark")
        self.master = CTk.CTk()

        self._ipLabel = None
        self._portLabel = None
        self._startButton = None
        self.height, self.width = 750, 1100
        self.create_ui()
    
    def create_ui(self) -> None:
        self.master.geometry(f"{self.width}x{self.height}")
        self.master.resizable(False, False)
        self.master.title("Server GUI")
    
    def run(self) -> None:
        self.master.mainloop()


if __name__ == "__main__":
    App = CServerGUI()
    App.run()
