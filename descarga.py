"""
download_data.py
----------------
Descarga el dataset oficial de direcciones de Madrid (direcciones.csv) desde
el portal de datos abiertos del Ayuntamiento de Madrid.

Uso:
    python download_data.py
"""

import os
import urllib.request

# URL de descarga directa desde datos.madrid.es
URL = "https://datos.madrid.es/egob/catalogo/213605-3-callejero-oficial-madrid.csv"
FICHERO_SALIDA = "direcciones.csv"


def descargar_direcciones(url: str = URL, salida: str = FICHERO_SALIDA) -> None:
    """
    Descarga el fichero CSV de direcciones de Madrid si no existe ya en local.

    Args:
        url (str): URL de descarga del fichero CSV.
        salida (str): Nombre del fichero local donde guardar los datos.
    """
    if os.path.exists(salida):
        print(f"'{salida}' ya existe. No es necesario volver a descargarlo.")
        return

    print(f"Descargando '{salida}' desde:\n  {url}")
    print("Esto puede tardar unos segundos (el fichero pesa ~33 MB)...")

    try:
        urllib.request.urlretrieve(url, salida)
        tamanyo_mb = os.path.getsize(salida) / (1024 * 1024)
        print(f"Descarga completada. Fichero guardado como '{salida}' ({tamanyo_mb:.1f} MB).")
    except Exception as e:
        print(f"Error al descargar el fichero: {e}")
        raise


if __name__ == "__main__":
    descargar_direcciones()
