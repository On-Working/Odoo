from decouple import config
import requests
import html
import validators
import base64
import re
import odoo
import sysc

db = config("odoo_test_db", default="")
# db = config("odoo_db", default="")
odo = odoo.odoo_connect(db)

uid = odo[0]
models = odo[1]
password = odo[2]

brands = sysc.sys_brands()
exchange = sysc.sys_exchange()


def attribute_created(objects, actions, sku, attrs):
    atts = attrs
    attributes = []

    product_data = models.execute_kw(
        db,
        uid,
        password,
        objects.get("product_template"),
        actions.get("s_read"),
        [[["default_code", "=", sku]]],
        {"fields": ["attribute_line_ids"]},
    )

    if not product_data:
        print(sku)
        return False

    attribute_pavs = product_data[0].get("attribute_line_ids")

    for attribute in attribute_pavs:
        attributes.append(attribute)

    for attr_id in attributes:
        attribute_value_info = models.execute_kw(
            db,
            uid,
            password,
            objects.get("attribute_value"),
            actions.get("s_read"),
            [[["pav_attribute_line_ids", "=", attr_id]]],
        )

        attribute_name = attribute_value_info[0].get("attribute_id")[1]

        if atts.__contains__(attribute_name):
            atts.pop(attribute_name)

    length = len(attrs)

    if length <= 0:
        return False

    product_attributes = []

    for attr_name, value in atts.items():
        attr_creat = attribute_creation(objects, actions, attr_name, value)
        product_attributes.append(attr_creat)

    return product_attributes


def attribute_creation(objects, actions, attribute_name, value):
    attribute_search = models.execute_kw(
        db,
        uid,
        password,
        objects.get("attribute"),
        actions.get("s_read"),
        [[["name", "=", attribute_name]]],
        {"fields": ["id"]},
    )

    attribute_id = attribute_search[0].get("id")

    attribute_value = models.execute_kw(
        db,
        uid,
        password,
        objects.get("attribute_value"),
        actions.get("s_read"),
        [[["name", "=", value]]],
        {"fields": ["id"]},
    )

    if attribute_value:
        attribute_value_id = attribute_value[0].get("id")
    else:
        attribute_value_id = models.execute_kw(
            db,
            uid,
            password,
            objects.get("attribute_value"),
            actions.get("create"),
            [
                {
                    "attribute_id": attribute_id,
                    "name": value,
                }
            ],
        )

    attribute = (
        0,
        0,
        {
            "attribute_id": attribute_id,
            "value_ids": [(4, attribute_value_id)],
        },
    )

    return attribute


def sys_get_image(product):
    image = product.get("img_portada")

    url = validators.url(image)

    if not url:  # * Validación de la url
        return False

    get_image = requests.get(image)
    data_image = get_image.content
    binary_image = base64.b64encode(data_image)
    final_image = binary_image.decode("ascii")

    return final_image


def sys_stock(product):
    total_stock = product.get("total_existencia")
    stock = 0

    if total_stock <= 0:
        return stock

    stock = product.get("existencia")
    new_stock = 0

    if stock.__contains__("nuevo"):
        new_stock = stock.get("nuevo")

    return new_stock


def ct_stock_created(objects, actions, id, qty):
    find = models.execute_kw(
        db,
        uid,
        password,
        objects.get("stock"),
        actions.get("s_read"),
        [[["location_id", "=", 419], ["product_id", "=", id]]],
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
            "location_id": 419,  # Ecommerce Syscom
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
        creation = ct_stock_creation(objects, actions, id, dif)

        return creation


def ct_stock_creation(objects, actions, id, qty):
    if qty == 0:
        return

    picking_order = {  # * Creacion de orden de inventario
        "partner_id": 1064,  # 1064 Syscom
        "picking_type_id": 303,  # Ecommerce: transferencias internas
        "move_type": "direct",
        "immediate_transfer": True,
        "priority": "1",
        "location_id": 3,  # 3 Virtual Locations
        "location_dest_id": 419,  # 419 Ecommerce - Syscom
        "move_ids": [
            (
                0,
                0,
                {
                    "name": "Actual stock",
                    "location_id": 3,  # Virtual Locations
                    "location_dest_id": 419,  # Syscom
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


def sys_created(objects, actions, sku):
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


def sys_creation(catalogue):
    success = 0
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
        name = product.get("titulo")
        brand = product.get("marca")
        sku = product.get("modelo")
        precios = product.get("precios")
        conversion = float(exchange)
        product_created = sys_created(objects, actions, sku)
        qty = sys_stock(product)

        if precios:  # * Precio en dolares por conversión
            costo = float(precios.get("precio_descuento"))
            precio = float(precios.get("precio_lista"))

        if not precios:
            costo = 0
            precio = 0

        costo *= conversion
        precio *= conversion
        final_image = sys_get_image(product)

        if qty <= 0:
            published = False

        product_template = {
            "is_published": published,
            "name": name,
            "default_code": sku,
            # "public_categ_ids": [(6, 0, [prod_category])],
            "sale_ok": True,
            "purchase_ok": True,
            "detailed_type": "product",  # Solo netdata
            "list_price": precio,
            "standard_price": costo,
            "description_purchase": "Producto Syscom",
            "description_sale": f"Producto: {name} \nMarca: {brand}",
            # "weight": product.get("peso"),
            # "volume": record.get("volume"),
            "image_1920": final_image,  # Encode base64
            "allow_out_of_stock_order": False,
            "show_availability": True,
            "available_threshold": 20,
            # "attribute_line_ids": attributes,
            # "unspsc_code_id": record.get("sat_code"),
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

            success += 1

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

            success += 1

    return success, errors


def sys_main():
    print("Iniciando creación y/o actualización de productos - SYSCOM")
    success = 0
    errors = 0
    # products_list = []

    for brand in brands:
        brand_id = brand.get("id")
        catalogue = sysc.sys_catalogue(brand_id)
        quantity = catalogue.get("cantidad")

        if quantity > 0:
            products = catalogue.get("productos")
            create = sys_creation(products)
            success += create[0]
            errors += create[1]

    print(f"Exitos: {success} - Errores: {errors}", end="\r")
    print("Operación SYSCOM en NetDataSolutions exitosa")
