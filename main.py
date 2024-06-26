import threading
import time

import odoo as netdata
import product as catalogue

TIME_STR = "%Y-%m-%d %H:%M:%S"

START = "Inicio de actualización {}: {}"
RESULT = "{} productos actualizados correctamente y {} inconvenientes"
END = "Ultima actualización de {}: {}"
SYS = "Syscom"
CT = "Ct"
TEC = "Tec"


def main():
    # * Actualizacion ct

    odoo = netdata.odoo_ct_uno()
    local_time = time.strftime(f"{TIME_STR} \n")
    print(START.format(CT, local_time), end="\r")
    print("")
    ct_products = catalogue.ct_main(odoo)
    ct_success = ct_products[0]
    ct_fails = ct_products[1]
    print(
        RESULT.format(ct_success, ct_fails),
        end="\r",
    )
    print("")
    local_time = time.strftime(f"{TIME_STR} \n\n")
    print(END.format(CT, local_time), end="\r")

    # * Actualizacion tec

    odoo = netdata.odoo_tec_uno()
    local_time = time.strftime(f"{TIME_STR} \n")
    print(START.format(TEC, local_time), end="\r")
    print("")
    tec_products = catalogue.tec_main(odoo)
    tec_success = tec_products[0]
    tec_fails = tec_products[1]
    print(
        RESULT.format(tec_success, tec_fails),
        end="\r",
    )
    print("")
    local_time = time.strftime(f"{TIME_STR} \n\n")
    print(END.format(TEC, local_time), end="\r")

    # * Actualizacion sys

    odoo = netdata.odoo_sys_uno()
    local_time = time.strftime(f"{TIME_STR} \n")
    print(START.format(SYS, local_time), end="\r")
    print("")
    sys_products = catalogue.sys_main(odoo)
    sys_success = sys_products[0]
    sys_fails = sys_products[1]
    print(
        RESULT.format(sys_success, sys_fails),
        end="\r",
    )
    print("")
    local_time = time.strftime(f"{TIME_STR} \n\n")
    print(END.format(SYS, local_time), end="\r")

    t = threading.Timer(5, main)
    t.start()


if __name__ == "__main__":
    main()
