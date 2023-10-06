from decouple import config
import requests
import html
import validators
import base64
import re
import odoo
import ct

db = config("odoo_db", default="")
odo = odoo.odoo_connect(db)

uid = odo[0]
models = odo[1]
password = odo[2]

catalogue = ct.ct_catalogue()
stock = ct.ct_stock()


def ct_get_image(producto):
    image = producto.get("imagen")

    url = validators.url(image)

    if not url:  # * Validación de la url
        return False

    get_image = requests.get(image)
    data_image = get_image.content
    binary_image = base64.b64encode(data_image)
    final_image = binary_image.decode("ascii")

    return final_image


def ct_created(objects, actions, sku):
    found = False
    find = models.execute_kw(
        db,
        uid,
        password,
        objects.get("products"),
        actions.get("search"),
        [[["default_code", "=", sku]]],
    )

    if find:
        found = True

    return found, find


def ct_price(product):
    promociones = product.get("promociones")
    moneda = product.get("moneda")
    cambio = product.get("tipoCambio")

    if promociones:
        costo = promociones[0].get("promocion")
    precio = product.get("precio")

    # * En caso de no existir costo, aplicar 10% costo más impuestos
    if not promociones:
        costo = precio
        precio = costo + ((costo * 10) / 100)

    # * Conversión de moneda de cambio
    if moneda == "USD":
        costo *= cambio
        precio *= cambio

    return costo, precio


def ct_creation():
    print("Iniciando creación y/o actualización de productos")
    products = 0
    errors = 0

    objects = {  # Modelos disponibles en Odoo
        "products": "product.product",
        "product": "product.template",
        "product_category": "product.public.category",
        "attribute": "product.attribute",
        "attribute_value": "product.attribute.value",
        "stock": "stock.quant",
        "intern": "stock.picking",
        "scrap": "stock.scrap",
    }

    actions = {  # Acciones disponibles en Odoo
        "search": "search",
        "read": "read",
        "s_read": "search_read",
        "write": "write",
        "create": "create",
        "validate": "action_validate",
        "button": "button_validate",
    }

    for product in catalogue:
        published = True
        sku = product.get("clave")

        # * Funciones
        final_image = ct_get_image(product)
        product_created = ct_created(objects, actions, sku)
        prices = ct_price(product)
        worth = prices[0]
        price = prices[1]

        product_template = {
            "is_published": published,
            "name": product.get("nombre"),
            "default_code": sku,
            # "public_categ_ids": [(6, 0, [prod_category])], # Creación de categoria
            "sale_ok": True,
            "purchase_ok": True,
            "detailed_type": "product",  # Solo netdata
            "list_price": worth,
            "standard_price": price,
            "description_purchase": "Producto CT",
            "description_sale": product.get("descripcion_corta"),
            # "weight": record.get("weight"),
            # "volume": record.get("volume"),
            "image_1920": final_image,
            "allow_out_of_stock_order": False,
            "show_availability": True,
            "available_threshold": 20,
            # "attribute_line_ids": attributes, # Creación de atributos
            # "unspsc_code_id": record.get("sat_code"), # Envio de codigo sat
        }

        if final_image == False:
            product_template.pop("image_1920")

        if product_created[0]:
            prod_id = product_created[1][0]
            write = models.execute_kw(
                db,
                uid,
                password,
                objects.get("products"),
                actions.get("write"),
                [[prod_id], product_template],
            )

            products += 1

        else:
            create = models.execute_kw(
                db,
                uid,
                password,
                objects.get("product"),
                actions.get("create"),
                [product_template],
            )

            products += 1

        print(f"Exitos: {products} - Errores: {errors}", end="\r")

    print("Operación en NetDataSolutions exitosa")
