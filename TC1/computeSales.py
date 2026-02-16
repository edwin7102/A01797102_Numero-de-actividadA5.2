#!/usr/bin/env python3
"""
Total de ventas desde catálogo de precios y registro de ventas.
"""

import json
import sys
import time
from pathlib import Path

RESULTS_FILENAME = "SalesResults.txt"

if len(sys.argv) != 3:
    print("Lo sentimos, el número de argumentos es incorrecto", file=sys.stderr)
    sys.exit(1)

path_cat = Path(sys.argv[1])
path_sales = Path(sys.argv[2])

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

