import ct
import requests
import validators
import base64
import time

from decouple import config
import odoo as netdata


def unspsc_verification(odoo, objects, actions, product):
    uid, models, db, password = odoo
    code = product.get("sat_key")
    sat_id = "01010101"

    unspsc = models.execute_kw(
        db,
        uid,
        password,
        objects.get("unspsc"),
        actions.get("s_read"),
        [[["code", "=", code]]],
        {"fields": ["code", "name"]},
    )

    if not unspsc:
        return sat_id

    sat_id = unspsc[0].get("id")

    return sat_id


def cat_created(odoo, objects, actions, name):
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


def cat_creation(odoo, objects, actions, record):
    uid, models, db, password = odoo
    parent_of_parent = ""
    parent = record.get("categoria")
    parent_created = cat_created(odoo, objects, actions, parent)
    parent_id = False
    category = record.get("subcategoria")
    category_created = cat_created(odoo, objects, actions, category)

    if parent_created[0]:
        parent_id = parent_created[1][0].get("id")
        parent_of_parent = parent_created[1][0].get("parent_id")

        if parent_of_parent:
            parent_of_parent = parent_created[1][0].get("parent_id")[0]

    cat_data = {
        "name": category,
        "parent_id": parent_id,
        "website_description": category,
    }

    if not parent_id:
        cat_data.pop("parent_id")

    if category_created[0]:
        category_id = category_created[1][0].get("id")

        try:
            models.execute_kw(
                db,
                uid,
                password,
                objects.get("product_category"),
                actions.get("write"),
                [[category_id], cat_data],
            )

        except Exception as e:

            del e

        return category_id

    if category == "" and parent != "":
        category = parent

    elif parent == "":
        return False

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
        if cat_data.__contains__("parent_id"):
            cat_data.pop("parent_id")

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


def ct_get_image(product, has):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    }

    if has:
        return False, False

    h_img = True
    image = product.get("imagen")

    url = validators.url(image)

    if not url:  # * Validación de la url
        image = config("NDS_DEF_IMG", default="")
        h_img = False

    try:
        get_image = requests.get(image, headers=headers)
    except Exception as e:
        del e
        return False, False

    data_image = get_image.content
    binary_image = base64.b64encode(data_image)
    final_image = binary_image.decode("ascii")

    return final_image, h_img


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
    precio = product.get("precio")

    if promociones:
        costo = promociones[0].get("promocion")
        precio = costo + ((costo * 15) / 100)

    # * En caso de no existir costo, aplicar 20% costo más impuestos
    if not promociones:
        costo = precio
        precio = costo + ((costo * 15) / 100)

    # * Conversión de moneda de cambio
    if moneda == "USD":
        costo *= cambio
        precio *= cambio

    return costo, precio


def ct_specs(product):
    all_specs = ""
    specs = product.get("especificaciones")

    if specs == [] or specs == None:
        return all_specs

    for spec in specs:
        variety = spec.get("tipo")
        value = spec.get("valor")

        info = f"{variety}: {value} \n"
        all_specs += info

    return all_specs


def ct_stock_created(odoo, objects, actions, id, qty):
    uid, models, db, password = odoo
    location_id = 418  # CT
    scrap_location_id = 352  # Ecommerce Scrap

    find = models.execute_kw(
        db,
        uid,
        password,
        objects.get("stock"),
        actions.get("s_read"),
        [[["location_id", "=", location_id], ["product_id", "=", id]]],
        {"fields": ["quantity"]},
    )

    if not find:
        creation = ct_stock_creation(odoo, objects, actions, id, qty)
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
        creation = ct_stock_creation(odoo, objects, actions, id, dif)

        return creation


