from decouple import config
import odoo
import tech_sinergy
import requests
import html
import validators
import base64
import re

# db = config("odoo_test_db", default="")
db = config("odoo_db", default="")
odo = odoo.odoo_connect(db)

uid = odo[0]
models = odo[1]
password = odo[2]

tec = tech_sinergy.tech_api()

info = tec[0]
data = tec[1]


def get_image(record):
    image = record.get("image")

    url = validators.url(image)

    if not url:  # * Validación de la url
        return False

    get_image = requests.get(image)
    data_image = get_image.content
    binary_image = base64.b64encode(data_image)
    final_image = binary_image.decode("ascii")

    return final_image


def desc_format(text):
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


def cat_created(objects, actions, name):
    found = False
    find = models.execute_kw(
        db,
        uid,
        password,
        objects.get("product_category"),
        actions.get("search"),
        [[["name", "=", name]]],
    )

    if find:
        found = True

    return found, find


def cat_creation(objects, actions, record):
    name = html.unescape(record.get("category"))
    parent = html.unescape(record.get("parent_subcategory"))
    created = cat_created(objects, actions, name)

    cat_data = {
        "name": name,
        "parent_id": parent,
        "website_description": name,
    }

    if name == parent:
        cat_data.pop("parent_id")

    if created[0]:
        write = models.execute_kw(
            db,
            uid,
            password,
            objects.get("product_category"),
            actions.get("write"),
            [[created[1][0]], cat_data],
        )

        return created[1][0]

    create = models.execute_kw(
        db,
        uid,
        password,
        objects.get("product_category"),
        actions.get("create"),
        [cat_data],
    )

    return create


def stock_created(objects, actions, id, qty):
    find = models.execute_kw(
        db,
        uid,
        password,
        objects.get("stock"),
        actions.get("s_read"),
        [[["location_id", "=", 336], ["product_id", "=", id]]],
        {"fields": ["quantity"]},
    )

    if not find:
        creation = stock_creation(objects, actions, id, qty)
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
            "location_id": 336,  # Ecommerce
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
            "location_id": 351,  # 351 Tecnosinergia
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


def stock_creation(objects, actions, id, qty):
    if qty == 0:
        return

    picking_order = {  # * Creacion de orden de inventario
        "partner_id": 206,  # 10 Jorge # 206 Tecnosinergia
        "picking_type_id": 303,  # Ecommerce:interno Tipo recibo
        "move_type": "direct",
        "immediate_transfer": True,
        "priority": "1",
        "location_id": 351,  # 351 Tecnosinergia
        "location_dest_id": 336,  # 349 Ecommerce
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


def product_created(objects, actions, sku):
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


def produc_create():
    print("Iniciando creación y/o actualización de productos")
    products = 0
    errors = 0

    objects = {  # Modelos disponibles en Odoo
        "products": "product.product",
        "product_template": "product.template",
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

    for record in data:
        # * Variables
        published = True
        brand = html.unescape(record.get("brand")).upper()  # Marca
        category = html.unescape(record.get("category")).upper()  # Categoria
        attrs = {"Marca": brand, "Categoría": category}  # Attributes
        sku = record.get("sku")  # SKU
        stock_meri = record.get("stock_MER") | 0  # Stock de merida
        stock_qroo = record.get("stock_QRO") | 0  # Stock de qroo
        qty = stock_qroo + stock_meri  # Stock: merida||qroo
        name = html.unescape(record.get("name"))  # Nombre de producto
        clean_description = html.unescape(record.get("description"))

        # * Formateo de imagen
        final_image = get_image(record)

        # * Formateo de textos
        description = desc_format(clean_description)

        # * Verificación de existencia
        prod_created = product_created(objects, actions, sku)
        prod_category = cat_creation(objects, actions, record)

        # * Verificación de atributos
        attributes = attribute_created(objects, actions, sku, attrs)

        # * Elección de publicación
        if qty <= 0 or category == "Marketing":
            published = False

        # * Plantilla de creación del producto
        product_template = {
            "is_published": published,
            "name": name,
            "default_code": record.get("sku"),
            "public_categ_ids": [(6, 0, [prod_category])],
            "sale_ok": True,
            "purchase_ok": True,
            "detailed_type": "product",  # Solo netdata
            "list_price": record.get("regular_price"),
            "standard_price": record.get("sale_price"),
            "description_sale": description,
            "weight": record.get("weight"),
            "volume": record.get("volume"),
            "image_1920": final_image,  # Encode base64
            "allow_out_of_stock_order": False,
            "show_availability": True,
            "available_threshold": 50,
            "attribute_line_ids": attributes,
            # "unspsc_code_id": record.get("sat_code"),
        }

        if final_image == False:  # * Imagen producto
            product_template.pop("image_1920")

        if attributes == False:  # * Atributos producto
            product_template.pop("attribute_line_ids")

        if prod_created[0]:
            prod_id = prod_created[1][0]

            write = models.execute_kw(
                db,
                uid,
                password,
                objects.get("products"),
                actions.get("write"),
                [[prod_id], product_template],
            )

            products += 1

            stock = stock_created(objects, actions, prod_id, qty)

        # * Creación por inexistencia
        else:
            create = models.execute_kw(
                db,
                uid,
                password,
                objects.get("product_template"),
                actions.get("create"),
                [product_template],
            )

            try:
                stock = stock_creation(objects, actions, create, qty)
            except:
                errors += 1

            products += 1

        print(f"Exitos: {products} - Errores: {errors}", end="\r")

    print("Operación en NetDataSolutions exitosa")
