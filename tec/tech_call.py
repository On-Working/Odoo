import requests

from decouple import config

URL = config("TECH_URL", default="")  # * Url del API
TOKEN = config("TECH_TOKEN", default="")


def tech_catalogue():
    # ? Llamada al API
    print("Iniciando conexión con el API de Tecnosinergia")

    headers = {
        "Content-Type": "application/json",
        "api-token": TOKEN,
    }

    redirects = {
        "test": "/status",  # Prueba token
        "products": "/item/list",  # Lista de productos
        "product": "/item/list?item_id=",  # Producto especifico
        "addresses": "/address/list",  # Lista de direcciones
        "address": "/address/list?address_id=",  # Dirección especifica
        "order": "/order/create",  # Creación de una orden
    }

    res = requests.get(URL + redirects.get("products"), headers=headers)

    if res.status_code != 200:
        print("Error en la llamada al API")
        return

    info = res.json()  # Respuesta en formato JSON
    catalogue = info.get("data")  # Arreglo de productos

    lenght = len(catalogue)
    print("Conexión con el API Tecnosinergia exitosa")
    print(f"Retornando datos: Respuesta, Catalogo[{lenght}] \n")
    return (info, catalogue)
