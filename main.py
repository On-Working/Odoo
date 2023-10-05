import schedule
import time
import product

TIME_STR = "%Y-%m-%d %H:%M:%S"


def main():
    local_time = time.strftime(f"{TIME_STR} \n")
    print(f"Inicio de actualización Tecnosinergia: {local_time}", end="\r")
    print("")
    product.produc_create()
    print("")
    local_time = time.strftime(f"{TIME_STR} \n")
    print(f"Ultima actualización Tecnosinergia: {local_time}", end="\r")

    local_time = time.strftime(f"{TIME_STR} \n")
    print(f"Inicio de actualización CT: {local_time}", end="\r")
    print("")
    product.ct_creation()
    print("")
    local_time = time.strftime(f"{TIME_STR} \n")
    print(
        f"Ultima actualización CT: {local_time}",
    )


if __name__ == "__main__":
    main()

    schedule.every().day.do(main)

    while True:
        schedule.run_pending()

        time.sleep(1)
