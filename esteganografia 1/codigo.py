"""
Unidad de Aprendizaje: Multimedia
Alumno: Luis Fernando Tlapalcoyoac Olivares
Institución: UPIITA - IPN

Script de esteganografía LSB para ocultar y extraer texto en imágenes BMP, 
incluyendo la medición de degradación visual (PSNR).
"""

import math
import struct

def escribir_imagen_bmp(ruta_salida, cabecera_bmp, matriz_pixeles):
    """
    Almacena la estructura binaria en un nuevo archivo de imagen con formato BMP.
    """
    with open(ruta_salida, 'wb') as archivo_salida:
        archivo_salida.write(cabecera_bmp)
        archivo_salida.write(matriz_pixeles)

def cargar_imagen_bmp(ruta_entrada):
    """
    Abre y decodifica un archivo BMP en modo binario.
    Extrae la cabecera, la sección de datos y las dimensiones correspondientes.
    Retorna: (cabecera_bmp, matriz_pixeles, ancho_img, alto_img, padding_fila)
    """
    with open(ruta_entrada, 'rb') as archivo_entrada:
        trama_bytes = archivo_entrada.read()

        desplazamiento = struct.unpack_from('<I', trama_bytes, 10)[0]
        ancho_img = struct.unpack_from('<i', trama_bytes, 18)[0]
        alto_img = struct.unpack_from('<i', trama_bytes, 22)[0]
        
        padding_fila = ((ancho_img * 3 + 3) & ~3)
        
        cabecera_bmp = bytearray(trama_bytes[:desplazamiento])
        matriz_pixeles = bytearray(trama_bytes[desplazamiento:])
        
        return cabecera_bmp, matriz_pixeles, ancho_img, alto_img, padding_fila

def evaluar_calidad_psnr(ruta_base, ruta_modificada):
    """
    Determina la degradación visual (PSNR en dB) midiendo la diferencia 
    entre la imagen original y el medio portador (estego-imagen).
    """
    _, pixeles_base, w, h, _ = cargar_imagen_bmp(ruta_base)
    _, pixeles_stego, _, _, _ = cargar_imagen_bmp(ruta_modificada)
    
    # Obtención del Error Cuadrático Medio iterando todos los canales
    error_cuadratico = sum((val_orig - val_mod) ** 2 for val_orig, val_mod in zip(pixeles_base, pixeles_stego)) / (w * h * 3)
    
    if error_cuadratico == 0:
        print("Resultado: Ambas imágenes son idénticas a nivel de bits.")
        return float('inf')
        
    # Fórmula estándar de PSNR para imágenes de 8 bits por canal
    valor_psnr = 10 * math.log10((255 ** 2) / error_cuadratico)
    
    print(f'Métrica MSE registrada: {error_cuadratico:.6f}')
    print(f'Métrica PSNR registrada: {valor_psnr:.2f} dB (Valores > 40 dB implican cambios indetectables)')
    return valor_psnr

def ocultar_texto_lsb(ruta_origen, ruta_destino, texto_secreto):
    """
    Inserta un bloque de texto en el bit menos significativo (LSB) de los canales 
    de color de una imagen de mapa de bits.
    """
    cabecera_bmp, matriz_pixeles, ancho_img, alto_img, padding_fila = cargar_imagen_bmp(ruta_origen)
    
    bytes_texto = texto_secreto.encode('utf-8')
    tamano_texto = len(bytes_texto)
    
    # Empaquetamiento de la longitud (4 bytes, Little-Endian) junto con el payload
    trama_datos = struct.pack('<I', tamano_texto) + bytes_texto
    
    arreglo_bits = []
    for octeto in trama_datos:
        for bit_pos in range(7, -1, -1):
            arreglo_bits.append((octeto >> bit_pos) & 1)
            
    if len(arreglo_bits) > len(matriz_pixeles):
        raise ValueError('Capacidad excedida: El texto introducido es demasiado largo para el medio portador.')
        
    pixeles_alterados = bytearray(matriz_pixeles)
    for indice, valor_bit in enumerate(arreglo_bits):
        # La máscara 0xFE asegura que el LSB se resetee a 0, luego se aplica OR con el nuevo bit
        pixeles_alterados[indice] = (pixeles_alterados[indice] & 0xFE) | valor_bit 
        
    escribir_imagen_bmp(ruta_destino, cabecera_bmp, pixeles_alterados)
    print(f'[ÉXITO] Carga útil de {tamano_texto} bytes inyectada correctamente en: {ruta_destino}')

def recuperar_texto_lsb(ruta_estego_img):
    """
    Extrae la carga útil oculta en el LSB de la imagen procesada.
    Primero recupera los 4 bytes iniciales para conocer la extensión del texto.
    """
    _, matriz_pixeles, _, _, _ = cargar_imagen_bmp(ruta_estego_img)
    
    # Fase 1: Extracción del tamaño (primeros 32 bits)
    bits_longitud = [matriz_pixeles[idx] & 1 for idx in range(32)]
    
    bloque_longitud = bytearray()
    for idx in range(0, 32, 8):
        octeto_tmp = 0
        for b in bits_longitud[idx:idx+8]:
            octeto_tmp = (octeto_tmp << 1) | b
        bloque_longitud.append(octeto_tmp)
        
    # Desempaquetado usando Little-Endian para coincidir con la fase de ocultamiento
    tamano_texto = struct.unpack('<I', bloque_longitud)[0]
        
    # Fase 2: Extracción de los bits pertenecientes al mensaje principal
    limite_bits = 32 + (tamano_texto * 8)
    bits_texto = [matriz_pixeles[idx] & 1 for idx in range(32, limite_bits)]
    
    # Fase 3: Agrupación de los bits extraídos para formar bytes
    bloque_bytes_mensaje = bytearray()
    for idx in range(0, len(bits_texto), 8):
        octeto_tmp = 0
        for b in bits_texto[idx:idx+8]:
            octeto_tmp = (octeto_tmp << 1) | b
        bloque_bytes_mensaje.append(octeto_tmp)
        
    # Fase 4: Retorno del mensaje decodificado
    return bloque_bytes_mensaje.decode('utf-8')

# ==========================================
# BLOQUE PRINCIPAL DE EJECUCIÓN
# ==========================================
if __name__ == "__main__":
    img_original_ruta = 'imagen512.bmp'
    img_modificada_ruta = 'stego512_max.bmp'

    # Variables de prueba
    txt_500_chars = "A" * 500
    txt_5000_chars = "B" * 5000
    txt_maximo_chars = "C" * 98300

    # Selección del mensaje a inyectar
    informacion_a_ocultar = txt_maximo_chars

    print(">>> Iniciando el algoritmo esteganográfico <<<")
    # Paso 1: Inyección
    ocultar_texto_lsb(img_original_ruta, img_modificada_ruta, informacion_a_ocultar)

    # Paso 2: Recuperación
    texto_rescatado = recuperar_texto_lsb(img_modificada_ruta)

    # Paso 3: Control de calidad e integridad
    assert texto_rescatado == informacion_a_ocultar, 'Fallo crítico: El texto extraído no coincide con el original.'
    print('Validación superada. La extracción de datos se completó de forma íntegra.')

    # Paso 4: Análisis de calidad de imagen (PSNR)
    print("\n>>> Evaluando métricas de distorsión visual <<<")
    evaluar_calidad_psnr(img_original_ruta, img_modificada_ruta)
