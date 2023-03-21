import requests # Libreria de peticiones python
import xmlrpc.client # Cliente xmlrpc para conexiones proxy

# Base de datos de Odoo
url = 'https://nd-test.odoo.com/'
db = 'nd-test'

# Credenciales administrador de Odoo
username= 'jmartinez@netdata.com.mx'
password = 'd2fe38692b1c10ce22ba64c9be4da48ca283aaec'

# Conexión y autenticación al servicio de Odoo
common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url)) # Conexión
uid = common.authenticate(db, username, password, {}) # Autenticación
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url)) # Obtención de objetos

# Modelos de Odoo
objects = {
    'products': 'product.template',
}

# Acciones disponibles en Odoo
actions = {
    'read': 'search_read',
    'create': 'create'
}

# ? Continuar si es el programa principal
if __name__ == '__main__':
    url = 'https://fakestoreapi.com/products/'

    res = requests.get(url) # Llamada a la API

    # ? Continuar si el estatus es valido
    if res.status_code == 200:
        content = res.json()
        first = content[1]
        print(content[1])
        iva = (first.get('price') * 16) / 100
        gain = (first.get('price') * 25) / 100

        create = models.execute_kw(db, uid, password,
        objects.get('products'), actions.get('create'),
        [
            {
                'name': first.get('title'),
                'sale_ok': True,
                'purchase_ok': True,
                'list_price': first.get('price') + gain + iva,
                'standard_price': first.get('price'),
                'description_sale': first.get('description'),
            }
        ]
        )

        # for element in content:
        #     print('Fin del programa...')
