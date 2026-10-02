from mutagen.mp3 import MP3
from mutagen.id3 import ID3

def inspeccionar_todas_las_etiquetas(ruta_mp3):
    # Lectura del archivo multimedia
    pista = MP3(ruta_mp3, ID3=ID3)

    print(f"--- Volcado de metadatos crudos para: {ruta_mp3} ---")
    
    # Recorrer secuencialmente el diccionario de etiquetas y mostrar su contenido
    for clave_etiqueta in pista.tags:
        valor_etiqueta = pista.tags[clave_etiqueta]
        print(f"[{clave_etiqueta}] -> {valor_etiqueta}")

# Bloque de ejecución principal
inspeccionar_todas_las_etiquetas("Fly Me To The Moon.mp3")