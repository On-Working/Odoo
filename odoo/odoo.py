import xmlrpc.client

from decouple import config


URL = config("NDS_URL", default="")
DB = config("NDS_DB", default="")
USER = config("NDS_USERNAME", default="")
PASSWORD = config("NDS_PASSWORD", default="")
COMMON = config("ODOO_COMMON", default="")
OBJECT = config("ODOO_OBJECT", default="")
SYS_UNO = config("NDS_SYS_UNO", default="")
SYS_DOS = config("NDS_SYS_DOS", default="")
SYS_TRES = config("NDS_SYS_TRES", default="")
SYS_CUATRO = config("NDS_SYS_CUATRO", default="")
SYS_CINCO = config("NDS_SYS_CINCO", default="")
SYS_SEIS = config("NDS_SYS_SEIS", default="")
SYS_SIETE = config("NDS_SYS_SIETE", default="")
SYS_OCHO = config("NDS_SYS_OCHO", default="")
SYS_NUEVE = config("NDS_SYS_NUEVE", default="")
SYS_DIEZ = config("NDS_SYS_DIEZ", default="")

SYS_ONCE = config("NDS_SYS_ONCE", default="")
SYS_DOCE = config("NDS_SYS_DOCE", default="")
SYS_TRECE = config("NDS_SYS_TRECE", default="")
SYS_CATORCE = config("NDS_SYS_CATORCE", default="")
SYS_QUINCE = config("NDS_SYS_QUINCE", default="")
SYS_DIECISEIS = config("NDS_SYS_DIECISEIS", default="")
SYS_DIECISIETE = config("NDS_SYS_DIECISIETE", default="")
SYS_DIECIOCHO = config("NDS_SYS_DIECIOCHO", default="")
SYS_DIECINUEVE = config("NDS_SYS_DIECINUEVE", default="")
SYS_VEINTE = config("NDS_SYS_VEINTE", default="")
SYS_VEINTIUNO = config("NDS_SYS_VEINTIUNO", default="")
SYS_VEINTIDOS = config("NDS_SYS_VEINTIDOS", default="")
SYS_VEINTITRES = config("NDS_SYS_VEINTITRES", default="")

CT_UNO = config("NDS_CT_UNO", default="")
CT_DOS = config("NDS_CT_DOS", default="")
CT_TRES = config("NDS_CT_TRES", default="")
CT_CUATRO = config("NDS_CT_CUATRO", default="")
CT_CINCO = config("NDS_CT_CINCO", default="")

TEC_UNO = config("NDS_TEC_UNO", default="")
TEC_DOS = config("NDS_TEC_DOS", default="")
TEC_TRES = config("NDS_TEC_TRES", default="")
TEC_CUATRO = config("NDS_TEC_CUATRO", default="")
TEC_CINCO = config("NDS_TEC_CINCO", default="")


# ? Conexión original
def odoo_connect():
    if URL == "":
        print("Error en la conexión principal con Odoo")
        return

    print("Iniciando conexión con la base de datos de Odoo")
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    if USER == "" or PASSWORD == "":
        print("Error en las credenciales")
        return

    uid = common.authenticate(DB, USER, PASSWORD, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    if uid == False:
        print("Error en la autenticación del usuario")
        return

    print("Conexión con la base de datos Netdata Solutions exitosa")
    print("Retornando datos: Uid, Models, Password \n")
    return (uid, models, DB, PASSWORD)


# ? Conexiones SYSCOM
def odoo_sys_uno():
    if URL == "":
        print("Error en la conexión principal con Odoo")
        return

    print("Iniciando conexión con la base de datos de Odoo")
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    if USER == "" or SYS_UNO == "":
        print("Error en las credenciales")
        return

    uid = common.authenticate(DB, USER, SYS_UNO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    if uid == False:
        print("Error en la autenticación del usuario")
        return

    print("Conexión con la base de datos Netdata Solutions exitosa")
    print("Retornando datos: Uid, Models, Password \n")
    return (uid, models, DB, SYS_UNO)


def odoo_sys_dos():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_DOS, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_DOS)


def odoo_sys_tres():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_TRES, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_TRES)


