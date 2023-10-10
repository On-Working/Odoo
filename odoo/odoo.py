from decouple import config
import xmlrpc.client

url = config("odoo_test_url", default="")
# url = config("odoo_url", default="")


def odoo_connect(db):
    if url == "":
        print("Error en la conexión principal con Odoo")
        return

    print("Iniciando conexión con la base de datos de Odoo")
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")  # * Conexión

    username = config("odoo_username", default="")
    password = config("odoo_password", default="")

    if username == "" or password == "":
        print("Error en las credenciales")
        return

    uid = common.authenticate(db, username, password, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(
        "{}/xmlrpc/2/object".format(url)
    )  # * Obtención de objetos

    if uid == False:
        print("Error en la autenticación del usuario")
        return

    print("Conexión con la base de datos Netdata Solutions exitosa")
    print("Retornando datos: Uid, Models, Password \n")
    return (uid, models, password)
