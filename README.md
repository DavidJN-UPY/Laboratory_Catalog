# Laboratory Catalog – Laboratorio de Manufactura de PCB

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistema de inventario para los equipos del **Laboratorio de Manufactura de PCB** de la Universidad Politécnica de Yucatán (UPY). Tiene estas partes:

* **Base de datos PostgreSQL** con categorías, ubicaciones físicas, usuarios, equipos e historial de cambios.
* **API REST (FastAPI)** para consultar, crear y editar equipos.
* **Frontend web (HTML)**, servido por la misma API.
* **Frontend Streamlit** con resumen, catálogo, búsqueda, filtros, formulario de alta/edición e historial.

```text
   Navegador ──► http://127.0.0.1:8000  (HTML)  ─┐
                                                 ├──► API FastAPI :8000 ──► PostgreSQL :5432
   Navegador ──► http://127.0.0.1:8501 (Streamlit)┘
```

---

## 👥 Equipo de Trabajo (Team 1)

* **Product Owner:** Didier Gamboa Angulo
* **Scrum Master:** David Juárez Nava (ID: 2509215)
* **Development Team:**
  * David Juárez Nava (ID: 2509215)
  * Gener Daniel Pacheco Moo (ID: 2509219)
  * Jovanhy Alejandro Solis Escamilla (ID: 2409224)
  * Jose Alejandro Juarez Pacheco (ID: 2509213)
  * Pedro Enrique Alonzo Jimenez (ID: 2509007)

---

## 🛠️ Requisitos

