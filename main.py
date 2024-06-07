import tkinter as tk
from tkinter import filedialog
import pandas as pd
import re
def encontrar_titulos_con_runs(archivo):
    try:
        titulos_con_runs = []
        with open(archivo, 'r') as f:
            contenido = f.read()
            matches = re.findall(r'<a[^>]+?title="([^"]+?)"', contenido)
            titulos_con_runs = [match.replace("\\u0026", "&").replace("▶️", "").replace("⚽️", "") for match in matches if match not in palabras_a_eliminar]
        palabras_clave = ['Inicio', 'Shorts', 'Suscripciones', 'Tú']
        indices = [titulos_con_runs[::-1].index(palabra) for palabra in palabras_clave]
        indice_maximo = len(titulos_con_runs) - max(indices) - 1

        # Elimina los elementos antes del índice máximo
        titulos_con_runs = titulos_con_runs[indice_maximo + 1:]

        # Elimina las palabras clave también
        titulos_con_runs = [titulo for titulo in titulos_con_runs if titulo not in palabras_clave]

        return titulos_con_runs
    except ValueError:
        return titulos_con_runs

class Jugador:
    def __init__(self, nombre, paises, posicion):
        self.nombre = nombre
        self.paises = paises
        self.posicion = posicion

def convertir_a_objetos(lista, simbolos_paises):
    jugadores = []
    for elemento in lista:
        paises_encontrados = []
        for simbolo in simbolos_paises:
            if simbolo in elemento:
                partes = elemento.split(simbolo)
                nombre = partes[0].strip()
                pais = simbolo
                paises_encontrados.append(pais)
                # Eliminar símbolos de posición si están presentes
                posicion = partes[1].strip()
                # Eliminar símbolos de posición de simbolos_sum si están presentes
                for simbolo_posicion in simbolos_sum:
                    posicion = posicion.replace(simbolo_posicion, '')
                # Eliminar 'hd' si está presente
                posicion = posicion.replace('ᴴᴰ', '')
        if paises_encontrados:  # Solo si se encontró al menos un país
            jugador = Jugador(nombre, paises_encontrados, posicion)
            jugadores.append(jugador)

    return jugadores


# Símbolos de países de Europa
simbolos_paises_europa = ['🇦🇱', '🇦🇩', '🇦🇹', '🇧🇾', '🇧🇪', '🇧🇦', '🇧🇬', '🇭🇷', '🇨🇾', '🇨🇿', '🇩🇰', '🇪🇪', '🇫🇮', '🇫🇷', '🇩🇪', '🇬🇷', '🇭🇺', '🇮🇸', '🇮🇪', '🇮🇹', '🇽🇰', '🇱🇻', '🇱🇮', '🇱🇹', '🇱🇺', '🇲🇰', '🇲🇹', '🇲🇩', '🇲🇪', '🇳🇱', '🇳🇴', '🇵🇱', '🇵🇹', '🇷🇴', '🇷🇸', '🇸🇰', '🇸🇮', '🇪🇸', '🇸🇪', '🇨🇭', '🇺🇦', '🇬🇧']

# Símbolos de países de América
simbolos_paises_america = ['🇦🇬', '🇦🇷', '🇧🇸', '🇧🇧', '🇧🇿', '🇧🇴', '🇧🇷', '🇨🇦', '🇨🇱', '🇨🇴', '🇨🇷', '🇨🇺', '🇩🇲', '🇩🇴', '🇪🇨', '🇸🇻', '🇬🇶', '🇬🇹', '🇬🇾', '🇭🇹', '🇭🇳', '🇯🇲', '🇲🇽', '🇳🇮', '🇵🇦', '🇵🇾', '🇵🇪', '🇵🇷', '🇰🇳', '🇱🇨', '🇻🇨', '🇸🇷', '🇹🇹', '🇺🇸', '🇺🇾', '🇻🇪']

simbolos_paises_africa = ['🇲🇱''🇩🇿', '🇦🇴', '🇧🇯', '🇧🇼', '🇧🇫', '🇧🇮', '🇨🇲', '🇨🇻', '🇨🇫', '🇹🇩', '🇨🇬', '🇨🇮', '🇩🇯', '🇪🇬', '🇬🇶', '🇪🇷', '🇪🇹', '🇬🇦', '🇬🇲', '🇬🇭', '🇬🇳', '🇬🇼', '🇰🇪', '🇱🇸', '🇱🇷', '🇱🇾', '🇲🇬', '🇲🇼', '🇲🇱', '🇲🇷', '🇲🇺', '🇲🇿', '🇳🇦', '🇳🇪', '🇳🇬', '🇷🇼', '🇸🇭', '🇸🇱', '🇸🇴', '🇿🇦', '🇸🇸', '🇱🇰', '🇸🇩', '🇸🇿', '🇹🇿', '🇹🇬', '🇹🇳', '🇺🇬', '🇿🇲', '🇿🇼']


# Combinamos todas las listas de símbolos de países
simbolos_sum = simbolos_paises_europa + simbolos_paises_america +simbolos_paises_africa


palabras_a_eliminar = ['Enlace de vídeo compartido', 'Siguiente&nbsp;(SHIFT+n)','Denunciar esta lista','Configuración de la lista de reproducción', 'Eliminar lista de reproducción', 'Descripción', 'Subir vídeo', 'Emitir en directo', 'Combinaciones de teclas', 'Reproducción', 'General', 'Subtítulos', 'Vídeos esféricos', 'Configuración de la lista de reproducción', 'Eliminar lista de reproducción']

def generar_excel(archivo):
    # Encontrar los títulos con las corridas
    titulos_con_runs = encontrar_titulos_con_runs(archivo)

    # Convertir los títulos a objetos de jugador
    objetos_jugadores = convertir_a_objetos(titulos_con_runs, simbolos_sum)

    # Crear un DataFrame con los datos de los jugadores
    data = {
        'Nombre': [jugador.nombre for jugador in objetos_jugadores],
        'Países': [', '.join(jugador.paises) for jugador in objetos_jugadores],
        'Posición': [jugador.posicion for jugador in objetos_jugadores]
    }
    df = pd.DataFrame(data)

    # Permitir al usuario elegir dónde guardar el archivo Excel
    ruta_guardado = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Archivos de Excel", "*.xlsx")])
    if ruta_guardado:
        # Guardar el DataFrame en un archivo Excel
        df.to_excel(ruta_guardado, index=False)
        print(f'Se ha guardado el archivo Excel como "{ruta_guardado}"')

def seleccionar_archivo():
    ruta_archivo = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt")])
    if ruta_archivo:
        generar_excel(ruta_archivo)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Generador de Excel")

    # Botón para seleccionar el archivo
    btn_seleccionar_archivo = tk.Button(root, text="Seleccionar Archivo de Texto", command=seleccionar_archivo)
    btn_seleccionar_archivo.pack(pady=10)

    root.mainloop()



