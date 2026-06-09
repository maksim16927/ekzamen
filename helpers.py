import os
from PIL import Image, ImageTk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
IMAGES_DIR = os.path.join(BASE_DIR, "product_images")
PLACEHOLDER = os.path.join(RESOURCES_DIR, "picture.png")
LOGO = os.path.join(RESOURCES_DIR, "logo.png")
MAX_WIDTH = 300
MAX_HEIGHT = 200

BACKGROUND_DISCOUNT = "#FFDEAD"
BACKGROUND_OUT_OF_STOCK = "#ADD8E6"
BACKGROUND_DEFAULT = "#FFFFFF"


def resource_path(name):
    return os.path.join(RESOURCES_DIR, name)


def load_card_image(image_path, size):
    source = image_path if image_path and os.path.exists(image_path) else PLACEHOLDER
    image = Image.open(source)
    image.thumbnail(size)
    return ImageTk.PhotoImage(image)


def load_logo(size):
    image = Image.open(LOGO)
    image.thumbnail(size)
    return ImageTk.PhotoImage(image)


def final_price(price, discount):
    return round(price * (1 - discount / 100), 2)


def store_product_image(source_path):
    if not os.path.exists(IMAGES_DIR):
        os.makedirs(IMAGES_DIR)
    image = Image.open(source_path)
    image.thumbnail((MAX_WIDTH, MAX_HEIGHT))
    base = os.path.splitext(os.path.basename(source_path))[0]
    index = 1
    target = os.path.join(IMAGES_DIR, base + ".png")
    while os.path.exists(target):
        target = os.path.join(IMAGES_DIR, base + "_" + str(index) + ".png")
        index += 1
    image.save(target, "PNG")
    return target


def remove_product_image(image_path):
    if image_path and os.path.exists(image_path) and os.path.commonpath([IMAGES_DIR, image_path]) == IMAGES_DIR:
        os.remove(image_path)
