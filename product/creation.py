from decouple import config
import odoo
import tech_sinergy
import textwrap
import html
import base64

db = config('odoo_db', default='')
odo = odoo.odoo_connect()

uid = odo[0]
models = odo[1]
password = odo[2]

tec = tech_sinergy.tech_api()

info = tec[0]
data = tec[1]
data_image = tec[2]

def produc_creat():
    print('Iniciando creación masiva de productos en la base de datos de Odoo')
    print('NetDataSolutions')

    # * Text values
    title = textwrap.shorten(data.get('name'), width=100, placeholder='...')
    description = html.unescape(data.get('description'))

    # * Image value
    binary_image = base64.b64encode(data_image)
    final_image = binary_image.decode('ascii')

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

    print('Creación de productos en NetDataSolutions exitosa \n')
    return create