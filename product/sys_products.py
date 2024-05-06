import sysc
import requests
import validators
import base64
import datetime
import time

from bs4 import BeautifulSoup, Comment
from decouple import config
import odoo as netdata

NDS_DEF_SEARCH = config("NDS_DEF_SEARCH", default="")
LOCAL_DAY = datetime.date.today()


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

        if parent_of_parent == category_id or category_id == parent_id:
            cat_data.pop("parent_id")

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


def sys_get_image(product, has):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    }

    if has:
        return False, False

    h_img = True
    image = product.get("img_portada")

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


def sys_get_specs(url, has):
    if url == "" or has:
        return False, False

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
    }

    default_html = (
        "<div class='contenedor_nds'><p>Error en el contenedor del producto</p></div>"
    )
    nice = False
    description = False
    elmnts = []

    try:
        res = requests.get(url, headers=headers)
    except Exception as e:
        del e

        return default_html, description

    res_text = res.text

    content = BeautifulSoup(res_text, "html.parser")

    # ? Label elements
    info_comment = "Inicia información de producto"
    specs_comment = "Inicia especificaciones de producto"
    parent_class = "contenedor_nds"
    info_class = "info_nds"
    specs_class = "specs_nds"
    img_class = "imagen_nds"
    loading_img = "lazy"
    style_attr = "style"
    class_attr = "class"
    a_attr = "href"

    # ? New html labels
    parent_div = content.new_tag("div", attrs={"class": parent_class})
    info_div = content.new_tag("div", attrs={"class": info_class})
    specs_div = content.new_tag("div", attrs={"class": specs_class})

    # ? Html actions
    style_labels = content.find_all("style")
    div_content = content.find("div", {"class": "container"})

    if not div_content:
        return default_html, description

    comment_specs = div_content.find(
        string=lambda text: isinstance(text, Comment) and specs_comment in text
    )

    comment_info = div_content.find(
        string=lambda text: isinstance(text, Comment) and info_comment in text
    )

    # ? Info box
    prod_info = comment_info.find_next("div")
    info_div.append(prod_info)
    elmnts.append(info_div)

    # ? Espec box
    prod_specs = comment_specs.find_next("div")
    specs_div.append(prod_specs)
    elmnts.append(specs_div)

    # ? Insert style labels
    for style in style_labels:
        parent_div.append(style)

    for elmnt in elmnts:
        iframe_content = elmnt.find_all("iframe")
        img_content = elmnt.find_all("img")
        a_content = elmnt.find_all("a")

        for iframe in iframe_content:
            new_div = content.new_tag("div", attrs={"class": "multimedia"})

            iframe.insert_after(new_div)
            new_div.append(iframe)

        # ? Only exec on info box
        if elmnts.index(elmnt) == 0:
            cols_content = elmnt.find_all("div", attrs={"class": "col-md-4"})

            for cols in cols_content:
                info_img = content.new_tag("div", attrs={"class": "media"})
                cols_img = cols.find_all("img")

                for img in cols_img:
                    lenght = len(cols_img)

                    if img.attrs.__contains__(class_attr):
                        img_class = img.attrs.get(class_attr)
                        if img_class == ["img-responsive", "img-thumbnail"]:
                            thumb_img = content.new_tag("div", attrs={"class": "media"})
                            img.insert_after(thumb_img)
                            thumb_img.append(img)

                    else:
                        # ? Only exec on last item
                        if lenght == (cols_img.index(img) + 1):
                            img.insert_after(info_img)

                        info_img.append(img)

        # ? Only exec on spec box
        if elmnts.index(elmnt) != 0:
            for img in img_content:
                img["class"] = img_class
                img["loading"] = loading_img

                specs_img = content.new_tag("div", attrs={"class": "media"})

                if img.attrs.__contains__(style_attr):
                    style = img.attrs.get(style_attr)
                    if style == "float: right;":
                        del img[style_attr]

                img.insert_after(specs_img)
                specs_img.append(img)

        for a in a_content:
            if a.attrs.__contains__(a_attr):
                text = a.get_text()

                if a[a_attr].startswith("https://www.syscom"):
                    a[a_attr] = NDS_DEF_SEARCH.format(text)

        parent_div.append(elmnt)

    nice = parent_div.prettify()
    description = True

    return nice, description


