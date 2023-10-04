import schedule
import time
import product


def main():
    local_time = time.strftime("%Y-%m-%d %H:%M:%S \n")
    print(f"Inicio de actualización Tecnosinergia: {local_time}", end="\r")
    product.produc_create()
    local_time = time.strftime("%Y-%m-%d %H:%M:%S \n")
    print(f"Ultima actualización Tecnosinergia: {local_time}", end="\r")


if __name__ == "__main__":
    main()

    schedule.every().day.do(main)

    while True:
        schedule.run_pending()

        time.sleep(1)
