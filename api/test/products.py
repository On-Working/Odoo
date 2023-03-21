import xmlrpc.client
import json
import base64

# API keys
test = 'd2fe38692b1c10ce22ba64c9be4da48ca283aaec'
ecommerce = 'b046782b53d4b31eb0c3f901ec20a659ea0be1f3'

# Base de datos
url = 'https://nd-test.odoo.com/'
db = 'nd-test'

# Usuario
username= 'jmartinez@netdata.com.mx'
password = 'd2fe38692b1c10ce22ba64c9be4da48ca283aaec'

# Creando la conexión proxy con el cliente Odoo
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
# Iniciando sesión en la base de datos
uid = common.authenticate(db, username, password, {})
# Obteniendo los objetos de la base de datos
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# data = models.execute_kw(db, uid, password,
#     products, read,
#     [[
#         ['detailed_type', '=', 'product']
#     ]],
#     {'fields': [
#       'name',
#       'taxes_id',
#       'list_price',
#     ], 'limit': 2}
# )

# print(str('Productos: '), data)

# print('') # Division

# CREACIÓN DE PRODUCTOS

# create = models.execute_kw(db, uid, password,
#   products, createProduct,
#   [
#     {
#       'name': 'Memoria RAM',
#       'sale_ok': True,
#       'purchase_ok': True,
#       'list_price': 450.00,
#       'standard_price': 300.00,
#     }
#   ]
# )

# print(str('Producto creado: '), create)