def odoo_sys_cuatro():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_CUATRO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_CUATRO)


def odoo_sys_cinco():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_CINCO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_CINCO)


def odoo_sys_seis():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_SEIS, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_SEIS)


def odoo_sys_siete():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_SIETE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_SIETE)


def odoo_sys_ocho():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_OCHO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_OCHO)


def odoo_sys_nueve():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_NUEVE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_NUEVE)


def odoo_sys_diez():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_DIEZ, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_DIEZ)


def odoo_sys_once():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_ONCE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_ONCE)


def odoo_sys_doce():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_DOCE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_DOCE)


def odoo_sys_trece():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_TRECE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_TRECE)


def odoo_sys_catorce():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_CATORCE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_CATORCE)


def odoo_sys_quince():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_QUINCE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_QUINCE)


def odoo_sys_dieciseis():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_DIECISEIS, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_DIECISEIS)


def odoo_sys_diecisiete():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_DIECISIETE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_DIECISIETE)


def odoo_sys_dieciocho():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_DIECIOCHO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_DIECIOCHO)


def odoo_sys_diecinueve():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_DIECINUEVE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_DIECINUEVE)


def odoo_sys_veinte():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_VEINTE, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_VEINTE)


def odoo_sys_veintiuno():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_VEINTIUNO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_VEINTIUNO)


def odoo_sys_veintidos():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_VEINTIDOS, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_VEINTIDOS)


def odoo_sys_veintitres():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, SYS_VEINTITRES, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, SYS_VEINTITRES)


# ? Conexiones CT
def odoo_ct_uno():
    if URL == "":
        print("Error en la conexión principal con Odoo")
        return

    print("Iniciando conexión con la base de datos de Odoo")
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    if USER == "" or CT_UNO == "":
        print("Error en las credenciales")
        return

    uid = common.authenticate(DB, USER, CT_UNO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    if uid == False:
        print("Error en la autenticación del usuario")
        return

    print("Conexión con la base de datos Netdata Solutions exitosa")
    print("Retornando datos: Uid, Models, Password \n")
    return (uid, models, DB, CT_UNO)


def odoo_ct_dos():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, CT_DOS, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, CT_DOS)


def odoo_ct_tres():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, CT_TRES, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, CT_TRES)


def odoo_ct_cuatro():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, CT_CUATRO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, CT_CUATRO)


def odoo_ct_cinco():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, CT_CINCO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, CT_CINCO)


# ? Conexiones TECNOSINERGIA
def odoo_tec_uno():
    if URL == "":
        print("Error en la conexión principal con Odoo")
        return

    print("Iniciando conexión con la base de datos de Odoo")
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    if USER == "" or TEC_UNO == "":
        print("Error en las credenciales")
        return

    uid = common.authenticate(DB, USER, TEC_UNO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    if uid == False:
        print("Error en la autenticación del usuario")
        return

    print("Conexión con la base de datos Netdata Solutions exitosa")
    print("Retornando datos: Uid, Models, Password \n")

    return (uid, models, DB, TEC_UNO)


def odoo_tec_dos():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, TEC_DOS, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, TEC_DOS)


def odoo_tec_tres():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, TEC_TRES, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, TEC_TRES)


def odoo_tec_cuatro():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, TEC_CUATRO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, TEC_CUATRO)


def odoo_tec_cinco():
    common = xmlrpc.client.ServerProxy(COMMON.format(URL))  # * Conexión

    uid = common.authenticate(DB, USER, TEC_CINCO, {})  # * Autenticación
    models = xmlrpc.client.ServerProxy(OBJECT.format(URL))  # * Obtención de objetos

    return (uid, models, DB, TEC_CINCO)
