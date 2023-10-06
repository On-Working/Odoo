from decouple import config
import requests
import html
import validators
import base64
import re
import odoo
import sysc

brands = sysc.sys_brands()
catalogue = sysc.sys_catalogue()


def sys_get_image(producto):
    image = producto.get("img_portada")

    url = validators.url(image)

    if not url:  # * Validación de la url
        return False

    get_image = requests.get(image)
    data_image = get_image.content
    binary_image = base64.b64encode(data_image)
    final_image = binary_image.decode("ascii")

    return final_image


def sys_creation():
    products = 10

    return products
