*El png sin nombre es un paint donde hice skins*
Corre el ajedrez.py


Para meter más skins:
  1º: Pon la imagen en la carpeta 'Fichas
  2º: En el código, rellena las comillas de la línea donde se encuentra un dibujo de la pieza que quieres cambiar (el color de la misma lo pone arriba) por algo como:
    os.path.join(CARPETA_FICHAS, "*nombre del archivo*")
