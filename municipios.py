import requests
from bs4 import BeautifulSoup

# URL de la página web
URL = 'https://shakacmpny.com.ar/productos/'

# Productos anteriores
previous_products = set()
first_product_title = "FIRST STEPS TEE (gris)"


def check_for_new_products():
    global previous_products, first_product_title

    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Suponiendo que los productos están en contenedores con la clase 'js-item-product'
    products = soup.find_all(class_='js-item-product')

    current_products = {product.get_text().strip() for product in products}

    # Comparar los productos actuales con los anteriores
    new_products = current_products - previous_products

    if new_products:
        print('New products have been added:')
        for product in new_products:
            print(product)
        previous_products = current_products

    # Verificar el título del primer producto
    if products:
        first_product = products[0].find('a', title=True)
        if first_product and first_product['title'] != first_product_title:
            print(f"The first product title has changed: {first_product['title']}")


# Ejecutar el chequeo manualmente
check_for_new_products()
