from decouple import config
from ftplib import FTP
import requests
import validators
import base64
import odoo
import json

# db = config("odoo_test_db", default="")
db = config("odoo_db", default="")
odo = odoo.odoo_connect(db)

uid = odo[0]
models = odo[1]
password = odo[2]

objects = {
    "test": "x_mayoristas",
    "product": "product.template",
    "entry": "stock.move",
    "intern": "stock.picking",
    "scrap": "stock.scrap",
}

actions = {
    "search": "search",
    "read": "read",
    "create": "create",
    "write": "write",
    "confirm": "action_confirm",
    "validate": "action_validate",
    "button": "button_validate",
}


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


def ct_creation(objects, actions, producto):
    published = True

    promociones = producto.get("promociones")
    moneda = producto.get("moneda")
    cambio = producto.get("tipoCambio")

    if promociones:
        costo = promociones[0].get("promocion")
    precio = producto.get("precio")

    # * En caso de no existir costo, aplicar 10% costo más impuestos
    if not promociones:
        costo = precio
        precio = costo + ((costo * 10) / 100)

    # * Conversión de moneda de cambio
    if moneda == "USD":
        costo *= cambio
        precio *= cambio

    final_image = ct_get_image(producto)

    product_template = {
        "is_published": published,
        "name": producto.get("nombre"),
        "default_code": producto.get("clave"),
        # "public_categ_ids": [(6, 0, [prod_category])],
        "sale_ok": True,
        "purchase_ok": True,
        "detailed_type": "product",  # Solo netdata
        "list_price": precio,
        "standard_price": costo,
        "cost_currency_id": producto.get("moneda"),
        "description_purchase": "Producto CT",
        "description_sale": producto.get("descripcion_corta"),
        # "weight": record.get("weight"),
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

    prod_creation = models.execute_kw(
        db,
        uid,
        password,
        objects.get("product"),
        actions.get("create"),
        [product_template],
    )

    return prod_creation


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


def sys_creation(objects, actions, producto):
    published = True

    precios = producto.get("precios")

    if precios:
        costo = precios.get("precio_descuento")
        precio = precios.get("precio_lista")

    if not precios:
        costo = 0
        precio = 0

    final_image = sys_get_image(producto)

    product_template = {
        "is_published": published,
        "name": producto.get("titulo"),
        "default_code": producto.get("modelo"),
        # "public_categ_ids": [(6, 0, [prod_category])],
        "sale_ok": True,
        "purchase_ok": True,
        "detailed_type": "product",  # Solo netdata
        "list_price": precio,
        "standard_price": costo,
        "description_purchase": "Producto Syscom",
        "description_sale": f"Producto: {producto.get('titulo')} \nMarca: {producto.get('marca')}",
        "weight": producto.get("peso"),
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

    prod_creation = models.execute_kw(
        db,
        uid,
        password,
        objects.get("product"),
        actions.get("create"),
        [product_template],
    )

    return prod_creation


# ? Obtención de productos CT

ftp_host = config("ct_host", default="")
ftp_user = config("ct_user", default="")
ftp_password = config("ct_pass", default="")
ftp_directory = config("ct_dir", default="")
json_file_name = config("ct_file", default="")

# ? Creamos una instancia FTP
ftp = FTP(ftp_host)

# ? Iniciando sesión en el servidor ftp
ftp.login(ftp_user, ftp_password)

# ? Moviendonos al directorio deseado
ftp.cwd(ftp_directory)

# ? Descarga del archivo JSON
with open(json_file_name, "wb") as local_file:
    ftp.retrbinary("RETR " + json_file_name, local_file.write)

# ? Cerrando la conexion FTP
ftp.quit()

# ? Carga y trabaja con el archivo JSON localmente
with open(json_file_name, "r") as local_file:
    productos = json.load(local_file)

limite = 1

print("\n\n\n")

print("Obtención de productos de CT \n")

# ? Verificar el contenido de los productos
for producto in productos:
    # ? Crear producto en base a su clave
    if producto.get("clave") == "DDUKGT2210":
        print("Producto ya creado")
        # creation = ct_creation(objects, actions, producto)
        # print(f"Producto {creation} creado de: \n\n {json.dumps(producto)}")

print("\nFin de obtención de productos de CT")

# ? Fin obtención de productos CT

print("\n\n\n")

# ? Obtención de productos Syscom

sys_url = config("sys_url", default="")

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {}".format(config("sys_token", default="")),
}

redirects = {
    "test": "/status",  # Prueba token
    "products": "/item/list",  # Lista de productos
    "product": "/item/list?item_id=",  # Producto especifico
    "addresses": "/address/list",  # Lista de direcciones
    "marcas": "/marcas",  # * Todas las marcas
    "marca_prods": "/marcas/{}/productos",  # * Todos los productos de una marca
    "categorias": "/order/create",  # * Todas las categorias
}

req_adata = requests.get(
    sys_url + redirects.get("marca_prods").format("apple"), headers=headers
)

productos_adata = req_adata.json()

prods = productos_adata.get("productos")

limite = 1

print("Obtención de productos de Syscom \n")

# ? Verificar el contenido de los productos
for prod in prods:
    while limite > 0:
        creation = sys_creation(objects, actions, prod)
        print(f"Producto {creation} creado de: \n\n {json.dumps(prod)}")
        limite -= 1

print("\nFin de obtención de productos de Syscom \n")

# ? Fin obtención de productos Syscom

crear = "False"

if crear == True:
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
                    "product_id": 85,
                    "product_uom": 1,
                    # "product_uom_qty": 5,
                    "quantity_done": 5,
                },
            )
        ],
    }

    # * Creation
    # picking_creation = models.execute_kw(
    #     db,
    #     uid,
    #     password,
    #     objects.get("intern"),
    #     actions.get("create"),
    #     [picking_order],
    # )

    # picking_confirmation = models.execute_kw(
    #     db,
    #     uid,
    #     password,
    #     objects.get("intern"),
    #     actions.get("button"),
    #     [picking_creation],
    # )

