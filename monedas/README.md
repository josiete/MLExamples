# Captura de monedas con Nikon D60

CLI de adquisición para el proyecto Monedas. Cada disparo descarga la imagen mediante `gphoto2` y genera un JSON con mediciones y anotaciones. No entrena todavía el modelo ni detecta monedas: conserva los datos de entrada para esa fase posterior.

## Requisitos y uso

Python 3.10+ y `gphoto2` instalado. En Ubuntu: `sudo apt install gphoto2`. Conecta la Nikon D60 por USB, enciéndela y comprueba `gphoto2 --auto-detect`. Cierra aplicaciones que estén usando la cámara. Desde la raíz del repositorio:

```bash
python3 monedas/capture.py --output ./capturas
```

Se solicita antes de **cada foto** la hipotenusa, el cateto horizontal, la focal, el número de monedas, una etiqueta libre y una descripción. Intro conserva el valor anterior; `:q`, `:quit`, `:salir` o Ctrl+C terminan. Antes del disparo, `r` permite corregir. Los últimos valores confirmados se guardan en `capturas/.session-defaults.json` y se recuperan al reiniciar; un disparo fallido no los actualiza. Cada toma produce `ID.jpg` (y otros formatos si los descarga la cámara) y `ID.json` en la misma carpeta. El JSON contiene el nombre exacto de las imágenes, identificadores de sesión y toma, UTC, dimensiones del tablero, medidas, ángulo estimado y anotación. No guardes secretos en las descripciones.

Las distancias se introducen en **milímetros**: hipotenusa de la cámara al punto enfocado, y cateto horizontal desde la proyección vertical del centro óptico de la cámara sobre el plano hasta ese punto. El ángulo con el plano se calcula como `acos(cateto / hipotenusa)`. Medir desde la base física del trípode puede introducir un error si esa base no coincide con la proyección del centro óptico. La focal manual se registra como dato declarado: para análisis geométrico fiable conviene contrastarla con EXIF y calibrar la cámara con el tablero ChArUco. La focal por sí sola no determina el tamaño de una moneda en píxeles. Se supone un tablero de 600 × 400 mm con cuadrados de 40 mm; la identificación exacta del diccionario y los marcadores ChArUco deberán añadirse cuando se fije el patrón impreso.

Una etiqueta libre como `España | 1 euro` sirve para una serie homogénea. En fotos mixtas o con monedas parcialmente tapadas, usa `mixto` y describe la escena; el recuento y la etiqueta no equivalen a anotaciones individuales con cajas o máscaras. Esas anotaciones serán necesarias para entrenar y evaluar detección por instancia.

Las fotografías, JSON y `.session-defaults.json` contienen datos de la colección: conserva `capturas/` fuera del repositorio o añádelo a `.gitignore` antes de versionar imágenes.
