import requests

from decouple import config

URL = config("SYS_URL", default="")  # * Url del API
TOKEN = config("SYS_TOKEN", default="")  # * Token del API

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {}".format(TOKEN),
}

redirects = {
    "exchange": "/tipocambio",  # ? Cambio de dolar
    "brands": "/marcas",  # ? Todas las marcas
    "brand_prods": "/marcas/{}/productos/?pagina={}",  # ? Todos los productos de una marca
    "categories": "/categorias",
    "cat_prods": "/productos/?categoria={}&pagina={}",
}


def sys_exchange():
    conversion = redirects.get("exchange")
    get_exchange = requests.get(URL + conversion, headers=headers)
    exchange = get_exchange.json().get("normal")

    return exchange


def sys_brands():
    all_brands = redirects.get("brands")
    get_brands = requests.get(URL + all_brands, headers=headers)
    brands = get_brands.json()

    return brands


def sys_categories():
    all_categories = redirects.get("categories")
    get_categories = requests.get(URL + all_categories, headers=headers)
    categories = get_categories.json()

    return categories


def sys_categorie_products(cat_id, page):
    products = 0
    prod_categories = redirects.get("cat_prods")

    get_cat_prods = requests.get(
        URL + prod_categories.format(cat_id, page), headers=headers
    )

    products = get_cat_prods.json()

    return products


def sys_brand_products(brand_id, page):
    products = 0
    prod_brands = redirects.get("brand_prods")

    get_brand_prods = requests.get(
        URL + prod_brands.format(brand_id, page), headers=headers
    )

    products = get_brand_prods.json()

    return products


def sys_catalogue():
    print("Iniciando conexión HTTP con Syscom")
    catalogue = []

    categories = sys_categories()

    for categorie in categories:
        page = 1
        categorie_id = categorie.get("id")

        products = sys_categorie_products(categorie_id, page)
        pages = products.get("paginas")
        qty = products.get("cantidad")

        if qty == 0:
            page += 1
            continue

        while page <= pages:
            products_page = sys_categorie_products(categorie_id, page)
            products = products_page.get("productos")

            for product in products:
                catalogue.append(product)

            page += 1

    lenght = len(catalogue)
    print("Conexión con el HTTP de Syscom exitosa")
    print(f"Retornando datos: Catalogo[{lenght}] \n")

    return catalogue
