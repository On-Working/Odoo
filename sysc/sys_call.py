from decouple import config
import requests

url = config("sys_url", default="")  # * Url del API
token = config("sys_token", default="")  # * Token del API

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {}".format(token),
}

redirects = {
    "exchange": "/tipocambio",  # ? Cambio de dolar
    "brands": "/marcas",  # ? Todas las marcas
    "brand_prods": "/marcas/{}/productos",  # ? Todos los productos de una marca
}


def sys_exchange():
    conversion = redirects.get("exchange")
    get_exchange = requests.get(url + conversion, headers=headers)
    exchange = get_exchange.json().get("normal")

    return exchange


def sys_brands():
    print("Iniciando conexión HTTP con Syscom")

    all_brands = redirects.get("brands")
    get_brands = requests.get(url + all_brands, headers=headers)
    brands = get_brands.json()

    print("Conexión con el HTTP de Syscom exitosa")
    print("Retornando datos: Brands \n")

    return brands


def sys_catalogue(brand):
    brand_prods = redirects.get("brand_prods")

    get_prods = requests.get(url + brand_prods.format(brand), headers=headers)

    brand_prods = get_prods.json()

    return brand_prods
