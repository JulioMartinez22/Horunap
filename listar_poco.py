import os
import sys

def generar_arbol_con_contenido(ruta_raiz, archivo_salida):
    """
    Genera una representación en árbol de la estructura del proyecto,
    mostrando el contenido de cada archivo y guardándolo en el archivo_salida.
    """
    ignorar = {
        '__pycache__', '.git', '.vscode', '.idea',
        'venv', 'env', '.venv', 'Lib', 'Scripts', 'include', 'lib',
        'node_modules',
        'db.sqlite3',
        'listar_archivos.py', # Puedes poner el nombre de este script aquí
        'estructura_proyecto.txt' # Ignorar el propio archivo de salida
    }

    # Escribe el nombre de la carpeta raíz en el archivo
    print(f"📁 {os.path.basename(os.path.abspath(ruta_raiz))}/", file=archivo_salida)
    _recorrer_directorio(ruta_raiz, prefix="", ignorar=ignorar, archivo_salida=archivo_salida)

def _recorrer_directorio(directorio, prefix, ignorar, archivo_salida):
    """
    Función auxiliar recursiva para recorrer directorios y escribir
    el contenido de los archivos en el archivo_salida.
    """
    try:
        elementos = sorted([e for e in os.listdir(directorio) if e not in ignorar])
    except FileNotFoundError:
        return

    punteros = ['|-- '] * (len(elementos) - 1) + ['`-- ']

    for puntero, nombre_elemento in zip(punteros, elementos):
        ruta_completa = os.path.join(directorio, nombre_elemento)
        
        # Se usa 'end=""' para que print no agregue un salto de línea extra
        print(f"{prefix}{puntero}", end="", file=archivo_salida)

        if os.path.isdir(ruta_completa):
            print(f"📁 {nombre_elemento}/", file=archivo_salida)
            extension = '|   ' if puntero == '|-- ' else '    '
            _recorrer_directorio(ruta_completa, prefix=prefix + extension, ignorar=ignorar, archivo_salida=archivo_salida)
        else:
            print(f"📄 {nombre_elemento}", file=archivo_salida)
            
            content_prefix = prefix + ('|   ' if puntero == '|-- ' else '    ')
            
            try:
                with open(ruta_completa, 'r', encoding='utf-8') as archivo_a_leer:
                    lineas = archivo_a_leer.readlines()
                    if not lineas:
                        print(f"{content_prefix}  (Archivo vacío)", file=archivo_salida)
                    else:
                        print(f"{content_prefix}┌─ CONTENIDO ─┐", file=archivo_salida)
                        for linea in lineas:
                            print(f"{content_prefix}│ {linea.rstrip()}", file=archivo_salida)
                        print(f"{content_prefix}└─────────────┘", file=archivo_salida)
            except Exception:
                print(f"{content_prefix}  (No se pudo leer el contenido, puede ser un archivo binario)", file=archivo_salida)

if __name__ == '__main__':
    directorio_del_proyecto = '.'
    nombre_archivo_salida = 'estructura_completa_proyecto.txt'
    
    print(f"Generando la estructura del proyecto en el archivo '{nombre_archivo_salida}'...")

    # Abrimos el archivo de texto en modo escritura ('w')
    with open(nombre_archivo_salida, 'w', encoding='utf-8') as f:
        # Pasamos el objeto de archivo 'f' a la función principal
        generar_arbol_con_contenido(directorio_del_proyecto, archivo_salida=f)

    print("¡Archivo generado con éxito!")