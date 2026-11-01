# Laboratory Catalog Database (Epic 2)

Sistema de gestión y base de datos relacional para el control de inventario de equipos en el **Laboratorio de Manufactura de PCB** de la Universidad Politécnica de Yucatán (UPY).

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

## 🛠️ Requisitos del Sistema
Asegúrate de tener instaladas las siguientes herramientas en tu entorno de desarrollo (Windows 10/11)[cite: 9]:
* **Git y GitHub** (Control de versiones)
* **Visual Studio Code** (Editor de código)
* **Miniconda / Anaconda** (Entorno virtual de Python)
* **PostgreSQL y pgAdmin** (Servidor de base de datos y cliente gráfico)

---

## 📁 Estructura del Repositorio
```text
Laboratory_Catalog/
├── data/
│   ├── categories.csv
│   ├── physical_locations.csv
│   ├── users.csv
│   ├── catalog_items.csv
│   └── audit_logs.csv
├── sql/
│   ├── 00_reset_demo.sql
│   ├── 01_create_tables.sql
│   └── 02_validate_data.sql
├── scripts/
│   ├── db_config.py
│   ├── test_connection.py
│   ├── create_schema.py
│   ├── import_csv.py
│   └── verify_database.py
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md