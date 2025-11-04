import os

def generar_arbol_limpio(ruta_raiz):
    """
    Genera una representación en árbol de la estructura del proyecto,
    ignorando carpetas de entorno virtual y otros archivos generados.
    """
    ignorar = [
        '__pycache__', '.git', '.vscode', '.idea',
        'venv', 'env', '.venv', 'Lib', 'Scripts', 'include', 'lib',
        'node_modules',
        'db.sqlite3',
        'listar_archivos.py',
        'estructura_proyecto.txt' # Ignorar el propio archivo de salida
    ]

    # Imprime el nombre de la carpeta raíz sin emoji
    print(f"{os.path.basename(os.path.abspath(ruta_raiz))}/")
    _recorrer_directorio(ruta_raiz, prefix="", ignorar=set(ignorar))

def _recorrer_directorio(directorio, prefix, ignorar):
    """Función auxiliar recursiva para recorrer los directorios."""
    try:
        elementos = sorted([e for e in os.listdir(directorio) if e not in ignorar])
    except FileNotFoundError:
        return

    punteros = ['|-- '] * (len(elementos) - 1) + ['`-- ']

    for puntero, nombre_elemento in zip(punteros, elementos):
        ruta_completa = os.path.join(directorio, nombre_elemento)
        print(f"{prefix}{puntero}", end="")

        if os.path.isdir(ruta_completa):
            # Imprime directorios sin emoji
            print(f"{nombre_elemento}/")
            extension = '|   ' if puntero == '|-- ' else '    '
            _recorrer_directorio(ruta_completa, prefix=prefix + extension, ignorar=ignorar)
        else:
            # Imprime archivos sin emoji
            print(f"{nombre_elemento}")

if __name__ == '__main__':
    directorio_del_proyecto = '.'
    generar_arbol_limpio(directorio_del_proyecto)