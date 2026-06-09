import tkinter as tk
from tkinter import ttk, messagebox

from helpers import (
    load_card_image,
    load_logo,
    final_price,
    BACKGROUND_DISCOUNT,
    BACKGROUND_OUT_OF_STOCK,
    BACKGROUND_DEFAULT,
)
from product_form import ProductForm
from orders_window import OrdersWindow

SORT_OPTIONS = {
    "Без сортировки": None,
    "Наименование (А-Я)": "name_asc",
    "Наименование (Я-А)": "name_desc",
    "Цена (по возрастанию)": "price_asc",
    "Цена (по убыванию)": "price_desc",
    "Количество (по возрастанию)": "quantity_asc",
    "Количество (по убыванию)": "quantity_desc",
}


class CatalogWindow(ttk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.database = controller.database
        self.user = controller.current_user
        self.role = self.user["role"]
        self.can_manage = self.role == "Администратор"
        self.can_search = self.role in ("Менеджер", "Администратор")
        self.can_view_orders = self.role in ("Менеджер", "Администратор")
        self.card_images = []

        self.build_header()
        if self.can_search:
            self.build_toolbar()
        self.build_list_area()
        self.load_products()

    def build_header(self):
        header = tk.Frame(self, bg="#FF8C00")
        header.pack(fill="x")

        self.header_logo = load_logo((48, 48))
        tk.Label(header, image=self.header_logo, bg="#FF8C00").pack(side="left", padx=10, pady=8)
        tk.Label(
            header, text="Каталог товаров", bg="#FF8C00", fg="white",
            font=("Segoe UI", 16, "bold"),
        ).pack(side="left", padx=5)

        logout_button = ttk.Button(header, text="Выход", command=self.controller.open_login)
        logout_button.pack(side="right", padx=10)

        user_label = tk.Label(
            header, text=self.user["full_name"] + "  (" + self.role + ")",
            bg="#FF8C00", fg="white", font=("Segoe UI", 11, "bold"),
        )
        user_label.pack(side="right", padx=10)

        if self.can_view_orders:
            ttk.Button(header, text="Заказы", command=self.open_orders).pack(side="right", padx=5)

    def build_toolbar(self):
        toolbar = ttk.Frame(self, padding=8)
        toolbar.pack(fill="x")

        ttk.Label(toolbar, text="Поиск:").pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=30)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<Return>", lambda event: self.load_products())

        ttk.Button(toolbar, text="Найти", command=self.load_products).pack(side="left", padx=2)

        ttk.Label(toolbar, text="Категория:").pack(side="left", padx=(15, 2))
        self.category_var = tk.StringVar()
        self.category_map = {"Все категории": None}
        for row in self.database.get_categories():
            self.category_map[row["category_name"]] = row["category_id"]
        self.category_box = ttk.Combobox(
            toolbar, textvariable=self.category_var, values=list(self.category_map.keys()),
            state="readonly", width=20,
        )
        self.category_box.current(0)
        self.category_box.pack(side="left", padx=2)
        self.category_box.bind("<<ComboboxSelected>>", lambda event: self.load_products())

        ttk.Label(toolbar, text="Сортировка:").pack(side="left", padx=(15, 2))
        self.sort_var = tk.StringVar()
        self.sort_box = ttk.Combobox(
            toolbar, textvariable=self.sort_var, values=list(SORT_OPTIONS.keys()),
            state="readonly", width=24,
        )
        self.sort_box.current(0)
        self.sort_box.pack(side="left", padx=2)
        self.sort_box.bind("<<ComboboxSelected>>", lambda event: self.load_products())

        ttk.Button(toolbar, text="Сбросить", command=self.reset_filters).pack(side="left", padx=10)

        if self.can_manage:
            ttk.Button(toolbar, text="Добавить товар", command=self.add_product).pack(side="right")

    def build_list_area(self):
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.list_frame = tk.Frame(self.canvas, bg="#F0F0F0")

        self.list_frame.bind(
            "<Configure>",
            lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")),
        )
        self.window_id = self.canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfig(self.window_id, width=event.width),
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)

    def on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def reset_filters(self):
        self.search_var.set("")
        self.category_box.current(0)
        self.sort_box.current(0)
        self.load_products()

    def load_products(self):
        for widget in self.list_frame.winfo_children():
            widget.destroy()
        self.card_images = []

        search_text = ""
        category_id = None
        sort_key = None
        if self.can_search:
            search_text = self.search_var.get().strip()
            category_id = self.category_map.get(self.category_var.get())
            sort_key = SORT_OPTIONS.get(self.sort_var.get())

        products = self.database.get_products(search_text, category_id, sort_key)
        if not products:
            tk.Label(
                self.list_frame, text="Товары не найдены", bg="#F0F0F0",
                font=("Segoe UI", 12),
            ).pack(pady=30)
            return
        for product in products:
            self.create_card(product)

    def create_card(self, product):
        if product["quantity"] == 0:
            background = BACKGROUND_OUT_OF_STOCK
        elif product["discount"] > 17:
            background = BACKGROUND_DISCOUNT
        else:
            background = BACKGROUND_DEFAULT

        card = tk.Frame(self.list_frame, bg=background, bd=1, relief="solid")
        card.pack(fill="x", padx=5, pady=5)

        image = load_card_image(product["image_path"], (120, 90))
        self.card_images.append(image)
        photo_label = tk.Label(card, image=image, bg=background)
        photo_label.pack(side="left", padx=10, pady=10)

        info = tk.Frame(card, bg=background)
        info.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        title = product["category_name"] + " | " + product["product_name"]
        tk.Label(info, text=title, bg=background, fg="black", font=("Segoe UI", 12, "bold"), anchor="w").pack(fill="x")
        tk.Label(info, text="Описание: " + (product["description"] or ""), bg=background, fg="black", anchor="w", wraplength=600, justify="left").pack(fill="x")
        tk.Label(info, text="Производитель: " + product["manufacturer_name"], bg=background, fg="black", anchor="w").pack(fill="x")
        tk.Label(info, text="Поставщик: " + product["supplier_name"], bg=background, fg="black", anchor="w").pack(fill="x")

        price_row = tk.Frame(info, bg=background)
        price_row.pack(fill="x")
        tk.Label(price_row, text="Цена: ", bg=background, fg="black").pack(side="left")
        if product["discount"] > 0:
            tk.Label(
                price_row, text="{:.2f} ₽".format(product["price"]), bg=background,
                fg="red", font=("Segoe UI", 10, "overstrike"),
            ).pack(side="left")
            tk.Label(
                price_row, text="  {:.2f} ₽".format(final_price(product["price"], product["discount"])),
                bg=background, fg="black", font=("Segoe UI", 10, "bold"),
            ).pack(side="left")
        else:
            tk.Label(price_row, text="{:.2f} ₽".format(product["price"]), bg=background, fg="black").pack(side="left")

        tk.Label(info, text="Единица измерения: " + product["unit_name"], bg=background, fg="black", anchor="w").pack(fill="x")
        tk.Label(info, text="Количество на складе: " + str(product["quantity"]), bg=background, fg="black", anchor="w").pack(fill="x")

        side = tk.Frame(card, bg=background)
        side.pack(side="right", fill="y", padx=10, pady=10)
        tk.Label(
            side, text="Скидка\n{:.0f}%".format(product["discount"]), bg=background, fg="black",
            font=("Segoe UI", 12, "bold"), justify="center",
        ).pack()

        if self.can_manage:
            actions = tk.Frame(side, bg=background)
            actions.pack(pady=10)
            ttk.Button(actions, text="Изменить", command=lambda: self.edit_product(product["product_id"])).pack(pady=2)
            ttk.Button(actions, text="Удалить", command=lambda: self.delete_product(product)).pack(pady=2)
            for widget in [card, info, photo_label]:
                widget.bind("<Double-Button-1>", lambda event, pid=product["product_id"]: self.edit_product(pid))

    def add_product(self):
        ProductForm(self, self.controller, on_save=self.load_products)

    def edit_product(self, product_id):
        ProductForm(self, self.controller, product_id=product_id, on_save=self.load_products)

    def delete_product(self, product):
        if self.database.is_product_in_order(product["product_id"]):
            messagebox.showerror(
                "Удаление запрещено",
                "Товар «" + product["product_name"] + "» присутствует в заказе.\n"
                "Удалить такой товар нельзя.",
            )
            return
        confirm = messagebox.askyesno(
            "Подтверждение удаления",
            "Удалить товар «" + product["product_name"] + "»?\nЭто действие необратимо.",
        )
        if not confirm:
            return
        self.database.delete_product(product["product_id"])
        messagebox.showinfo("Готово", "Товар успешно удалён.")
        self.load_products()

    def open_orders(self):
        OrdersWindow(self, self.controller)
