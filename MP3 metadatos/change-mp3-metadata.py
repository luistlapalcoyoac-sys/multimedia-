from mutagen.id3 import ID3, TIT2, TPE1, TALB
from mutagen.mp3 import MP3

def sobreescribir_etiquetas_audio(ruta_mp3):
    # Cargar el archivo de audio con soporte para lectura y escritura ID3
    pista_audio = MP3(ruta_mp3, ID3=ID3)

    # Actualizar la información básica inyectando nuevas tramas
    pista_audio.tags.add(TIT2(encoding=3, text="Pista 1"))     # Título de la pista
    pista_audio.tags.add(TPE1(encoding=3, text="Artista 1"))    # Intérprete/Artista
    pista_audio.tags.add(TALB(encoding=3, text="Album 1"))   # Nombre del disco

    # Aplicar y consolidar los cambios en el archivo físico
    pista_audio.save()
    print("¡Metadatos de audio actualizados correctamente!")

# Bloque de ejecución principal
archivo_objetivo = "Fly Me To The Moon.mp3"
sobreescribir_etiquetas_audio(archivo_objetivo)
