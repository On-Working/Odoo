from decouple import config
from ftplib import FTP
import json
import requests

url = config("sys_url", default="")  # * Url del API
token = config("sys_token", default="")  # * Token del API


def sys_brands():
    print("Marcas Syscom")


def sys_catalogue():
    print("Iniciando conexión HTTP con Syscom")
    print("Conexión con el HTTP de Syscom exitosa")
    print("Retornando datos: Catalogue \n")
