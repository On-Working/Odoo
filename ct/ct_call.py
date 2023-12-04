import json

from decouple import config
from ftplib import FTP

URL = config("CT_URL", default="")
FTP_HOST = config("CT_HOST", default="")
FTP_USER = config("CT_USER", default="")
FTP_PASSWORD = config("CT_PASS", default="")
FTP_DIRECTORY = config("CT_DIR", default="")
JSON_FILE = config("CT_FILE", default="")


def ct_catalogue():
    print("Iniciando conexión FTP con CT")

    # ? Instancia FTP
    ftp = FTP(FTP_HOST)

    # ? Inicio de sesion FTP
    ftp.login(FTP_USER, FTP_PASSWORD)

    # ? Directorio deseado
    ftp.cwd(FTP_DIRECTORY)

    # ? Archivo JSON
    with open(JSON_FILE, "wb") as local_file:
        ftp.retrbinary("RETR " + JSON_FILE, local_file.write)

    # ? Conexion FTP cerrada
    ftp.quit()

    # ? Carga y trabaja con el archivo JSON localmente
    with open(JSON_FILE, "r") as local_file:
        catalogue = json.load(local_file)

    lenght = len(catalogue)
    print("Conexión con el FTP de CT exitosa")
    print(f"Retornando datos: Catalogo[{lenght}] \n")

    return catalogue
