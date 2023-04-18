from decouple import config
import requests

def tech_api():
    # ? Llamada al API
    print('Iniciando conexión con el API de Tecnosinergia')

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

    print('Conexión con el API Tecnosinergia exitosa \n')
    print('Retornando datos: Info, Data, Data_image \n')
    return (info, data, data_image)