if crear == False:
    existing_order = {  # * Creacion de orden de desecho
        "product_id": 85,
        "scrap_qty": 5,
        "location_id": 336,  # Ecommerce
        "scrap_location_id": 352,  # Ecommerce Scrap
    }

    # * Orden de desecho
    # exist_creation = models.execute_kw(
    #     db,
    #     uid,
    #     password,
    #     objects.get("scrap"),
    #     actions.get("create"),
    #     [existing_order],
    # )

    # * Validación
    # exist_confirmation = models.execute_kw(
    #     db,
    #     uid,
    #     password,
    #     objects.get("scrap"),
    #     actions.get("validate"),
    #     [exist_creation],
    #     {},
    # )

# Encontrar un producto por ID en nuestro almacen Ecommerce y obtener la cantidad
# stock = models.execute_kw(
#     db,
#     uid,
#     password,
#     "stock.quant",
#     "search_read",
#     [[["location_id", "=", 336], ["product_id", "=", 80]]],
#     {"fields": ["quantity"]},
# )

# if stock:
#     qty = stock[0]["quantity"]
#     typ = type(qty)

#     print(f"Producto {qty} de tipo: {typ}")
# else:
#     print("No existe")

product_template = {
    "is_published": "published",
    "name": "name",
    "x_name": "title",
    "default_code": 1,
    "public_categ_ids": "[(6, 0, [prod_category])]",
    "sale_ok": True,
    "purchase_ok": True,
    "detailed_type": "product",  # Solo netdata
    "list_price": 1,
    "standard_price": 12,
    "description_sale": "description",
    "weight": 3,
    "volume": 2,
    "image_1920": "21212",
    "allow_out_of_stock_order": False,
    "show_availability": True,
}

# print(json.dumps(product_template))

# product_template.pop("image_1920")

# print(json.dumps(product_template))

# attribute_data = {
#     "name": "Marca",
# }

# exist = True

# if not exist:
#     attribute_id = models.execute_kw(
#         db,
#         uid,
#         password,
#         "product.attribute",
#         "create",
#         [attribute_data],
#     )

# Buscar el atributo por su nombre
# attribute_name = "Marca"

# attribute_ids = models.execute_kw(
#     db,
#     uid,
#     password,
#     "product.attribute",
#     "search_read",
#     [[["name", "=", attribute_name]]],
#     {"fields": ["id"]},
# )

