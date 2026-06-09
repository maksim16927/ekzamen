import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from helpers import load_card_image, store_product_image, remove_product_image


class ProductForm(tk.Toplevel):
    def __init__(self, master, controller, product_id=None, on_save=None):
        super().__init__(master)
        self.controller = controller
        self.database = controller.database
        self.product_id = product_id
        self.on_save = on_save
        self.current_image_path = None
        self.selected_image_source = None
        self.preview_image = None

        self.is_edit = product_id is not None
        self.title("Редактирование товара" if self.is_edit else "Добавление товара")
        self.resizable(False, False)
        self.transient(master)
        self.grab_set()

        self.build_form()
        self.load_dictionaries()
        if self.is_edit:
            self.fill_from_database()
        else:
            self.id_var.set(str(self.database.get_next_product_id()))
            self.update_preview(None)

        self.protocol("WM_DELETE_WINDOW", self.close)
        self.center()

    def build_form(self):
        container = ttk.Frame(self, padding=15)
        container.pack(fill="both", expand=True)

        left = ttk.Frame(container)
        left.grid(row=0, column=0, padx=10, sticky="n")

        self.preview_label = ttk.Label(left)
        self.preview_label.pack()
        ttk.Button(left, text="Выбрать фото", command=self.choose_image).pack(pady=8)

        right = ttk.Frame(container)
        right.grid(row=0, column=1, sticky="n")

        self.id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.category_var = tk.StringVar()
        self.manufacturer_var = tk.StringVar()
        self.supplier_var = tk.StringVar()
        self.unit_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        self.discount_var = tk.StringVar(value="0")

        row = 0
        ttk.Label(right, text="ID товара:").grid(row=row, column=0, sticky="e", pady=5, padx=5)
        ttk.Entry(right, textvariable=self.id_var, state="readonly", width=35).grid(row=row, column=1, pady=5)

        row += 1
        ttk.Label(right, text="Наименование:").grid(row=row, column=0, sticky="e", pady=5, padx=5)
        ttk.Entry(right, textvariable=self.name_var, width=35).grid(row=row, column=1, pady=5)

        row += 1
        ttk.Label(right, text="Категория:").grid(row=row, column=0, sticky="e", pady=5, padx=5)
        self.category_box = ttk.Combobox(right, textvariable=self.category_var, state="readonly", width=33)
        self.category_box.grid(row=row, column=1, pady=5)

        row += 1
        ttk.Label(right, text="Описание:").grid(row=row, column=0, sticky="ne", pady=5, padx=5)
        self.description_text = tk.Text(right, width=35, height=4)
        self.description_text.grid(row=row, column=1, pady=5)

        row += 1
        ttk.Label(right, text="Производитель:").grid(row=row, column=0, sticky="e", pady=5, padx=5)
        self.manufacturer_box = ttk.Combobox(right, textvariable=self.manufacturer_var, state="readonly", width=33)
        self.manufacturer_box.grid(row=row, column=1, pady=5)

        row += 1
        ttk.Label(right, text="Поставщик:").grid(row=row, column=0, sticky="e", pady=5, padx=5)
        self.supplier_box = ttk.Combobox(right, textvariable=self.supplier_var, state="readonly", width=33)
        self.supplier_box.grid(row=row, column=1, pady=5)

        row += 1
        ttk.Label(right, text="Цена:").grid(row=row, column=0, sticky="e", pady=5, padx=5)
        ttk.Entry(right, textvariable=self.price_var, width=35).grid(row=row, column=1, pady=5)

        row += 1
        ttk.Label(right, text="Единица измерения:").grid(row=row, column=0, sticky="e", pady=5, padx=5)
        self.unit_box = ttk.Combobox(right, textvariable=self.unit_var, state="readonly", width=33)
        self.unit_box.grid(row=row, column=1, pady=5)

        row += 1
        ttk.Label(right, text="Количество на складе:").grid(row=row, column=0, sticky="e", pady=5, padx=5)
        ttk.Entry(right, textvariable=self.quantity_var, width=35).grid(row=row, column=1, pady=5)

        row += 1
        ttk.Label(right, text="Действующая скидка, %:").grid(row=row, column=0, sticky="e", pady=5, padx=5)
        ttk.Entry(right, textvariable=self.discount_var, width=35).grid(row=row, column=1, pady=5)

        buttons = ttk.Frame(container)
        buttons.grid(row=1, column=0, columnspan=2, pady=15)
        ttk.Button(buttons, text="Сохранить", command=self.save).pack(side="left", padx=10)
        ttk.Button(buttons, text="Назад", command=self.close).pack(side="left", padx=10)

    def load_dictionaries(self):
        self.categories = {row["category_name"]: row["category_id"] for row in self.database.get_categories()}
        self.manufacturers = {row["manufacturer_name"]: row["manufacturer_id"] for row in self.database.get_manufacturers()}
        self.suppliers = {row["supplier_name"]: row["supplier_id"] for row in self.database.get_suppliers()}
        self.units = {row["unit_name"]: row["unit_id"] for row in self.database.get_units()}
        self.category_box["values"] = list(self.categories.keys())
        self.manufacturer_box["values"] = list(self.manufacturers.keys())
        self.supplier_box["values"] = list(self.suppliers.keys())
        self.unit_box["values"] = list(self.units.keys())

    def fill_from_database(self):
        product = self.database.get_product(self.product_id)
        self.id_var.set(str(product["product_id"]))
        self.name_var.set(product["product_name"])
        self.description_text.insert("1.0", product["description"] or "")
        self.price_var.set("{:.2f}".format(product["price"]))
        self.quantity_var.set(str(product["quantity"]))
        self.discount_var.set("{:.0f}".format(product["discount"]))
        self.current_image_path = product["image_path"]

        for name, value in self.categories.items():
            if value == product["category_id"]:
                self.category_var.set(name)
        for name, value in self.manufacturers.items():
            if value == product["manufacturer_id"]:
                self.manufacturer_var.set(name)
        for name, value in self.suppliers.items():
            if value == product["supplier_id"]:
                self.supplier_var.set(name)
        for name, value in self.units.items():
            if value == product["unit_id"]:
                self.unit_var.set(name)
        self.update_preview(self.current_image_path)

    def update_preview(self, image_path):
        self.preview_image = load_card_image(image_path, (200, 150))
        self.preview_label.configure(image=self.preview_image)

    def choose_image(self):
        path = filedialog.askopenfilename(
            title="Выберите изображение товара",
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif")],
        )
        if not path:
            return
        self.selected_image_source = path
        self.update_preview(path)

    def validate(self):
        if not self.name_var.get().strip():
            messagebox.showwarning("Проверка данных", "Укажите наименование товара.")
            return None
        if not self.category_var.get():
            messagebox.showwarning("Проверка данных", "Выберите категорию товара.")
            return None
        if not self.manufacturer_var.get():
            messagebox.showwarning("Проверка данных", "Выберите производителя.")
            return None
        if not self.supplier_var.get():
            messagebox.showwarning("Проверка данных", "Выберите поставщика.")
            return None
        if not self.unit_var.get():
            messagebox.showwarning("Проверка данных", "Выберите единицу измерения.")
            return None
        try:
            price = float(self.price_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Цена должна быть числом. Допускаются сотые части, например 199.99.")
            return None
        if price < 0:
            messagebox.showerror("Ошибка ввода", "Цена не может быть отрицательной.")
            return None
        try:
            quantity = int(self.quantity_var.get())
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Количество на складе должно быть целым числом.")
            return None
        if quantity < 0:
            messagebox.showerror("Ошибка ввода", "Количество на складе не может быть отрицательным.")
            return None
        try:
            discount = float(self.discount_var.get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Скидка должна быть числом.")
            return None
        if discount < 0 or discount > 100:
            messagebox.showerror("Ошибка ввода", "Скидка должна быть в диапазоне от 0 до 100 процентов.")
            return None
        return {
            "product_name": self.name_var.get().strip(),
            "category_id": self.categories[self.category_var.get()],
            "description": self.description_text.get("1.0", "end").strip(),
            "manufacturer_id": self.manufacturers[self.manufacturer_var.get()],
            "supplier_id": self.suppliers[self.supplier_var.get()],
            "price": price,
            "unit_id": self.units[self.unit_var.get()],
            "quantity": quantity,
            "discount": discount,
        }

    def save(self):
        data = self.validate()
        if data is None:
            return
        image_path = self.current_image_path
        if self.selected_image_source:
            image_path = store_product_image(self.selected_image_source)
            if self.is_edit and self.current_image_path:
                remove_product_image(self.current_image_path)
        data["image_path"] = image_path

        if self.is_edit:
            self.database.update_product(self.product_id, data)
            messagebox.showinfo("Готово", "Изменения сохранены.")
        else:
            self.database.add_product(data)
            messagebox.showinfo("Готово", "Новый товар добавлен.")

        if self.on_save:
            self.on_save()
        self.close()

    def close(self):
        self.grab_release()
        self.destroy()

    def center(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry("+" + str(x) + "+" + str(y))
