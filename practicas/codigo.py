"""
Unidad de Aprendizaje: Multimedia
Alumno: Luis Fernando Tlapalcoyoac Olivares
Institución: UPIITA - IPN

Script de esteganografía avanzada con distribución pseudoaleatoria 
y cifrado de flujo XOR basado en contraseñas, incluyendo 
un módulo de estegoanálisis mediante la prueba Chi-cuadrado.
"""

import struct
import hashlib
import random

def obtener_datos_bmp(ruta_archivo):
    """
    Parsea la estructura de un archivo BMP.
    Retorna una tupla conteniendo: (bytes_cabecera, arreglo_pixeles, ancho, alto, tamano_fila).
    """
    with open(ruta_archivo, 'rb') as archivo:
        trama = archivo.read()

        inicio_datos = struct.unpack_from('<I', trama, 10)[0]
        ancho_img = struct.unpack_from('<i', trama, 18)[0]
        alto_img = struct.unpack_from('<i', trama, 22)[0]
        
        # Cálculo del relleno (padding) por fila para alineación a 4 bytes
        padding_fila = ((ancho_img * 3 + 3) & ~3)
        
        cabecera_img = bytearray(trama[:inicio_datos])
        arreglo_pixeles = bytearray(trama[inicio_datos:])
        
        return cabecera_img, arreglo_pixeles, ancho_img, alto_img, padding_fila

def escribir_datos_bmp(ruta_destino, cabecera_img, arreglo_pixeles):
    """
    Crea un nuevo archivo de imagen escribiendo la cabecera seguida del volcado de píxeles.
    """
    with open(ruta_destino, 'wb') as archivo_salida:
        archivo_salida.write(cabecera_img)
        archivo_salida.write(arreglo_pixeles)

# ==========================================
# MÓDULOS DE CIFRADO Y SEGURIDAD
# ==========================================

def generar_llave_flujo(contrasena: str, tamano_requerido: int) -> bytes:
    """
    Construye una secuencia pseudoaleatoria de bytes del tamaño especificado 
    utilizando el algoritmo SHA-256 iterado como un cifrador de flujo.
    """
    llave_resultante = b''
    iterador = 0
    while len(llave_resultante) < tamano_requerido:
        # Se genera el hash de la contraseña concatenada con un contador de 32 bits
        bloque_hash = hashlib.sha256(contrasena.encode() + struct.pack('<I', iterador)).digest()
        llave_resultante += bloque_hash
        iterador += 1
    return llave_resultante[:tamano_requerido]

def aplicar_cifrado_xor(texto_plano: bytes, contrasena: str) -> bytes:
    """
    Aplica una operación XOR a nivel de byte entre los datos de entrada y la llave de flujo.
    """
    llave_flujo = generar_llave_flujo(contrasena, len(texto_plano))
    return bytes([byte_msj ^ byte_llave for byte_msj, byte_llave in zip(texto_plano, llave_flujo)])

def revertir_cifrado_xor(texto_cifrado: bytes, contrasena: str) -> bytes:
    """
    Aprovecha la propiedad involutiva de la operación XOR para recuperar el texto original.
    """
    return aplicar_cifrado_xor(texto_cifrado, contrasena)

def obtener_semilla_entera(contrasena: str) -> int:
    """
    Deriva un valor numérico entero a partir del resumen criptográfico de la contraseña,
    adecuado para inicializar generadores pseudoaleatorios.
    """
    resumen_bytes = hashlib.sha256(contrasena.encode()).digest()
    return int.from_bytes(resumen_bytes[:8], 'big')

def calcular_indices_pseudoaleatorios(total_espacio: int, cantidad_indices: int, valor_semilla: int) -> list:
    """
    Genera una secuencia predecible y desordenada de índices sin repetición, 
    asegurando que la inyección de bits se distribuya por toda la imagen.
    """
    generador = random.Random(valor_semilla)
    
    # Se crea un mapeo del espacio total y se permuta según la semilla
    mapeo_indices = list(range(total_espacio))
    generador.shuffle(mapeo_indices)
    
    return mapeo_indices[:cantidad_indices]

# ==========================================
# RUTINAS PRINCIPALES DE ESTEGANOGRAFÍA
# ==========================================

def inyectar_datos_seguros(ruta_origen, ruta_destino, texto_oculto, contrasena):
    """
    Oculta un mensaje cifrado distribuyendo sus bits en posiciones aleatorias de la imagen.
    """
    cabecera, pixeles, w, h, padding = obtener_datos_bmp(ruta_origen)
    
    bytes_mensaje = texto_oculto.encode('utf-8')
    # Fase 1: Cifrado de la carga útil
    payload_cifrado = aplicar_cifrado_xor(bytes_mensaje, contrasena)
    
    # Fase 2: Empaquetado (Longitud 4 bytes + Payload)
    trama_completa = struct.pack('<I', len(bytes_mensaje)) + payload_cifrado
    
    # Fase 3: Descomposición en matriz de bits
    arreglo_bits = []
    for octeto in trama_completa:
        for bit_pos in range(7, -1, -1):
            arreglo_bits.append((octeto >> bit_pos) & 1)
            
    cantidad_bits = len(arreglo_bits)
    if cantidad_bits > len(pixeles):
        raise ValueError('Capacidad excedida: El portador es insuficiente para el tamaño del mensaje.')
        
    # Fase 4: Selección de espacio portador
    semilla = obtener_semilla_entera(contrasena)
    posiciones_objetivo = calcular_indices_pseudoaleatorios(len(pixeles), cantidad_bits, semilla)
    
    # Fase 5: Inserción de bits LSB en las coordenadas generadas
    pixeles_alterados = bytearray(pixeles)
    for coordenada, valor_bit in zip(posiciones_objetivo, arreglo_bits):
        pixeles_alterados[coordenada] = (pixeles_alterados[coordenada] & 0xFE) | valor_bit
        
    escribir_datos_bmp(ruta_destino, cabecera, pixeles_alterados)
    print(f'[ÉXITO] {len(bytes_mensaje)} bytes procesados e inyectados en: {ruta_destino}')

