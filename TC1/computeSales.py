#!/usr/bin/env python3
# pylint: disable=invalid-name
"""
Total de ventas desde catálogo de precios y registro de ventas.
Nombre del archivo computeSales definido por requerimientos.
"""

import json
import sys
import time
from pathlib import Path

# Ruta del archivo de resultados
SCRIPT_DIR = Path(__file__).resolve().parent
RESULTS_FILENAME = SCRIPT_DIR / "SalesResults.txt"

if len(sys.argv) != 3:
    print("Lo sentimos, número de argumentos incorrecto", file=sys.stderr)
    sys.exit(1)

path_cat = SCRIPT_DIR / sys.argv[1]
path_sales = SCRIPT_DIR / sys.argv[2]

start_time = time.perf_counter()
console_errors = []

# Catálogo de precios
if not path_cat.exists():
    print(f"No fue posible encontrar el archivo: {path_cat}", file=sys.stderr)
    sys.exit(1)
try:
    with open(path_cat, "r", encoding="utf-8") as f:
        raw_catalogue = json.load(f)
except json.JSONDecodeError as e:
    print(f"Formato del archivo de precios no es válido: {e}", file=sys.stderr)
    sys.exit(1)
except OSError as e:
    print(f"No fue posible leer el archivo del precios: {e}", file=sys.stderr)
    sys.exit(1)

catalogue = {}
if not isinstance(raw_catalogue, list):
    print("El formato del catálogo de precios no válido.", file=sys.stderr)
    sys.exit(1)
for i, item in enumerate(raw_catalogue):
    if not isinstance(item, dict):
        console_errors.append(f"Formato de precio del objeto {i} no válido.")
        continue
    name = item.get("title") or item.get("Product")
    price = item.get("price")
    if name is None:
        console_errors.append(f"No se encontró el nombre del producto {i}.")
        continue
    if price is None:
        console_errors.append(f"No se encontró el precio del producto {i}")
        continue
    try:
        price_float = float(price)
    except (TypeError, ValueError):
        console_errors.append(f"Precio no válido para el producto {i}.")
        continue
    if price_float < 0:
        console_errors.append(f"El precio del producto {i} es negativo.")
        continue
    catalogue[str(name).strip()] = price_float
if not catalogue:
    print("Producto no encontrado en el catálogo de precios.", file=sys.stderr)
    sys.exit(1)

# Registro de ventas
if not path_sales.exists():
    print(f"No se encontró el archivo: {path_sales}", file=sys.stderr)
    sys.exit(1)
try:
    with open(path_sales, "r", encoding="utf-8") as f:
        sales_data = json.load(f)
except json.JSONDecodeError as e:
    print(f"Formato del JSON de ventas no válido: {e}", file=sys.stderr)
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
            console_errors.append("Producto ausente en registro de ventas.")
            continue
        if quantity is None:
            console_errors.append("Cantidad ausente en el registro de ventas.")
            continue
        try:
            qty = int(quantity)
        except (TypeError, ValueError):
            console_errors.append("Cantidad no válida para el producto.")
            continue
        if qty < 0:
            console_errors.append("Cantidad de ventas no puede ser negativa.")
            continue
        product_key = str(product).strip()
        if product_key not in catalogue:
            console_errors.append("El código del producto no es válido.")
            continue
        total += catalogue[product_key] * qty

elapsed = time.perf_counter() - start_time
report = f"Monto de ventas: {total:,.2f}\nTiempo de ejecución: {elapsed:.4f} s"

if console_errors:
    print("Ejecución continúa con errores.", file=sys.stderr)
    for msg in console_errors:
        print(f"  - {msg}", file=sys.stderr)
    print("", file=sys.stderr)

print(report, flush=True)
try:
    with open(RESULTS_FILENAME, "w", encoding="utf-8") as f:
        f.write(report)
    print("Los resultados han sido almacenados correctamente", flush=True)
except OSError as e:
    print(f"No fue posible almacenar los resultados: {e}", file=sys.stderr)

sys.exit(0)
