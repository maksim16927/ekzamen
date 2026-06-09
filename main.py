import tkinter as tk
from tkinter import ttk

from database import Database
from helpers import load_logo
from login_window import LoginWindow
from catalog_window import CatalogWindow


class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.database = Database()
        self.current_user = None
        self.active_frame = None
        self.geometry("1024x720")
        self.minsize(900, 600)
        self.set_icon()
        self.open_login()

    def set_icon(self):
        try:
            self.app_icon = load_logo((64, 64))
            self.iconphoto(True, self.app_icon)
        except Exception:
            pass

    def clear_frame(self):
        if self.active_frame is not None:
            self.active_frame.destroy()
            self.active_frame = None

    def open_login(self):
        self.current_user = None
        self.clear_frame()
        self.title("Магазин игрушек «ToyStore» — Вход в систему")
        self.active_frame = LoginWindow(self, self)
        self.active_frame.pack(fill="both", expand=True)

    def open_catalog(self, user):
        self.current_user = user
        self.clear_frame()
        self.title("Магазин игрушек «ToyStore» — Каталог товаров")
        self.active_frame = CatalogWindow(self, self)
        self.active_frame.pack(fill="both", expand=True)


def main():
    app = Application()
    style = ttk.Style(app)
    if "vista" in style.theme_names():
        style.theme_use("vista")
    elif "clam" in style.theme_names():
        style.theme_use("clam")
    app.mainloop()


if __name__ == "__main__":
    main()
