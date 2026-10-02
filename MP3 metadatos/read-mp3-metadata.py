from mutagen.mp3 import MP3
from mutagen.id3 import ID3

def mostrar_detalles_pista(ruta_mp3):
    # Inicializar el lector y obtener el objeto de audio
    reproduccion = MP3(ruta_mp3, ID3=ID3)

    # Obtener el tiempo de reproducción total del objeto 'info'
    tiempo_segundos = reproduccion.info.length
    diccionario_etiquetas = reproduccion.tags

    # Extraer campos clave manejando excepciones por si no existen
    nombre_cancion = diccionario_etiquetas.get('TIT2', 'Título no definido').text[0]
    nombre_artista = diccionario_etiquetas.get('TPE1', 'Intérprete no definido').text[0]
    nombre_album = diccionario_etiquetas.get('TALB', 'Disco no definido').text[0]

    # Desplegar los resultados formateados en la consola
    print("=== Información Principal del Track ===")
    print(f"Canción    : {nombre_cancion}")
    print(f"Intérprete : {nombre_artista}")
    print(f"Disco      : {nombre_album}")
    print(f"Duración   : {tiempo_segundos:.2f} segundos")

# Bloque de ejecución principal
mostrar_detalles_pista("Fly Me To The Moon.mp3")