def ct_stock_creation(odoo, objects, actions, id, qty):
    uid, models, db, password = odoo
    partner_id = 887  # 887 CT
    picking_type_id = 303  # Ecommerce: Transferencias internas
    location_id = 3  # 3 Virtual Locations
    location_dest_id = 418  # 418 CT

    if qty == 0:
        return

    picking_order = {  # * Creacion de orden de inventario
        "partner_id": partner_id,
        "picking_type_id": picking_type_id,
        "move_type": "direct",
        "immediate_transfer": True,
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


def ct_created(odoo, objects, actions, sku):
    uid, models, db, password = odoo
    prod_info = {}
    found = False
    find = models.execute_kw(
        db,
        uid,
        password,
        objects.get("products"),
        actions.get("s_read"),
        [[["default_code", "=", sku]]],
    )

    if find:
        found = True

        p_id = find[0].get("id")
        p_qty = find[0].get("qty_available")
        p_img = find[0].get("x_has_image")
        p_desc = find[0].get("x_has_description")

        prod_info = {
            "id": p_id,
            "qty": p_qty,
            "img": p_img,
            "desc": p_desc,
        }

    return found, prod_info


def ct_creation(odoo, catalogue):
    print("Iniciando creación y/o actualización de productos - CT")
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

    for product in catalogue:
        if total == 2000:
            odoo = netdata.odoo_ct_dos()
            uid, models, db, password = odoo

        if total == 4000:
            odoo = netdata.odoo_ct_tres()
            uid, models, db, password = odoo

        if total == 6000:
            odoo = netdata.odoo_ct_cuatro()
            uid, models, db, password = odoo

        if total == 8000:
            odoo = netdata.odoo_ct_cinco()
            uid, models, db, password = odoo

        qty = ct_stock(product)
        sku = product.get("clave")
        product_created = ct_created(odoo, objects, actions, sku)

        prod_id = product_created[1].get("id")
        p_qty = product_created[1].get("qty")
        has_img = product_created[1].get("img")

        if qty == p_qty and has_img:
            total += 1

            continue

        published = True
        name = product.get("nombre")
        desc = product.get("descripcion_corta")
        final_image = ct_get_image(product, has_img)
        prices = ct_price(product)
        specs = ct_specs(product)
        worth = prices[0]
        price = prices[1]
        brand = product.get("marca")
        cap_brand = brand.capitalize()
        category = product.get("categoria")
        prod_category = cat_creation(odoo, objects, actions, product)
        attrs = {"Marcas": cap_brand, "Categorías": category}
        attributes = attribute_created(odoo, objects, actions, sku, attrs)

        if qty <= 0 or name == "":
            published = False

        product_template = {
            "is_published": published,
            "name": name,
            "default_code": sku,
            "public_categ_ids": [(6, 0, [prod_category])],  # Creación de categorias
            "sale_ok": True,
            "purchase_ok": True,
            "detailed_type": "product",  # Solo netdata
            "list_price": price,
            "standard_price": worth,
            "description_purchase": "Producto CT",
            "description_sale": f"{desc} \n\n{specs}",
            # "weight": record.get("weight"),
            # "volume": record.get("volume"),
            "image_1920": final_image[0],
            "allow_out_of_stock_order": False,
            "show_availability": True,
            "available_threshold": 20,
            "tracking": "none",
            "out_of_stock_message": no_stock,
            "attribute_line_ids": attributes,  # Creación de atributos
            # "unspsc_code_id": record.get("sat_code"), # Envio de codigo sat
            "x_has_image": final_image[1],
            # "x_has_description": specs[1],
        }

        if prod_category == False:
            product_template.pop("public_categ_ids")

        if final_image[0] == False:
            product_template.pop("image_1920")

        if attributes == False or attributes == "":
            product_template.pop("attribute_line_ids")

        if product_created[0]:

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
                ct_stock_created(odoo, objects, actions, prod_id, qty)

            except Exception as e:
                errors += 1
                total += 1

                del e

            success += 1
            total += 1

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
                ct_stock_creation(odoo, objects, actions, create, qty)

            except Exception as e:
                errors += 1
                total += 1

                del e

            success += 1
            total += 1

        print(f"Exitos: {success} - Errores: {errors}", end="\r")
        time.sleep(1)

    print("Operación CT en NetDataSolutions exitosa")

    return success, errors


def ct_main(odoo):
    catalogue = ct.ct_catalogue()
    creation = ct_creation(odoo, catalogue)

    return creation
