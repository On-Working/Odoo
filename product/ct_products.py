from decouple import config
import requests
import html
import validators
import base64
import re
import odoo
import ct

db = config("odoo_test_db", default="")
# db = config("odoo_db", default="")
odo = odoo.odoo_connect(db)

uid = odo[0]
models = odo[1]
password = odo[2]

catalogue = ct.ct_catalogue()
stock = ct.ct_stock()


def ct_get_image(product):
    image = product.get("imagen")

    url = validators.url(image)

    if not url:  # * Validación de la url
        return False

    get_image = requests.get(image)
    data_image = get_image.content
    binary_image = base64.b64encode(data_image)
    final_image = binary_image.decode("ascii")

    return final_image


def ct_stock(producto):
    stock = producto.get("existencia")
    cun_stock = 0

    if stock.__contains__("CUN"):
        cun_stock = stock.get("CUN")

    return cun_stock


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


def ct_stock_created(objects, actions, id, qty):
    find = models.execute_kw(
        db,
        uid,
        password,
        objects.get("stock"),
        actions.get("s_read"),
        [[["location_id", "=", 418], ["product_id", "=", id]]],
        {"fields": ["quantity"]},
    )

    if not find:
        creation = ct_stock_creation(objects, actions, id, qty)
        return creation

    stock = find[0]["quantity"]

    dif = qty - stock

    if dif == 0:
        return

    if dif < 0:
        done = stock - qty

        scrap_order = {  # * Creacion de orden de desecho
            "product_id": id,
            "scrap_qty": done,
            "location_id": 418,  # Ecommerce CT
            "scrap_location_id": 352,  # Ecommerce Scrap
        }

        # * Orden de desecho
        scrap_creation = models.execute_kw(
            db,
            uid,
            password,
            objects.get("scrap"),
            actions.get("create"),
            [scrap_order],
        )

        # * Validación
        scrap_confirmation = models.execute_kw(
            db,
            uid,
            password,
            objects.get("scrap"),
            actions.get("validate"),
            [scrap_creation],
            {},
        )

        return scrap_confirmation

    else:
        picking_order = {  # * Creacion de orden de inventario
            "partner_id": 206,  # 10 Jorge # 206 Tecnosinergia
            "picking_type_id": 303,  # Ecommerce:interno Tipo recibo
            "move_type": "direct",
            "immediate_transfer": True,
            "priority": "1",
            "location_id": 418,  # 418 CT
            "location_dest_id": 336,  # 336 Ecommerce
            "move_ids": [
                (
                    0,
                    0,
                    {
                        "name": "Actual stock",
                        "location_id": 351,  # Tecnosinergia
                        "location_dest_id": 336,  # Ecommerce
                        "product_id": id,
                        "product_uom": 1,
                        "quantity_done": dif,
                    },
                )
            ],
        }

        # * Creation
        picking_creation = models.execute_kw(
            db,
            uid,
            password,
            objects.get("intern"),
            actions.get("create"),
            [picking_order],
        )

        picking_confirmation = models.execute_kw(
            db,
            uid,
            password,
            objects.get("intern"),
            actions.get("button"),
            [picking_creation],
        )

        return picking_confirmation


def ct_stock_creation(objects, actions, id, qty):
    if qty == 0:
        return

    picking_order = {  # * Creacion de orden de inventario
        "partner_id": 887,  # 887 CT
        "picking_type_id": 303,  # Ecommerce: transferencias internas
        "move_type": "direct",
        "immediate_transfer": True,
        "priority": "1",
        "location_id": 3,  # 3 Virtual Locations
        "location_dest_id": 418,  # 418 Ecommerce - CT
        "move_ids": [
            (
                0,
                0,
                {
                    "name": "Actual stock",
                    "location_id": 3,  # Virtual Locations
                    "location_dest_id": 418,  # CT
                    "product_id": id,
                    "product_uom": 1,
                    "quantity_done": qty,
                },
            )
        ],
    }

    # * Creation
    picking_creation = models.execute_kw(
        db,
        uid,
        password,
        objects.get("intern"),
        actions.get("create"),
        [picking_order],
    )

    picking_confirmation = models.execute_kw(
        db,
        uid,
        password,
        objects.get("intern"),
        actions.get("button"),
        [picking_creation],
    )

    return picking_confirmation


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


def ct_creation():
    print("Iniciando creación y/o actualización de productos - CT")
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
        sku = product.get("clave")
        final_image = ct_get_image(product)
        product_created = ct_created(objects, actions, sku)
        prices = ct_price(product)
        qty = ct_stock(product)
        worth = prices[0]
        price = prices[1]
        published = True

        if qty <= 0:
            published = False

        product_template = {
            "is_published": published,
            "name": product.get("nombre"),
            "default_code": sku,
            # "public_categ_ids": [(6, 0, [prod_category])], # Creación de categoria
            "sale_ok": True,
            "purchase_ok": True,
            "detailed_type": "product",  # Solo netdata
            "list_price": price,
            "standard_price": worth,
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

            stock = ct_stock_created(objects, actions, prod_id, qty)

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

            try:
                stock = ct_stock_creation(objects, actions, create, qty)
            except:
                errors += 1

            products += 1

        print(f"Exitos: {products} - Errores: {errors}", end="\r")

    print("Operación CT en NetDataSolutions exitosa")
