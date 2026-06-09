import tkinter as tk
from tkinter import ttk


class OrdersWindow(tk.Toplevel):
    def __init__(self, master, controller):
        super().__init__(master)
        self.database = controller.database
        self.title("Заказы")
        self.geometry("600x400")
        self.transient(master)
        self.grab_set()

        ttk.Label(self, text="Список заказов", font=("Segoe UI", 14, "bold")).pack(pady=10)

        columns = ("order_id", "order_date", "full_name", "positions", "total_items")
        tree = ttk.Treeview(self, columns=columns, show="headings")
        tree.heading("order_id", text="№ заказа")
        tree.heading("order_date", text="Дата")
        tree.heading("full_name", text="Заказчик")
        tree.heading("positions", text="Позиций")
        tree.heading("total_items", text="Всего товаров")
        tree.column("order_id", width=70, anchor="center")
        tree.column("order_date", width=100, anchor="center")
        tree.column("full_name", width=220)
        tree.column("positions", width=80, anchor="center")
        tree.column("total_items", width=110, anchor="center")
        tree.pack(fill="both", expand=True, padx=10, pady=10)

        for order in self.database.get_orders():
            tree.insert("", "end", values=(
                order["order_id"],
                order["order_date"],
                order["full_name"],
                order["positions"],
                order["total_items"] or 0,
            ))

        ttk.Button(self, text="Назад", command=self.destroy).pack(pady=10)