def recuperar_datos_seguros(ruta_estego_img, contrasena):
    """
    Extrae y descifra la carga útil recuperando los bits desde las posiciones exactas 
    generadas por la contraseña.
    """
    _, pixeles, _, _, _ = obtener_datos_bmp(ruta_estego_img)
    semilla = obtener_semilla_entera(contrasena)
    
    # Fase 1: Localización y extracción del descriptor de tamaño (32 bits)
    coords_longitud = calcular_indices_pseudoaleatorios(len(pixeles), 32, semilla)
    bits_tamano = [pixeles[coord] & 1 for coord in coords_longitud]
    
    bloque_bytes_tamano = bytearray()
    for idx in range(0, 32, 8):
        octeto_temp = 0
        for b in bits_tamano[idx:idx+8]:
            octeto_temp = (octeto_temp << 1) | b
        bloque_bytes_tamano.append(octeto_temp)
        
    tamano_mensaje = struct.unpack('<I', bloque_bytes_tamano)[0]
    
    # Fase 2: Recalculando coordenadas para extraer el mensaje
    total_bits_esperados = 32 + (tamano_mensaje * 8)
    coords_totales = calcular_indices_pseudoaleatorios(len(pixeles), total_bits_esperados, semilla)
    
    # Extracción de la sección de datos cifrados
    bits_cifrados = [pixeles[coord] & 1 for coord in coords_totales[32:]]
    
    # Fase 3: Reconstrucción del arreglo de bytes
    bytes_cifrados = bytearray()
    for idx in range(0, len(bits_cifrados), 8):
        octeto_temp = 0
        for b in bits_cifrados[idx:idx+8]:
            octeto_temp = (octeto_temp << 1) | b
        bytes_cifrados.append(octeto_temp)
        
    # Fase 4: Descifrado y decodificación final
    return revertir_cifrado_xor(bytes(bytes_cifrados), contrasena).decode('utf-8')

# ==========================================
# MÓDULO DE AUDITORÍA Y ESTEGOANÁLISIS
# ==========================================

def analisis_estego_chi2(ruta_analisis):
    """
    Aplica una prueba de bondad de ajuste Chi-cuadrado sobre los bits menos significativos (LSB)
    para detectar anomalías probabilísticas indicativas de esteganografía.
    """
    _, pixeles, _, _, _ = obtener_datos_bmp(ruta_analisis)
    
    # Cuantificación de distribución de LSBs
    frecuencia_ceros = sum(1 for byte_val in pixeles if (byte_val & 1) == 0)
    frecuencia_unos = len(pixeles) - frecuencia_ceros
    
    # Modelo teórico esperado (distribución uniforme 50/50)
    frecuencia_esperada = len(pixeles) / 2
    
    # Cómputo del estadístico Chi-cuadrado
    estadistico_chi2 = ((frecuencia_ceros - frecuencia_esperada) ** 2 + 
                        (frecuencia_unos - frecuencia_esperada) ** 2) / frecuencia_esperada
    
    print(f'Evaluando archivo: {ruta_analisis}')
    print(f'Conteo LSB=0: {frecuencia_ceros} | LSB=1: {frecuencia_unos} | Valor x²: {estadistico_chi2:.4f}')
    
    # Evaluación de umbral empírico
    if estadistico_chi2 < 100:
         print('>>> [ADVERTENCIA] Uniformidad inusual detectada. Alta probabilidad de datos incrustados.')
    else:
         print('>>> [NORMAL] Distribución acorde a ruido fotográfico natural.')
    print('-' * 50)
    
    return estadistico_chi2

# ==========================================
# BLOQUE DE EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == '__main__':
    LLAVE_ACCESO = 'Telematica@2025'
    INFORMACION_SECRETA = 'Datos confidenciales de la red 10.0.1.0/24'
    
    # Archivos de prueba
    img_portadora = 'archivo_520.bmp' 
    img_resultante = 'archivo_520_seguro.bmp'

    print(">>> Iniciando inyección con seguridad criptográfica <<<")
    inyectar_datos_seguros(img_portadora, img_resultante, INFORMACION_SECRETA, LLAVE_ACCESO)

    print("\n>>> Protocolo de recuperación (Llave válida) <<<")
    datos_recuperados = recuperar_datos_seguros(img_resultante, LLAVE_ACCESO)
    print(f'Texto extraído: "{datos_recuperados}"')
    
    assert datos_recuperados == INFORMACION_SECRETA, "Fallo crítico: Discrepancia en los datos recuperados."

    print("\n>>> Protocolo de recuperación (Llave inválida) <<<")
    try:
        basura_criptografica = recuperar_datos_seguros(img_resultante, 'claveWrong')
        print(f'Resultado (inválido): "{basura_criptografica[:30]}..." (Comportamiento esperado)')
    except UnicodeDecodeError:
        print("Resultado: Excepción UnicodeDecodeError. (Validación de seguridad exitosa)")
    except Exception as error_sistema:
        print(f'Excepción no controlada detectada: {error_sistema}')
