# Transformación de imagen a una escala de 16 tonalidades de azul

imagen_entrada = open('./images/volcan.bmp', 'rb')
imagen_salida = open('./images/volcan_azul.bmp', 'wb')

# 1. Extracción y copiado de la cabecera (54 bytes)
cabecera_bmp = imagen_entrada.read(54)
imagen_salida.write(cabecera_bmp)

# 2. Construcción de la paleta de 16 tonalidades de azul (BGR)
escala_azules = []
for nivel in range(16):
    val_r = min(0 + (nivel * 15), 255)   
    val_g = min(40 + (nivel * 12), 255)  
    val_b = min(80 + (nivel * 11), 255)  
    escala_azules.append([int(val_b), int(val_g), int(val_r)])

# 3. Sustitución de píxeles
imagen_entrada.seek(54, 0)
contador_pixeles = 0

while True:
    bytes_pixel = imagen_entrada.read(3)
    if not bytes_pixel:
        break

    b_orig, g_orig, r_orig = bytes_pixel[0], bytes_pixel[1], bytes_pixel[2]

    # Determinación de luminancia y mapeo
    nivel_luminancia = (r_orig + g_orig + b_orig) // 3
    idx_color = min(nivel_luminancia // 16, 15)

    pixel_filtrado = escala_azules[idx_color]
    imagen_salida.write(bytes(pixel_filtrado))
    contador_pixeles += 1

print('Filtrado completado.')
imagen_entrada.close()
imagen_salida.close()
