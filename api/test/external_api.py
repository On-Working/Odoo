# External APi - XMLRPC

# Parametros configurables en el sistema externo
# Base de datos
url = 'https://nd-test.odoo.com/'
db = 'nd-test'

# Usuario
username= 'jmartinez@netdata.com.mx'
password = 'd2fe38692b1c10ce22ba64c9be4da48ca283aaec'

# API keys
test = 'd2fe38692b1c10ce22ba64c9be4da48ca283aaec'
ecommerce = 'b046782b53d4b31eb0c3f901ec20a659ea0be1f3'

# Libreria nativa de python xmlrpc
import xmlrpc.client
import json
import base64

# Conexion de prueba con el servidor de Odoo
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
output = common.version()
print(str('Version'), output)

print(' ') # Solo una division

# Llamamos las credenciales de prueba y regresamos el ID de usuario
uid = common.authenticate(db, username, password, {})
print(str('User id: '), uid)

# Inicializamos el modelo de puntos finales
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

# Metodos de llamada

# Leer datos de usuarios determinados
fields = models.execute_kw(db, uid, password,
    'res.partner', 'search_read',
    [[
        ['is_company', '=', True], # Ignorar usuarios que no coincidan
    ]],
    {'fields': [
        'total_due', # Deudas monetarias total
        'total_invoiced', # Facturas monetarias totales
        'total_overdue', # Atrasos monetarios totales
    ], 'limit': 5} # Limite de usuarios a obtener
)

# print('') # Solo una division

# print(str('Datos de contacto seleccionados: '), fields)

# print(' ') # Solo una division

# # Obtención de datos

# data = models.execute_kw(db, uid, password,
#     'res.partner', 'search',
#     [[
#         ['is_company', '=', True]
#     ]]
# )

# print(str('Listado de datos obtenidos: '), data)

# print(' ') # Solo una division

# # Paginación usando 'offset' y 'limit'

# pag = models.execute_kw(db, uid, password,
#     'res.partner', 'search',
#     [[
#         ['is_company', '=', True]
#     ]],
#     {'offset': 10, 'limit': 4}
# )

# print(str('Uso de paginación: '), pag)

# print(' ') # Solo una division

# # Creación de registros

# # newUser = models.execute_kw(db, uid, password,
# #     'res.partner', 'create',
# #     [
# #         {'name': 'David Carlo'}
# #     ]
# # )

# # print(str('Mi nuevo usuario: '), newUser)

# print(' ') # Solo una division

# # Actualización de registros

# id = 81
# theId = 82
# renewUser = models.execute_kw(db, uid, password,
#     'res.partner', 'write',
#     [
#         [theId],
#         {'name': 'Di Carlo Junior The Second'}
#     ]
# )
# # Obtención de nombre actualizado
# userData = models.execute_kw(db, uid, password,
#     'res.partner', 'name_get',
#     [
#         [theId]
#     ]
# )

# print(str('Usuario reciente actualizado: '), renewUser)
# print(str('Datos: '), userData)

# print(' ') # Solo una division

# # Eliminación de registros

# existUser = models.execute_kw(db, uid, password,
#     'res.partner', 'search',
#     [[
#         ['id', '=', id]
#     ]]
# )

# userDelete = models.execute_kw(db, uid, password,
#     'res.partner', 'unlink',
#     [
#         [id]
#     ]
# )

# noUser = models.execute_kw(db, uid, password,
#     'res.partner', 'search',
#     [[
#         ['id', '=', id]
#     ]]
# )

# print(str('Usuario reciente: '), existUser)
# print(str('Usuario eliminado: '), userDelete)
# print(str('Sin usuario: '), noUser)


