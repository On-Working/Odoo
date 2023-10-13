import schedule
import time
import product

TIME_STR = "%Y-%m-%d %H:%M:%S"


def main():
    local_time = time.strftime(f"{TIME_STR} \n")
    print(f"Inicio de actualización Tecnosinergia: {local_time}", end="\r")
    print("")
    tec_products = product.tec_main()
    print(f"{tec_products} productos actualizados correctamente", end="\r")
    print("")
    local_time = time.strftime(f"{TIME_STR} \n")
    print(f"Ultima actualización Tecnosinergia: {local_time}", end="\r")

    local_time = time.strftime(f"{TIME_STR} \n")
    print(f"Inicio de actualización CT: {local_time}", end="\r")
    print("")
    ct_products = product.ct_main()
    print(f"{ct_products} productos actualizados correctamente", end="\r")
    print("")
    local_time = time.strftime(f"\n{TIME_STR} \n")
    print(f"Ultima actualización CT: {local_time}", end="\r")

    local_time = time.strftime(f"{TIME_STR} \n")
    print(f"Inicio de actualización Syscom: {local_time}", end="\r")
    print("")
    sys_products = product.sys_main()
    print(f"{sys_products} productos actualizados correctamente", end="\r")
    print("")
    local_time = time.strftime(f"{TIME_STR} \n")
    print(f"Ultima actualización de Syscom: {local_time}", end="\r")


if __name__ == "__main__":
    main()

    schedule.every().day.do(main)

    while True:
        schedule.run_pending()

        time.sleep(1)
