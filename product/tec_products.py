import tec
import requests
import html
import validators
import base64
import re
import time

from decouple import config
from PIL import Image
from io import BytesIO
import odoo as netdata


def tec_get_image(record):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    }

    image = record.get("image")

    url = validators.url(image)

    if not url:  # * Validación de la url
        image = config("NDS_DEF_IMG", default="")

    try:
        get_image = requests.get(image, headers=headers)
    except Exception as e:
        del e
        return False

    try:
        data_image = get_image.content
        img = Image.open(BytesIO(data_image))
        img_size = img.size
        x, y = img_size
        if x or y > 5000:
            nx = x / 2
            ny = y / 2
            nsize = (round(nx), round(ny))
            nimage = img.resize(nsize)
            buffer = BytesIO()
            nimage.save(buffer, format="PNG")
            data_image = buffer.getvalue()
    except Exception as e:
        image = config("NDS_DEF_IMG", default="")
        get_image = requests.get(image)
        data_image = get_image.content
        del e

    binary_image = base64.b64encode(data_image)
    final_image = binary_image.decode("ascii")

    return final_image


def tec_desc_format(text):
    words = text.split()
    formatted_text = ""

    for word in words:
        if word == "":
            formatted_text += "\n\n"

        elif word.endswith("."):
            formatted_text += word + "\n\n"

        else:
            formatted_text += word + "  "

    pattern = r"[\x00-\x1F\x7F-\x9F]"

    return re.sub(pattern, "", formatted_text.strip())


def tec_cat_created(odoo, objects, actions, name):
    if name == "":
        return (False, [])

    uid, models, db, password = odoo
    found = False
    find = models.execute_kw(
        db,
        uid,
        password,
        objects.get("product_category"),
        actions.get("s_read"),
        [[["name", "=", name]]],
        {"fields": ["parent_id"]},
    )

    if find:
        found = True

    return found, find


def tec_cat_creation(odoo, objects, actions, record):
    uid, models, db, password = odoo
    category = html.unescape(record.get("line"))

    if category == "":
        category = html.unescape(record.get("category"))

    if category == "":
        return False

    category_created = tec_cat_created(odoo, objects, actions, category)

    cat_data = {
        "name": category,
        "website_description": category,
    }

    if category_created[0]:
        category_id = category_created[1][0].get("id")

        return category_id

    try:
        create = models.execute_kw(
            db,
            uid,
            password,
            objects.get("product_category"),
            actions.get("create"),
            [cat_data],
        )

    except Exception as e:

        create = models.execute_kw(
            db,
            uid,
            password,
            objects.get("product_category"),
            actions.get("create"),
            [cat_data],
        )

        del e

    return create