| Herramienta | Versión | Para qué |
|---|---|---|
| [Git](https://git-scm.com/) | cualquiera reciente | Clonar el repositorio |
| [Miniconda](https://docs.conda.io/en/latest/miniconda.html) o Anaconda | — | Entorno de Python 3.11 |
| [PostgreSQL](https://www.postgresql.org/download/) (+ pgAdmin, opcional) | 14 o superior | Base de datos |
| Navegador web | — | Usar los frontends |

> Probado en Windows 10/11. En macOS/Linux los pasos son iguales, solo cambia la forma de copiar archivos (`cp` en lugar de `copy`).

---

## 🚀 Despliegue local paso a paso

### 1. Clonar el repositorio

```bash
git clone https://github.com/DavidJN-UPY/Laboratory_Catalog.git
cd Laboratory_Catalog
```

### 2. Crear y activar el entorno de Python

```bash
conda env create -f environment.yml
conda activate dbman
```

> Si ya tienes el entorno y solo hay que actualizar dependencias: `pip install -r requirements.txt`.
> Sin conda: `python -m venv .venv`, actívalo y ejecuta `pip install -r requirements.txt`.

### 3. Crear la base de datos en PostgreSQL

En pgAdmin (o en `psql`) crea una base de datos vacía, por ejemplo:

```sql
CREATE DATABASE lab_catalog;
```

### 4. Configurar tu conexión (`.env`)

Copia la plantilla y edítala con **tus** datos de PostgreSQL:

```bash
copy .env.example .env      # Windows
# cp .env.example .env      # macOS / Linux
```

```ini
DB_HOST=localhost
DB_PORT=5432
DB_NAME=lab_catalog
DB_USER=postgres
DB_PASSWORD=tu_contraseña
```

> El `.env` es personal y **no se sube a GitHub** (está en `.gitignore`). Cada integrante usa el suyo.

### 5. Crear las tablas y cargar los datos de ejemplo

Desde la raíz del proyecto:

```bash
python scripts/test_connection.py    # Verifica que Python llega a PostgreSQL
python scripts/create_schema.py      # Crea las tablas (sql/01_create_tables.sql)
python scripts/import_csv.py         # Carga los CSV de la carpeta data/
python scripts/verify_database.py    # Comprueba conteos y relaciones
```

> ¿Quieres empezar de cero? Ejecuta `sql/00_reset_demo.sql` en pgAdmin (**borra todas las tablas**) y repite este paso.
> `sql/02_validate_data.sql` tiene consultas extra de validación para pgAdmin.

### 6. Levantar la API (terminal 1)

```bash
uvicorn api.main:app --reload --port 8000
```

| URL | Qué es |
|---|---|
| http://127.0.0.1:8000 | Frontend HTML |
| http://127.0.0.1:8000/docs | Documentación interactiva de la API (Swagger) |

### 7. Levantar Streamlit (terminal 2)

Con el entorno activado y **desde la raíz del proyecto**, para que se lea `.streamlit/config.toml`:

```bash
streamlit run frontend/app.py
```

Abre http://127.0.0.1:8501. La barra lateral debe decir **🟢 API conectada**.

> También existe un explorador alternativo: `streamlit run app/lab_catalog.py`.

---

## 🔌 Puertos y configuración

| Servicio | Puerto | Dónde se configura |
|---|---|---|
| PostgreSQL | 5432 | `.env` (`DB_PORT`) |
| API + HTML | 8000 | parámetro `--port` de `uvicorn` |
| Streamlit | 8501 | `.streamlit/config.toml` |

* **Si la API corre en otro puerto:**
  * Streamlit: define la variable `API_BASE_URL` antes de arrancar (`set API_BASE_URL=http://127.0.0.1:9000` en Windows, `export API_BASE_URL=...` en macOS/Linux).
  * HTML: abre la página con `?api=http://127.0.0.1:9000`.
* **El HTML también se puede abrir aparte** (doble clic o Live Server). En ese caso usa la API en `http://127.0.0.1:8000`, que lo permite vía CORS.

---

## 📡 Endpoints de la API

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Frontend HTML |
| GET | `/categories` | Lista de categorías |
| GET | `/physical-locations` | Lista de ubicaciones |
| GET | `/users` | Lista de usuarios |
| GET | `/catalog-items` | Lista de equipos |
| POST | `/catalog-items` | Crea un equipo (si no envías `internal_code`, se genera automáticamente) |
| PUT | `/catalog-items/{item_id}` | Actualiza un equipo |
| GET | `/audit-logs` | Historial de cambios |

---

## 🧪 Pruebas

```bash
# Solo lectura (no modifica tu base de datos)
pytest tests -k "not create and not update"

# Suite completa: crea y edita registros en tu base local
pytest tests
```

* `tests/test_books_client.py` usa `TestClient` (no necesita la API encendida).
* `tests/test_books_http.py` hace peticiones reales: **requiere la API encendida** en el puerto 8000.
* Las evidencias y reportes de testing están en [`docs/evidencia/`](docs/evidencia/).

---

## 📁 Estructura del repositorio

```text
Laboratory_Catalog/
├── api/
│   └── main.py               # API FastAPI (también sirve el HTML)
├── app/
│   └── lab_catalog.py        # Explorador Streamlit alternativo
├── frontend/
│   ├── app.py                # Frontend Streamlit principal
│   └── index.html            # Frontend web (HTML + JS)
├── .streamlit/
│   └── config.toml           # Puerto (8501) y tema de Streamlit
├── data/                     # CSV con los datos de ejemplo
├── sql/
│   ├── 00_reset_demo.sql     # Borra las tablas (opcional, destructivo)
│   ├── 01_create_tables.sql  # Esquema y relaciones
│   └── 02_validate_data.sql  # Consultas de validación
├── scripts/
│   ├── db_config.py          # Conexión a PostgreSQL desde .env
│   ├── test_connection.py
│   ├── create_schema.py
│   ├── import_csv.py
│   └── verify_database.py
├── tests/                    # Pruebas con pytest
├── docs/evidencia/           # Capturas, reportes y evidencias de testing
├── .env.example              # Plantilla de configuración
├── environment.yml           # Entorno conda (dbman)
├── requirements.txt          # Dependencias de Python
├── LICENSE                   # Licencia MIT
└── README.md
```

---

## 🩺 Solución de problemas

| Problema | Solución |
|---|---|
| `RuntimeError: Missing .env settings` | No existe `.env` o le faltan variables. Revisa el paso 4. |
| `password authentication failed` / `connection refused` | Revisa usuario, contraseña y puerto en `.env`, y que el servicio de PostgreSQL esté iniciado. |
| `Table '...' is missing. Run create_schema.py` | Ejecuta `python scripts/create_schema.py` antes de importar. |
| `duplicate key value` al importar | Los datos ya estaban cargados. Usa `sql/00_reset_demo.sql` si quieres recargarlos. |
| Streamlit dice "API desconectada" | Enciende la API (paso 6) y presiona «Reintentar». |
| `Port 8000/8501 is already in use` | Ya hay otra instancia corriendo. Ciérrala o usa otro puerto (ver *Puertos y configuración*). |
| `ModuleNotFoundError` | Activa el entorno (`conda activate dbman`) y ejecuta `pip install -r requirements.txt`. |

---

## 📄 Licencia

Este proyecto se distribuye bajo la **Licencia MIT**. Consulta el archivo [LICENSE](LICENSE) para ver el texto completo.