def sys_stock(product):
    total_stock = product.get("total_existencia")
    stock = 0

    if total_stock <= 0:
        return stock

    stock = product.get("existencia")
    new_stock = 0

    try:
        if stock.__contains__("nuevo"):
            new_stock = stock.get("nuevo")

    except Exception as e:
        del e

    if stock == None:
        new_stock = total_stock

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
        p_price = find[0].get("standard_price")
        p_qty = find[0].get("qty_available")
        p_img = find[0].get("x_has_image")
        p_desc = find[0].get("x_has_description")

        prod_info = {
            "id": p_id,
            "cost": p_price,
            "qty": p_qty,
            "img": p_img,
            "desc": p_desc,
        }

    return found, prod_info


def sys_creation(odoo, catalogue, exchange):
    print("Iniciando creación y/o actualización de productos - SYSCOM\n")
    uid, models, db, password = odoo
    total = 0
    success = 0
    errors = 0
    no_stock = "Producto disponible bajo pedido.\nPor favor póngase en contacto con nosotros para solicitar una cotización personalizada."

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

        qty = sys_stock(product)
        conversion = float(exchange)
        sku = product.get("modelo")
        precios = product.get("precios")

        if precios:  # * Precio en dolares por conversión
            costo = float(precios.get("precio_descuento"))
            precio = costo + ((costo * 15) / 100)

        if not precios:
            costo = 0
            precio = 0

        costo *= conversion
        precio *= conversion

        product_created = sys_created(odoo, objects, actions, sku)

        prod_id = product_created[1].get("id")
        cost = product_created[1].get("cost")
        p_qty = product_created[1].get("qty")
        has_img = product_created[1].get("img")
        has_desc = product_created[1].get("desc")

        if costo == cost and qty == p_qty and has_img and has_desc:
            total += 1

            continue

        published = True
        name = product.get("titulo")
        specs_link = product.get("link_privado")
        specs = sys_get_specs(specs_link, has_desc)
        code_id = unspsc_verification(odoo, objects, actions, product)
        brand = product.get("marca")
        cap_brand = brand.capitalize()
        category = ""
        subcategory = ""
        categories = product.get("categorias")

        for categorie in categories:
            level = categorie.get("nivel")

            if level == 1:
                category = categorie.get("nombre")

            if level == 2:
                subcategory = categorie.get("nombre")

        prod_categ = {"categoria": category, "subcategoria": subcategory}
        attrs = {"Marcas": cap_brand, "Categorías": category}

        final_image = sys_get_image(product, has_img)

        if qty <= 0 or precio <= 0 or name == "":
            published = False

        prod_category = cat_creation(odoo, objects, actions, prod_categ)
        attributes = attribute_created(odoo, objects, actions, sku, attrs)

        product_template = {
            "is_published": published,
            "name": name,
            "default_code": sku,
            "public_categ_ids": [(6, 0, [prod_category])],
            "sale_ok": True,
            "purchase_ok": True,
            "detailed_type": "product",  # Solo netdata
            "list_price": precio,
            "standard_price": costo,
            "description_purchase": "Producto Syscom",
            "description_sale": f"Producto: {name} \n\nMarca: {brand} \n",
            "description_picking": specs_link,
            "description_pickingin": specs[0],
            # "weight": product.get("peso"),
            # "volume": record.get("volume"),
            "image_1920": final_image[0],  # Encode base64
            "allow_out_of_stock_order": False,
            "show_availability": True,
            "available_threshold": 20,
            "tracking": "none",
            "out_of_stock_message": no_stock,
            "attribute_line_ids": attributes,
            "unspsc_code_id": code_id,
            "x_has_image": final_image[1],
            "x_has_description": specs[1],
        }

        if prod_category == False:
            product_template.pop("public_categ_ids")

        if code_id == False:
            product_template.pop("unspsc_code_id")

        if attributes == False or attributes == "":
            product_template.pop("attribute_line_ids")

        if final_image[0] == False:
            product_template.pop("image_1920")

        if specs[0] == False:
            product_template.pop("description_picking")
            product_template.pop("description_pickingin")

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
    exchange = sysc.sys_exchange()
    catalogue = sysc.sys_catalogue()
    creation = sys_creation(odoo, catalogue, exchange)

    return creation
