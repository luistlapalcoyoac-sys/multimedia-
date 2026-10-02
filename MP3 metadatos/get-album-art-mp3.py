from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

def exportar_arte_album(ruta_mp3, ruta_imagen_salida="portada_extraida.jpg"):
    # Instanciar el objeto manejador del archivo MP3
    archivo_sonido = MP3(ruta_mp3, ID3=ID3)

    # Iterar sobre las tramas buscando la etiqueta correspondiente a la imagen adjunta (APIC)
    for trama in archivo_sonido.tags.values():
        if isinstance(trama, APIC):
            # Volcar los datos binarios extraídos en un nuevo archivo de imagen
            with open(ruta_imagen_salida, "wb") as archivo_img:
                archivo_img.write(trama.data)
            print("¡Arte de álbum exportado con éxito!")
            break

# Bloque de ejecución principal
exportar_arte_album("Fly Me To The Moon.mp3")