# * ****************************
# ? Obteniendo atributos de un producto mediante su 'default_code'

# sku = "MFC4002KIT"

# product_data = models.execute_kw(
#     db,
#     uid,
#     password,
#     "product.template",
#     "search_read",
#     [[["default_code", "=", sku]]],
#     {"fields": ["attribute_line_ids"]},
# )

# attribute_pavs = product_data[0].get("attribute_line_ids")
# attributes = []

# for attribute in attribute_pavs:
#     attributes.append(attribute)

# print(attributes)

# * ****************************

# attribute_id = product_data[0].get("attribute_line_ids")
# name = product_data[0].get("name")

# print(attribute_id)
# print(name)
print("------------------")

# Buscar el valor del atributo por su nombre
attribute_name = "Marca"

attribute_name_info = models.execute_kw(
    db,
    uid,
    password,
    "product.attribute",
    "search_read",
    [[["name", "=", attribute_name]]],
    {"fields": ["id"]},
)

# Obtener el ID del valor del atributo
if attribute_name_info:
    attribute_value_id = attribute_name_info[0]["id"]
    # print(f"Value id: {attribute_name_info}")
    # print("ID del valor del atributo:", attribute_value_id)
else:
    print("Valor del atributo no encontrado")

attribute_value = "BELDEN"
the_attribute_id = 12
attribute_pav = 12  # attribute_id[0]

# ? Encontrando un atributo con un ID relacionado a un producto
attribute_value_info = models.execute_kw(
    db,
    uid,
    password,
    "product.attribute.value",
    "search_read",
    [[["pav_attribute_line_ids", "=", attribute_pav]]],
    {"fields": ["name"]},
)

print("------------")
# print(attribute_pav)
# print(attribute_value_info)
# category = attribute_value_info[0].get("attribute_id")
# print(category)
print("------------")

attr1 = "Tecnosinergia"
attr2 = "Pantallas"

attrs = {"Marca": attr1, "Categoria": attr2}

# print(attrs.get("Categoria"))

# attrs.pop(attr1)

attribute_id = attribute_name_info[0].get("id")

# print(attribute_id)

product_attributes = []

attribute_creation = (
    0,
    0,
    {
        "attribute_id": attribute_id,
        "value_ids": [(4, "value")],
    },
)

attribute_creation2 = (
    0,
    0,
    {
        "attribute_id": attribute_id,
        "value_ids": [(4, "value")],
    },
)

product_attributes.append(attribute_creation)
product_attributes.append(attribute_creation2)

# print(product_attributes)

# print(attrs.get("Categoria"))

# category_attribute = models.execute_kw(
#     db,
#     uid,
#     password,
#     "product.attribute.value",
#     "create",
#     [
#         {
#             "attribute_id": category[0],
#             "name": "Prueba",
#         }
#     ],
# )

# Obtener el ID del atributo
# if attribute_ids:
#     attribute_id = attribute_ids[0]["id"]
#     print("ID del atributo:", attribute_id)

#     product_data = {
#         "attribute_line_ids": [
#             (
#                 0,
#                 0,
#                 {
#                     "attribute_id": attribute_id,
#                     "value_ids": [
#                         (0, 0, {"name": "Meriva", "attribute_id": attribute_id}),
#                     ],
#                 },
#             ),
#         ],
#     }

# else:
#     print("Atributo no encontrado")

# * Asignar valor por ID
# product_data = {
#     "attribute_line_ids": [
#         (
#             0,
#             0,
#             {
#                 "attribute_id": attribute_id,
#                 "value_ids": [(4, attribute_value_id)],
#             },
#         ),
#     ],
# }

# result = models.execute_kw(
#     db,
#     uid,
#     password,
#     "product.product",
#     "write",
#     [[85], product_data],
# )

# fields = ["attribute_line_ids"]
# product_data = models.execute_kw(
#     db, uid, password, "product.product", "read", [85, fields], {}
# )

# attribute_line_ids = product_data[0].get("attribute_line_ids")
# print(attribute_line_ids)
# print(product_data)

# if attribute_line_ids:
#     print("Es un valor True")

# if not attribute_line_ids:
#     print("Es un valor False")
