import struct
import random

def redimensionar_bmp_aleatorio(ruta_img_origen, ruta_img_destino):
    # Fase 1: Lectura de cabecera y extracción de metadatos
    with open(ruta_img_origen, "rb") as archivo_origen:
        cabecera_bytes = bytearray(archivo_origen.read(54))
        
        # Desempaquetado de ancho y alto desde los offsets 0x12 (18) y 0x16 (22)
        ancho_orig = struct.unpack_from("<I", cabecera_bytes, 18)[0]
        alto_orig = struct.unpack_from("<I", cabecera_bytes, 22)[0]
        
        # Cálculo de bytes nulos para el alineamiento múltiplo de 4
        ajuste_padding_orig = (4 - ((ancho_orig * 3) % 4)) % 4
        
        matriz_pixeles = []
        for _ in range(alto_orig):
            bytes_linea = archivo_origen.read(ancho_orig * 3)
            archivo_origen.read(ajuste_padding_orig)  # Omitir padding anterior
            
            # Agrupación en bloques BGR (3 bytes)
            bloque_bgr = [bytes_linea[i:i+3] for i in range(0, len(bytes_linea), 3)]
            matriz_pixeles.append(bloque_bgr)

    # Fase 2: Expansión de dimensiones
    ancho_expandido = ancho_orig + 1
    alto_expandido = alto_orig + 1

    # Inserción de una nueva columna (un píxel al final de cada fila actual)
    for fila in matriz_pixeles:
        color_random = bytes([random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)])
        fila.append(color_random)

    # Inserción de una nueva fila base completa
    linea_extra = [bytes([random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]) for _ in range(ancho_expandido)]
    matriz_pixeles.append(linea_extra)

    # Fase 3: Recálculo estructural y actualización de cabecera
    ajuste_padding_nuevo = (4 - ((ancho_expandido * 3) % 4)) % 4
    peso_pixeles_total = ((ancho_expandido * 3) + ajuste_padding_nuevo) * alto_expandido
    peso_archivo_nuevo = 54 + peso_pixeles_total

    # Modificación in-place de la cabecera con los valores actualizados
    struct.pack_into("<I", cabecera_bytes, 2, peso_archivo_nuevo) 
    struct.pack_into("<I", cabecera_bytes, 18, ancho_expandido)    
    struct.pack_into("<I", cabecera_bytes, 22, alto_expandido)   

    # Fase 4: Escritura del nuevo mapa de bits
    with open(ruta_img_destino, "wb") as archivo_final:
        archivo_final.write(cabecera_bytes)
        
        secuencia_padding = b'\x00' * ajuste_padding_nuevo
        for fila in matriz_pixeles:
            for pixel in fila:
                archivo_final.write(pixel)
            archivo_final.write(secuencia_padding)

# Ejecución del script
redimensionar_bmp_aleatorio("./images/example001.bmp", "output_modificado.bmp")
