import requests
import xmlrpc.client
import base64

# * Odoo
url = 'http://www.netdata.com.mx'
db = 'bitnami_odoo'

# * Credenciales
username = 'jmartinez@netdata.com.mx'
password = 'b046782b53d4b31eb0c3f901ec20a659ea0be1f3'

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url)) # * Conexión
uid = common.authenticate(db, username, password, {}) # * Autenticación
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url)) # * Obtención de objetos

objects = { # * Modelos disponibles en Odoo
    'products': 'product.template',
    'product_category': 'product.public.category',
}

actions = { # * Acciones disponibles en Odoo
    'read': 'search_read',
    'create': 'create'
}

# ? Llamado al API

url = 'https://fakestoreapi.com/products/' # * Url del API
res = requests.get(url) # * Llamada a la API

# ? Creación de producto, solo si el estatus es valido

if res.status_code == 200:
    content = res.json()
    first = content[1]
    print(content[1])
    gain = (first.get('price') * 25) / 100

    create = models.execute_kw(db, uid, password,
    objects.get('products'), actions.get('create'),
    [
        {
            'name': first.get('title'),
            'sale_ok': True,
            'purchase_ok': True,
            'list_price': first.get('price') + gain,
            'standard_price': first.get('price'),
            'description_sale': first.get('description'),
            'image_1920': first.get('image'), # * Encode base64
        }
    ]
    )
else:
    print('Error')
