import tkinter as tk
from tkinter import ttk, messagebox

from helpers import load_logo


class LoginWindow(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master, padding=40)
        self.controller = controller

        self.logo_image = load_logo((140, 140))
        logo_label = ttk.Label(self, image=self.logo_image)
        logo_label.pack(pady=(10, 5))

        title_label = ttk.Label(self, text="Магазин игрушек «ToyStore»", font=("Segoe UI", 18, "bold"))
        title_label.pack(pady=(0, 20))

        form = ttk.Frame(self)
        form.pack()

        ttk.Label(form, text="Логин:").grid(row=0, column=0, sticky="e", padx=5, pady=8)
        self.login_entry = ttk.Entry(form, width=28)
        self.login_entry.grid(row=0, column=1, padx=5, pady=8)

        ttk.Label(form, text="Пароль:").grid(row=1, column=0, sticky="e", padx=5, pady=8)
        self.password_entry = ttk.Entry(form, width=28, show="•")
        self.password_entry.grid(row=1, column=1, padx=5, pady=8)

        buttons = ttk.Frame(self)
        buttons.pack(pady=20)

        login_button = ttk.Button(buttons, text="Войти", width=20, command=self.sign_in)
        login_button.grid(row=0, column=0, padx=5, pady=5)

        guest_button = ttk.Button(buttons, text="Войти как гость", width=20, command=self.sign_in_guest)
        guest_button.grid(row=1, column=0, padx=5, pady=5)

        self.login_entry.focus_set()
        self.password_entry.bind("<Return>", lambda event: self.sign_in())

    def sign_in(self):
        login = self.login_entry.get().strip()
        password = self.password_entry.get().strip()
        if not login or not password:
            messagebox.showwarning("Внимание", "Введите логин и пароль для входа в систему.")
            return
        user = self.controller.database.authorize(login, password)
        if user is None:
            messagebox.showerror("Ошибка авторизации", "Неверный логин или пароль.\nПроверьте введённые данные и повторите попытку.")
            return
        self.controller.open_catalog({
            "user_id": user["user_id"],
            "full_name": user["full_name"],
            "role": user["role_name"],
        })

    def sign_in_guest(self):
        self.controller.open_catalog({
            "user_id": None,
            "full_name": "Гость",
            "role": "Гость",
        })
