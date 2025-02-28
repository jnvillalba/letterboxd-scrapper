from tkinter import Tk
from tkinter.filedialog import askopenfilename

import pandas as pd
from unidecode import unidecode


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
tabla2 = pd.read_excel(archivo_excel, sheet_name="Tabla2")
tabla3 = pd.read_excel(archivo_excel, sheet_name="Tabla3")

# Preprocesar las tablas relacionadas para realizar un merge
tabla2['Valor alcaldia municipio'] = tabla2['Valor alcaldia municipio'].apply(lambda x: unidecode(x).lower())

# Merge de tablas para obtener las llaves relacionadas
tabla1['Alcaldía/Municipio'] = tabla1['Alcaldía/Municipio'].apply(lambda x: unidecode(x).lower())
tabla1 = tabla1.merge(tabla2[['Valor alcaldia municipio', 'Llave']], left_on='Alcaldía/Municipio',
                      right_on='Valor alcaldia municipio', how='left')
tabla1 = tabla1.merge(tabla3[['Valor estado', 'Llave']], left_on='Estado', right_on='Valor estado', how='left',
                      suffixes=('_alcaldia', '_estado'))

# Crear la tabla de resultado con la estructura deseada
resultado = []

# Iterar sobre las filas de tabla1 para generar la salida
for index, row in tabla1.iterrows():
    nueva_fila = {
        "Llave": row["d_codigo"],
        "Valor": row["d_codigo"],
        "catalogorelacionado1": "",
        "llaverelacionada1": row["Colonia"],
        "catalogorelacionado2": "CTD12008",
        "llaverelacionada2": row["Llave_alcaldia"] if pd.notna(row["Llave_alcaldia"]) else "None",
        "catalogorelacionado3": "CTD12005",
        "llaverelacionada3": row["Llave_estado"] if pd.notna(row["Llave_estado"]) else "None",
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
resultado_df.to_excel("resultado_cp_con_keys.xlsx", index=False)

print("El archivo resultado.xlsx ha sido generado.")
