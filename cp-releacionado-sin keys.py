from tkinter import Tk
from tkinter.filedialog import askopenfilename

import pandas as pd


# Función para seleccionar el archivo Excel
def seleccionar_archivo():
    Tk().withdraw()
    archivo = askopenfilename(
        title="Selecciona el archivo Excel",
        filetypes=[("Archivos de Excel", "*.xlsx *.xls")]
    )
    return archivo


# Seleccionar el archivo Excel
archivo_excel = seleccionar_archivo()
if not archivo_excel:
    print("No seleccionaste ningún archivo. Saliendo del programa.")
    exit()

# Leer las tablas desde el archivo seleccionado
tabla1 = pd.read_excel(archivo_excel, sheet_name="Tabla1")

# Crear la tabla de resultado con la estructura deseada
resultado = []

# Iterar sobre las filas de tabla1 para generar la salida
for index, row in tabla1.iterrows():
    nueva_fila = {
        "Llave": index + 1,
        "Valor": row["d_codigo"],
        "catalogorelacionado1": "",
        "llaverelacionada1": row["Colonia"],
        "catalogorelacionado2": "",
        "llaverelacionada2": row["Alcaldía/Municipio"],
        "catalogorelacionado3": "",
        "llaverelacionada3": row["Estado"],
        "catalogorelacionado4": "",
        "llaverelacionada4": "",
        "catalogorelacionado5": "",
        "llaverelacionada5": "",
        "Orden": index + 1
    }
    resultado.append(nueva_fila)
    print(f"Procesado: {row["d_codigo"]}")

# Convertir la lista de diccionarios a un DataFrame
resultado_df = pd.DataFrame(resultado)

# Guardar el resultado en un archivo Excel
resultado_df.to_excel("resultado_cp_sin_keys.xlsx", index=False)

print("El archivo resultado.xlsx ha sido generado.")
