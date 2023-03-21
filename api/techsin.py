from decouple import config
import requests
import xmlrpc.client
import textwrap
import html
import base64

url = config('odoo_url', default='')
db = config('odoo_db', default='')

if url == '' or db == '':
    print('Error en la conexión principal con Odoo')

def odoo_connect():
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url)) # * Conexión

    username = config('odoo_username', default='')
    password = config('odoo_password', default='')

    if username == '' or password == '':
        print('Error en las credenciales')

    uid = common.authenticate(db, username, password, {}) # * Autenticación
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url)) # * Obtención de objetos

    if uid == False:
        print('Error en la autenticación del usuario')

    return (uid, models, password)

def tech_api():
    # ? Llamada al API

    headers = {
        'Content-Type' : 'application/json',
        'api-token' : config('tech_token', default='')
    }

    redirects = {
        'test': '/status', # Prueba token
        'products': '/item/list', # Lista de productos
        'product': '/item/list?item_id=', # Producto especifico
        'addresses': '/address/list', # Lista de direcciones
        'address': '/address/list?address_id=', # Dirección especifica
        'order': '/order/create'
    }

    url = config('tech_url', default = '') # * Url del API
    res = requests.get(url + redirects.get('product') + '9891', headers=headers) # * Llamada a la API

    if res.status_code != 200:
        print('Error en la llamada al API')

    info = res.json()
    data = info.get('data')
    image = data.get('image')
    get_image = requests.get(image)
    data_image = get_image.content

    print(data)

    return (info, data, data_image)

def encod_decod():
    # ? Decoding and encoding values

    tech = tech_api()
    data = tech[1]
    data_image = tech[2]

    # * Text values
    title = textwrap.shorten(data.get('name'), width=100, placeholder='...')
    desc = html.unescape(data.get('description'))

    # * Image value
    bynary_image = base64.b64encode(data_image)
    final_image = bynary_image.decode('ascii')

    return (title, desc, final_image)

def produc_creat():
    tech = tech_api()
    info = tech[0]
    data = tech[1]

    odoo = odoo_connect()
    uid = odoo[0]
    models = odoo[1]
    password = odoo[2]

    decoded = encod_decod()
    title = decoded[0]
    description = decoded[1]
    final_image = decoded[2]

    if info.get('status') != True or data.get('active') != True:
        print('Error, producto fuera de linea')

    # ? Creación de producto en Odoo

    objects = { # * Modelos disponibles en Odoo
        'products': 'product.template',
        'product_category': 'product.public.category',
    }

    actions = { # * Acciones disponibles en Odoo
        'read': 'search_read',
        'create': 'create'
    }

    create = models.execute_kw(db, uid, password,
    objects.get('products'), actions.get('create'),
    [
        {
            'is_published': data.get('active'),
            'name': title,
            'display_name': title,
            'sale_ok': True,
            'purchase_ok': True,
            'list_price': data.get('regular_price'),
            'standard_price': data.get('sale_price'),
            'description_sale': description,
            'weight': data.get('weight'),
            'volume' : data.get('volume'),
            'sale_delay': 15,
            'image_1920': final_image, # * Encode base64
        }
    ]
    )

    return create

produc_creat()


