import sysc
import requests
import validators
import base64
import datetime
import time

from bs4 import BeautifulSoup
from decouple import config
import odoo as netdata

NDS_DEF_SEARCH = config("NDS_DEF_SEARCH", default="")
LOCAL_DAY = datetime.date.today()
exchange = sysc.sys_exchange()
catalogue = sysc.sys_catalogue()


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


def unspsc_verification(odoo, objects, actions, product):
    uid, models, db, password = odoo
    code = product.get("sat_key")
    sat_id = "1"

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


def sys_get_image(product):
    image = product.get("img_portada")

    url = validators.url(image)

    if not url:  # * Validación de la url
        image = config("NDS_DEF_IMG", default="")

    try:
        get_image = requests.get(image)
    except Exception as e:
        del e
        return False

    data_image = get_image.content
    binary_image = base64.b64encode(data_image)
    final_image = binary_image.decode("ascii")

    return final_image


def sys_get_specs(url):
    if url == "":
        return False

    res = requests.get(url)

    content = res.text

    soup = BeautifulSoup(content, "html.parser")

    style_labels = soup.find_all("style")
    contenido_div = soup.find("div", {"class": "container"})
    contenido_iframe = contenido_div.find_all("iframe")
    contenido_img = contenido_div.find_all("img")
    contenido_a = contenido_div.find_all("a")
    style_attr = "style"
    a_attr = "href"

    for style in style_labels:
        contenido_div.insert_before(style)

    for iframe in contenido_iframe:
        new_div = soup.new_tag("div", attrs={"class": "multimedia"})

        iframe.insert_after(new_div)
        new_div.append(iframe)

    for img in contenido_img:
        img["class"] = "imagen_nds"
        new_div = soup.new_tag("div", attrs={"class": "media"})

        if img.attrs.__contains__(style_attr):
            style = img.attrs.get(style_attr)
            if style == "float: right;":
                del img[style_attr]

        img.insert_after(new_div)
        new_div.append(img)

    for a in contenido_a:
        if a.attrs.__contains__(a_attr):
            text = a.get_text()

            if a[a_attr].startswith("https://www.syscom"):
                # print()
                a[a_attr] = NDS_DEF_SEARCH.format(text)

    # ? Agregar una clase extra al contenedor principal
    deseado = "contenedor_nds"
    contenido_div["class"] = deseado

    nice = contenido_div.prettify()

    return nice


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


def sys_stock_created(odoo, objects, actions, id, qty):
    uid, models, db, password = odoo
    location_id = 419  # Syscom
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
        creation = sys_stock_creation(odoo, objects, actions, id, qty)
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
            # "lot_id": f"{id} - {LOCAL_DAY}", # Lot id
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
        creation = sys_stock_creation(odoo, objects, actions, id, dif)

        return creation


def sys_stock_creation(odoo, objects, actions, id, qty):
    uid, models, db, password = odoo
    partner_id = 908  # 908 Syscom
    picking_type_id = 303  # Ecommerce: Transferencias internas
    location_id = 3  # 3 Virtual Locations
    location_dest_id = 419  # 419 Syscom

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


def sys_created(odoo, objects, actions, sku):
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