def tec_stock_created(odoo, objects, actions, p_id, p_qty):
    uid, models, db, password = odoo
    location_id = 420  # Tecnosinergia
    scrap_location_id = 352  # Ecommerce Scrap

    find = models.execute_kw(
        db,
        uid,
        password,
        objects.get("stock"),
        actions.get("s_read"),
        [[["location_id", "=", location_id], ["product_id", "=", p_id]]],
        {"fields": ["quantity"]},
    )

    if not find:
        creation = tec_stock_creation(odoo, objects, actions, p_id, p_qty)
        return creation

    stock = find[0]["quantity"]

    dif = p_qty - stock

    if dif == 0:
        return

    if dif < 0:
        done = stock - p_qty

        scrap_order = {  # * Creacion de orden de desecho
            "product_id": p_id,
            "scrap_qty": done,
            "location_id": location_id,
            "scrap_location_id": scrap_location_id,
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
        creation = tec_stock_creation(odoo, objects, actions, p_id, dif)

        return creation


def tec_stock_creation(odoo, objects, actions, p_id, p_qty):
    uid, models, db, password = odoo
    partner_id = 206  # 206 Tecnosinergia
    picking_type_id = 303  # Ecommerce: Transferencias internas
    location_id = 3  # 3 Virtual Locations
    location_dest_id = 420  # 420 Tecnosinergia

    if p_qty == 0:
        return

    picking_order = {  # * Creacion de orden de inventario
        "partner_id": partner_id,
        "picking_type_id": picking_type_id,
        "move_type": "direct",
        # "immediate_transfer": True, Utilizado en odoo 16
        "priority": "1",
        "location_id": location_id,
        "location_dest_id": location_dest_id,
        "move_ids": [
            (
                0,
                0,
                {
                    "name": "Actual stock",
                    "location_id": location_id,
                    "location_dest_id": location_dest_id,
                    "product_id": p_id,
                    "product_uom": 1,
                    "product_uom_qty": p_qty,
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


def attribute_created(odoo, objects, actions, sku, data):
    uid, models, db, password = odoo
    attrs = data
    attributes = []
    lines = False

    product_data = models.execute_kw(
        db,
        uid,
        password,
        objects.get("product"),
        actions.get("s_read"),
        [[["default_code", "=", sku]]],
        {"fields": ["attribute_line_ids"]},
    )

    if product_data:
        lines = product_data[0].get("attribute_line_ids")

    # ? If not product lines, then do both
    if not lines:
        for attr in attrs:
            value = attrs.get(attr)

            if value == "":
                continue

            create = attribute_creation(odoo, objects, actions, attr, value)
            attributes.append(create)

        return attributes

    # ? Depends on how many lines, do one or more
    for line in lines:
        attribute_value_info = models.execute_kw(
            db,
            uid,
            password,
            objects.get("attribute_value"),
            actions.get("s_read"),
            [[["pav_attribute_line_ids", "=", line]]],
        )

        attribute_name = attribute_value_info[0].get("attribute_id")[1]

        if attrs.__contains__(attribute_name):
            attrs.pop(attribute_name)

    length = len(attrs)

    if length <= 0:
        return False

    for attr in attrs:
        value = attrs.get(attr)

        if value == "":
            continue

        create = attribute_creation(odoo, objects, actions, attr, value)

        attributes.append(create)

    return attributes


def attribute_creation(odoo, objects, actions, attribute, value):
    uid, models, db, password = odoo
    attr_id = False
    attr_value = False

    # ? Reading lines from products
    attribute_search = models.execute_kw(
        db,
        uid,
        password,
        objects.get("attribute"),
        actions.get("s_read"),
        [[["name", "=", attribute]]],
        {"fields": ["name"]},
    )

    attribute_id = attribute_search[0].get("id")

    # ? Reading attribute id from attribute value
    attribute_values = models.execute_kw(
        db,
        uid,
        password,
        objects.get("attribute_value"),
        actions.get("s_read"),
        [[["name", "=", value]]],
        {"fields": ["attribute_id"]},
    )

    # ? Matching all values on attributes to get the one
    for attribute_value in attribute_values:
        attr_id = attribute_value.get("attribute_id")[0]
        if attribute_id == attr_id:
            attr_value = attribute_value

    if attr_value:
        attr_id = attr_value.get("attribute_id")[0]

    # ? Matching original attribute id to value attribute id
    if attribute_id == attr_id:
        attribute_value_id = attr_value.get("id")
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


def tec_product_created(odoo, objects, actions, sku):
    uid, models, db, password = odoo
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


def tec_creation(odoo, data):
    print("Iniciando creación y/o actualización de productos - Tecnosinergia")
    uid, models, db, password = odoo
    total = 0
    success = 0
    errors = 0
    no_stock = (
        "Por el momento no contamos con este producto.\n¡Comunícate con nosotros!"
    )

    objects = {  # Modelos disponibles en Odoo
        "products": "product.product",
        "product": "product.template",
        "product_category": "product.public.category",
        "attribute": "product.attribute",
        "attribute_value": "product.attribute.value",
        "stock": "stock.quant",
        "intern": "stock.picking",
        "scrap": "stock.scrap",
        "unspsc": "product.unspsc.code",
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

    for record in data:
        if total == 2000:
            odoo = netdata.odoo_tec_dos()
            uid, models, db, password = odoo

        if total == 4000:
            odoo = netdata.odoo_tec_tres()
            uid, models, db, password = odoo

        if total == 6000:
            odoo = netdata.odoo_tec_cuatro()
            uid, models, db, password = odoo

        if total == 8000:
            odoo = netdata.odoo_tec_cinco()
            uid, models, db, password = odoo

        # * Variables
        published = True
        sku = record.get("sku")  # SKU
        stock_meri = record.get("stock_MER") | 0  # Stock de merida
        stock_qroo = record.get("stock_QRO") | 0  # Stock de qroo
        qty = stock_qroo + stock_meri  # Stock: merida||qroo
        name = html.unescape(record.get("name"))  # Nombre de producto
        clean_description = html.unescape(record.get("description"))
        specs = record.get("data_sheet")
        brand = html.unescape(record.get("brand"))  # Marca
        cap_brand = brand.capitalize()  # Marca
        category = html.unescape(record.get("line"))  # Categoria
        attrs = {"Marcas": cap_brand, "Categorías": category}  # Attributes

        # * Formateo de imagen
        final_image = tec_get_image(record)

        # * Formateo de textos
        description = tec_desc_format(clean_description)

        # * Verificación de existencia
        prod_created = tec_product_created(odoo, objects, actions, sku)
        prod_category = tec_cat_creation(odoo, objects, actions, record)

        # * Verificación de atributos
        attributes = attribute_created(odoo, objects, actions, sku, attrs)

        # * Elección de publicación
        if qty <= 0 or category == "Marketing" or name == "":
            published = False

        # * Plantilla de creación del producto
        product_template = {
            "is_published": published,
            "name": name.capitalize(),
            "default_code": record.get("sku"),
            "public_categ_ids": [(6, 0, [prod_category])],
            "sale_ok": True,
            "purchase_ok": True,
            "detailed_type": "product",  # Solo netdata
            "list_price": record.get("regular_price"),
            "standard_price": record.get("sale_price"),
            "description_purchase": "Producto Tecnosinergia",
            "description_sale": description,
            "description_picking": specs,
            "weight": record.get("weight"),
            "volume": record.get("volume"),
            "image_1920": final_image,  # Encode base64
            "allow_out_of_stock_order": False,
            "show_availability": True,
            "available_threshold": 50,
            "tracking": "none",
            "out_of_stock_message": no_stock,
            "attribute_line_ids": attributes,
            # "unspsc_code_id": record.get("sat_code"),
        }

        if prod_category == False:
            product_template.pop("public_categ_ids")

        if final_image == False:  # * Imagen producto
            product_template.pop("image_1920")

        if attributes == False or attributes == "":
            product_template.pop("attribute_line_ids")

        if prod_created[0]:
            prod_id = prod_created[1][0]

            try:  # ? Manejo de errores en la escritura
                models.execute_kw(
                    db,
                    uid,
                    password,
                    objects.get("products"),
                    actions.get("write"),
                    [[prod_id], product_template],
                )

            except Exception as e:
                errors += 1

                del e

            try:  # ? Manejo de errores en la actualizacion de stock
                tec_stock_created(odoo, objects, actions, prod_id, qty)

            except Exception as e:
                errors += 1
                total += 1

                del e

            success += 1
            total += 1

        # * Creación por inexistencia
        else:
            try:  # ? Manejo de errores en la creación
                create = models.execute_kw(
                    db,
                    uid,
                    password,
                    objects.get("product"),
                    actions.get("create"),
                    [product_template],
                )

            except Exception as e:
                errors += 1

                del e

            try:  # ? Manejo de errores en la creación de stock
                tec_stock_creation(odoo, objects, actions, create, qty)

            except Exception as e:
                errors += 1
                total += 1
                del e

            success += 1
            total += 1

        print(f"Exitos: {success} - Errores: {errors}", end="\r")
        time.sleep(1)

    print("Operación Tecnosinergia en NetDataSolutions exitosa")

    return success, errors


def tec_main(odoo):
    sinergy = tec.tech_catalogue()

    data = sinergy[1]
    creation = tec_creation(odoo, data)

    return creation
