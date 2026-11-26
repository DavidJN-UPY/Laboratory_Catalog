# Fotos de los equipos

Fotos de los modelos reales del inventario del Laboratorio de PCB, proporcionadas por el equipo (Team 1).

Cada archivo se llama igual que el **código interno** del equipo (`<internal_code>.jpg`) y aparece en las fichas del frontend HTML y de Streamlit.

| Archivo | Equipo | Archivo original |
|---|---|---|
| `LAB-GEN-01.jpg` | Generador de RF y Audio – BK Precision 2005B | `2005b_image_1.jpg` |
| `LAB-SCR-01.jpg` | Pantalla HD 50" – LG 49UK6250PUB | `PANTALLA_LG.jpeg` |
| `LAB-GEN-02.jpg` | Generador de Funciones Arbitrario – Instek AFG-2105 | `AFG-2105.webp` |
| `LAB-PSU-01.jpg` | Fuente de Alimentación DC – Instek GPS-3303 | `GPS-3303.webp` |
| `LAB-PC-01.jpg` | Computadora de Escritorio – Dell OptiPlex 3060 | `COMPUTADORA_DELL.avif` |
| `LAB-BRD-01.jpg` | Pintarrón 240 x 90 cm – ESCO | `PINTARRON_BLANCO.webp` |
| `LAB-OSC-01.jpg` | Osciloscopio Digital – Tektronix TBS1032B | `TBS 1032B.jpeg` |
| `LAB-SCR-02.jpg` | Pantalla de Proyección Motorizada | `PANTALLA_PROYECTOR.jpg` |

## Agregar la foto de un equipo nuevo

1. Guarda la imagen como `frontend/img/<internal_code>.jpg` (máximo ~800 px).
2. Añade su entrada en `credits.json`:
   ```json
   "LAB-XXX-01": {"file": "LAB-XXX-01.jpg", "original": "nombre_original.jpg", "source": "Foto del equipo"}
   ```