def sys_creation(odoo):
    print("Iniciando creación y/o actualización de productos - SYSCOM\n")
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
            odoo = netdata.odoo_sys_dos()
            uid, models, db, password = odoo

        if total == 4000:
            odoo = netdata.odoo_sys_tres()
            uid, models, db, password = odoo

        if total == 6000:
            odoo = netdata.odoo_sys_cuatro()
            uid, models, db, password = odoo

        if total == 8000:
            odoo = netdata.odoo_sys_cinco()
            uid, models, db, password = odoo

        if total == 10000:
            odoo = netdata.odoo_sys_seis()
            uid, models, db, password = odoo

        if total == 12000:
            odoo = netdata.odoo_sys_siete()
            uid, models, db, password = odoo

        if total == 14000:
            odoo = netdata.odoo_sys_ocho()
            uid, models, db, password = odoo

        if total == 16000:
            odoo = netdata.odoo_sys_nueve()
            uid, models, db, password = odoo

        if total == 18000:
            odoo = netdata.odoo_sys_diez()
            uid, models, db, password = odoo

        if total == 20000:
            odoo = netdata.odoo_sys_once()
            uid, models, db, password = odoo

        if total == 22000:
            odoo = netdata.odoo_sys_doce()
            uid, models, db, password = odoo

        if total == 24000:
            odoo = netdata.odoo_sys_trece()
            uid, models, db, password = odoo

        if total == 26000:
            odoo = netdata.odoo_sys_catorce()
            uid, models, db, password = odoo

        if total == 28000:
            odoo = netdata.odoo_sys_quince()
            uid, models, db, password = odoo

        if total == 30000:
            odoo = netdata.odoo_sys_dieciseis()
            uid, models, db, password = odoo

        if total == 32000:
            odoo = netdata.odoo_sys_diecisiete()
            uid, models, db, password = odoo

        if total == 34000:
            odoo = netdata.odoo_sys_dieciocho()
            uid, models, db, password = odoo

        if total == 36000:
            odoo = netdata.odoo_sys_diecinueve()
            uid, models, db, password = odoo

        if total == 38000:
            odoo = netdata.odoo_sys_veinte()
            uid, models, db, password = odoo

        if total == 40000:
            odoo = netdata.odoo_sys_veintiuno()
            uid, models, db, password = odoo

        if total == 42000:
            odoo = netdata.odoo_sys_veintidos()
            uid, models, db, password = odoo

        if total == 44000:
            odoo = netdata.odoo_sys_veintitres()
            uid, models, db, password = odoo

        published = True
        name = product.get("titulo")
        sku = product.get("modelo")
        precios = product.get("precios")
        specs_link = product.get("link_privado")
        specs = sys_get_specs(specs_link)
        conversion = float(exchange)
        qty = sys_stock(product)
        product_created = sys_created(odoo, objects, actions, sku)
        code_id = unspsc_verification(odoo, objects, actions, product)
        brand = product.get("marca")
        cap_brand = brand.capitalize()
        categories = product.get("categorias")

        for categorie in categories:
            level = categorie.get("nivel")

            if level == 1:
                category = categorie.get("nombre")

        attrs = {"Marcas": cap_brand, "Categorías": category}

        if precios:  # * Precio en dolares por conversión
            costo = float(precios.get("precio_descuento"))
            precio = float(precios.get("precio_lista"))

        if not precios:
            costo = 0
            precio = 0

        costo *= conversion
        precio *= conversion
        final_image = sys_get_image(product)

        if qty <= 0 or precio <= 0 or name == "":
            published = False

        if specs == False:
            specs = ""

        attributes = attribute_created(odoo, objects, actions, sku, attrs)

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
            "description_sale": f"Producto: {name} \n\nMarca: {brand} \n",
            "description_picking": specs_link,
            "description_pickingin": specs,
            # "weight": product.get("peso"),
            # "volume": record.get("volume"),
            "image_1920": final_image,  # Encode base64
            "allow_out_of_stock_order": False,
            "show_availability": True,
            "available_threshold": 20,
            "tracking": "none",
            "out_of_stock_message": no_stock,
            "attribute_line_ids": attributes,
            "unspsc_code_id": code_id,
        }

        if code_id == False:
            product_template.pop("unspsc_code_id")

        if attributes == False or attributes == "":
            product_template.pop("attribute_line_ids")

        if final_image == False:
            product_template.pop("image_1920")

        if product_created[0]:
            prod_id = product_created[1][0]

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
                sys_stock_created(odoo, objects, actions, prod_id, qty)

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
                sys_stock_creation(odoo, objects, actions, create, qty)

            except Exception as e:
                errors += 1
                total += 1

                del e

            success += 1
            total += 1
        print(f"Exitos: {success} - Errores: {errors}", end="\r")
        time.sleep(1)

    print("Operación Syscom en NetDataSolutions exitosa")

    return success, errors


def sys_main(odoo):
    creation = sys_creation(odoo)

    return creation
