from decouple import config
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
stock = models.execute_kw(
    db,
    uid,
    password,
    "stock.quant",
    "search_read",
    [[["location_id", "=", 336], ["product_id", "=", 80]]],
    {"fields": ["quantity"]},
)

if stock:
    qty = stock[0]["quantity"]
    typ = type(qty)

    print(f"Producto {qty} de tipo: {typ}")
else:
    print("No existe")

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

attribute_data = {
    "name": "Marca",
}

exist = True

if not exist:
    attribute_id = models.execute_kw(
        db,
        uid,
        password,
        "product.attribute",
        "create",
        [attribute_data],
    )

# Buscar el atributo por su nombre
attribute_name = "Marca"

attribute_ids = models.execute_kw(
    db,
    uid,
    password,
    "product.attribute",
    "search_read",
    [[["name", "=", attribute_name]]],
    {"fields": ["id"]},
)

# Buscar el valor del atributo por su nombre
attribute_value_name = "Tecnosinergia"

attribute_value_ids = models.execute_kw(
    db,
    uid,
    password,
    "product.attribute.value",
    "search_read",
    [[["name", "=", attribute_value_name]]],
    {"fields": ["id"]},
)

# Obtener el ID del valor del atributo
if attribute_value_ids:
    attribute_value_id = attribute_value_ids[0]["id"]
    print("ID del valor del atributo:", attribute_value_id)
else:
    print("Valor del atributo no encontrado")

# Obtener el ID del atributo
if attribute_ids:
    attribute_id = attribute_ids[0]["id"]
    print("ID del atributo:", attribute_id)

    product_data = {
        "attribute_line_ids": [
            (
                0,
                0,
                {
                    "attribute_id": attribute_id,
                    "value_ids": [
                        (0, 0, {"name": "Meriva", "attribute_id": attribute_id}),
                    ],
                },
            ),
        ],
    }

else:
    print("Atributo no encontrado")

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

fields = ["attribute_line_ids"]
product_data = models.execute_kw(
    db, uid, password, "product.product", "read", [85, fields], {}
)

attribute_line_ids = product_data[0].get("attribute_line_ids")
print(attribute_line_ids)
print(product_data)

if attribute_line_ids:
    print("Es un valor True")

if not attribute_line_ids:
    print("Es un valor False")
