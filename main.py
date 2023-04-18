import schedule
import product

def main():
  created = False

  if created == False:
    print('Base de datos sin cambios')
  else:
    product.produc_creat()

if __name__ == '__main__':
  main()

  print('Conexión finalizada, base de datos actualizada con exito')
