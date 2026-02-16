#!/usr/bin/env python3
"""
Total de ventas desde catálogo de precios y registro de ventas.
"""

import json
import sys
import time
from pathlib import Path

# Ruta del archivo de resultados: misma carpeta que este script
SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_FILENAME = SCRIPT_DIR / "SalesResults.txt"

if len(sys.argv) != 3:
    print("Lo sentimos, el número de argumentos es incorrecto", file=sys.stderr)
    sys.exit(1)

path_cat = SCRIPT_DIR / sys.argv[1]
path_sales = SCRIPT_DIR / sys.argv[2]

start_time = time.perf_counter()
console_errors = []

# Catálogo de precios
if not path_cat.exists():
    print(f"Error: No fue posible encontrar el archivo: {path_cat}", file=sys.stderr)
    sys.exit(1)
try:
    with open(path_cat, "r", encoding="utf-8") as f:
        raw_catalogue = json.load(f)
except json.JSONDecodeError as e:
    print(f"Error: El formato del precio del producto no es válido: {e}", file=sys.stderr)
    sys.exit(1)
except OSError as e:
    print(f"Error: No fue posible leer el archivo del precio del producto: {e}", file=sys.stderr)
    sys.exit(1)

catalogue = {}
if not isinstance(raw_catalogue, list):
    print("Error: El formato del catálogo de precios no es válido.", file=sys.stderr)
    sys.exit(1)
for i, item in enumerate(raw_catalogue):
    if not isinstance(item, dict):
        console_errors.append(f"El formato del item {i} del catálogo de precios no es válido.")
        continue
    name = item.get("title") or item.get("Product")
    price = item.get("price")
    if name is None:
        console_errors.append(f"No se encontró el nombre del producto {i} del catálogo de precios.")
        continue
    if price is None:
        console_errors.append(f"No se encontró el precio del producto {i} del catálogo de precios.")
        continue
    try:
        price_float = float(price)
    except (TypeError, ValueError):
        console_errors.append(f"Precio no válido para el producto {i} del catálogo de precios.")
        continue
    if price_float < 0:
        console_errors.append(f"El precio del producto {i} no puede ser negativo.")
        continue
    catalogue[str(name).strip()] = price_float
if not catalogue:
    print("Producto no encontrado en el catálogo de precios.", file=sys.stderr)
    sys.exit(1)

# Registro de ventas
if not path_sales.exists():
    print(f"Lo sentimos, no se encontró el archivo: {path_sales}", file=sys.stderr)
    sys.exit(1)
try:
    with open(path_sales, "r", encoding="utf-8") as f:
        sales_data = json.load(f)
except json.JSONDecodeError as e:
    print(f"Formato del JSON del registro de ventas no es válido: {e}", file=sys.stderr)
    sys.exit(1)
except OSError as e:
    print(f"No fue posible leer el registro de ventas: {e}", file=sys.stderr)
    sys.exit(1)

# Calcular total de ventas
total = 0.0
if not isinstance(sales_data, list):
    console_errors.append("El formato de registro de ventas no es válido.")
else:
    for i, record in enumerate(sales_data):
        if not isinstance(record, dict):
            console_errors.append(
                f"Formato del registro de ventas {i} no es válido."
            )
            continue
        product = record.get("Product")
        quantity = record.get("Quantity")
        if product is None:
            console_errors.append(f"No se encontró el producto en el registro de ventas.")
            continue
        if quantity is None:
            console_errors.append(f"No se encontró la cantidad en el registro de ventas.")
            continue
        try:
            qty = int(quantity)
        except (TypeError, ValueError):
            console_errors.append(
                f"Cantidad no válida para el producto."
            )
            continue
        if qty < 0:
            console_errors.append(f"La cantidad de ventas no puede ser negativa.")
            continue
        product_key = str(product).strip()
        if product_key not in catalogue:
            console_errors.append(f"El código del producto no es válido.")
            continue
        total += catalogue[product_key] * qty

elapsed = time.perf_counter() - start_time
report = f"Monto total de ventas: {total:,.2f}\nTiempo de ejecución: {elapsed:.4f} s"

if console_errors:
    print("Se encontraron errores pero se continuará con la ejecución.", file=sys.stderr)
    for msg in console_errors:
        print(f"  - {msg}", file=sys.stderr)
    print("", file=sys.stderr)

print(report, flush=True)
try:
    with open(RESULTS_FILENAME, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Los resultados han sido almacenados correctamente", flush=True)
except OSError as e:
    print(f"Lo sentimos, no fue posible almacenar los resultados: {e}", file=sys.stderr)

sys.exit(0)
