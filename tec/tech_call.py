from decouple import config
import requests

url = config("tech_url", default="")  # * Url del API
token = config("tech_token", default="")


def tech_catalogue():
    # ? Llamada al API
    print("Iniciando conexión con el API de Tecnosinergia")

    headers = {
        "Content-Type": "application/json",
        "api-token": token,
    }

    redirects = {
        "test": "/status",  # Prueba token
        "products": "/item/list",  # Lista de productos
        "product": "/item/list?item_id=",  # Producto especifico
        "addresses": "/address/list",  # Lista de direcciones
        "address": "/address/list?address_id=",  # Dirección especifica
        "order": "/order/create",  # Creación de una orden
    }

    res = requests.get(url + redirects.get("products"), headers=headers)

    if res.status_code != 200:
        print("Error en la llamada al API")
        return

    info = res.json()  # Respuesta en formato JSON
    data = info.get("data")  # Arreglo de productos

    print("Conexión con el API Tecnosinergia exitosa")
    print("Retornando datos: Info, Data \n")
    return (info, data)
