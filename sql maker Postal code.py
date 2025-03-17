import logging
import os
import sys
import tkinter as tk
from datetime import datetime
from tkinter import filedialog

import pandas as pd

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('excel_to_sql_converter.log')
    ]
)
logger = logging.getLogger(__name__)


def select_excel_file():
    """
    Muestra un cuadro de diálogo para seleccionar un archivo Excel.

    Returns:
        str: Ruta al archivo seleccionado o None si se canceló
    """
    root = tk.Tk()
    root.withdraw()  # Ocultar la ventana principal de tkinter

    logger.info("Abriendo diálogo para seleccionar archivo Excel...")
    file_path = filedialog.askopenfilename(
        title="Selecciona el archivo Excel",
        filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
    )

    if file_path:
        logger.info(f"Archivo seleccionado: {file_path}")
        return file_path
    else:
        logger.warning("No se seleccionó ningún archivo")
        return None


def excel_to_postgres_inserts(excel_file, sheet_name=0, catalog_id=500038):
    """
    Lee un archivo Excel y genera sentencias INSERT para PostgreSQL.

    Args:
        excel_file (str): Ruta al archivo Excel
        sheet_name: Nombre o índice de la hoja (por defecto 0)
        catalog_id (int): ID del catálogo a insertar (por defecto 500038)

    Returns:
        list: Lista de sentencias INSERT SQL
    """
    logger.info(f"Leyendo archivo Excel: {excel_file}")

    try:
        # Leer el archivo Excel
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        logger.info(f"Excel leído correctamente. {len(df)} filas encontradas.")

        # Verificar si el dataframe tiene las columnas esperadas
        expected_columns = ['Llave', 'Valor', 'Orden']
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            logger.warning(f"Faltan columnas en el Excel: {missing_columns}")

        # Lista para almacenar las sentencias SQL
        inserts = []

        # Procesar cada fila del DataFrame
        total_rows = len(df)
        logger.info(f"Iniciando procesamiento de {total_rows} filas...")

        for index, row in df.iterrows():
            if index % 10 == 0 or index == total_rows - 1:  # Log cada 10 filas o la última
                logger.info(f"Procesando fila {index + 1} de {total_rows} ({(index + 1) / total_rows * 100:.1f}%)")

            # Extraer valores de la fila
            llave = str(row.get('Llave', ''))
            valor = str(row.get('Valor', ''))
            orden = index

            # Manejar valores relacionados correctamente
            va_related_value_1 = f"'{row.get('catalogorelacionado1', '')}'" if pd.notna(
                row.get('catalogorelacionado1', '')) else 'null'
            va_related_value_2 = f"'{row.get('catalogorelacionado2', '')}'" if pd.notna(
                row.get('catalogorelacionado2', '')) else 'null'
            va_related_value_3 = f"'{row.get('catalogorelacionado3', '')}'" if pd.notna(
                row.get('catalogorelacionado3', '')) else 'null'
            va_related_value_4 = f"'{row.get('catalogorelacionado4', '')}'" if pd.notna(
                row.get('catalogorelacionado4', '')) else 'null'
            va_related_value_5 = f"'{row.get('catalogorelacionado5', '')}'" if pd.notna(
                row.get('catalogorelacionado5', '')) else 'null'

            # Dejar va_code_related_catalog_X como null o vacío según se solicita
            va_code_related_catalog_1 = 'null'
            va_code_related_catalog_2 = 'null'
            va_code_related_catalog_3 = 'null'
            va_code_related_catalog_4 = 'null'
            va_code_related_catalog_5 = 'null'

            # INFO: poner el ultimo de la tabla values
            nm_catalog_value_id = 516000 + index

            # INFO: el del POSTAL_CODE activo
            catalog_id = 500038

            # Crear la sentencia INSERT
            insert_sql = f"""insert into public.amp_catalog_values (
                nm_catalog_value_id, va_code_related_catalog_1, va_code_related_catalog_2, 
                va_code_related_catalog_3, va_code_related_catalog_4, va_code_related_catalog_5, 
                va_data_additional_1, va_data_additional_2, va_key, nm_order, 
                va_related_value_1, va_related_value_2, va_related_value_3, va_related_value_4, 
                va_related_value_5, va_value, nm_catalog_id, va_tags
            ) values (
                {nm_catalog_value_id}, {va_code_related_catalog_1}, {va_code_related_catalog_2}, 
                {va_code_related_catalog_3}, {va_code_related_catalog_4}, {va_code_related_catalog_5}, 
                '{{}}', null, '{llave}', {orden}, 
                {va_related_value_1}, {va_related_value_2}, {va_related_value_3}, {va_related_value_4}, 
                {va_related_value_5}, '{valor}', {catalog_id}, null
            );"""

            inserts.append(insert_sql)

        logger.info(f"Procesamiento completo. Se generaron {len(inserts)} sentencias INSERT.")
        return inserts

    except Exception as e:
        logger.error(f"Error al procesar el archivo Excel: {str(e)}")
        return []


def main():
    logger.info("=== Iniciando conversor de Excel a SQL ===")

    # Seleccionar archivo Excel
    excel_file = select_excel_file()
    if not excel_file:
        logger.error("No se seleccionó ningún archivo. Terminando programa.")
        return

    # Generar sentencias INSERT
    logger.info("Iniciando generación de sentencias INSERT...")
    inserts = excel_to_postgres_inserts(excel_file)

    if not inserts:
        logger.error("No se generaron sentencias INSERT. Verificar el archivo Excel.")
        return

    # Crear nombre de archivo con timestamp para evitar sobrescribir archivos anteriores
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"inserts_{timestamp}.sql"

    # Guardar las sentencias en un archivo SQL
    logger.info(f"Guardando sentencias en archivo {output_filename}...")
    with open(output_filename, "w", encoding="utf-8") as f:
        for insert in inserts:
            f.write(insert + "\n")

    logger.info(f"Se generaron {len(inserts)} sentencias INSERT y se guardaron en '{output_filename}'")

    # Mostrar ruta completa al archivo generado
    abs_path = os.path.abspath(output_filename)
    logger.info(f"Ruta completa al archivo: {abs_path}")

    # Mostrar un ejemplo
    if inserts:
        logger.info("Ejemplo de sentencia INSERT generada:")
        logger.info(inserts[0])

    logger.info("=== Programa finalizado ===")


if __name__ == "__main__":
    main()
