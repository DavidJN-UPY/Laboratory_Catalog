import streamlit as st
import pandas as pd
import requests

# Configuración de página
st.set_page_config(
    page_title="Catálogo Laboratorio de PCB",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos visuales
st.markdown("""
    <style>
        .block-container {
            padding-top: 1.8rem;
            padding-bottom: 2.5rem;
        }
        .catalog-hero {
            background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%);
            padding: 24px 30px;
            border-radius: 14px;
            color: #ffffff;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.1);
        }
        .catalog-hero h1 {
            color: #ffffff;
            font-size: 1.9rem;
            font-weight: 800;
            letter-spacing: 1px;
            margin: 0;
            text-transform: uppercase;
        }
        .catalog-hero p {
            color: #cfd8dc;
            font-size: 0.95rem;
            margin: 6px 0 0 0;
        }
        .detail-box {
            background-color: rgba(255, 255, 255, 0.05);
            border-left: 4px solid #38bdf8;
            padding: 16px 20px;
            border-radius: 8px;
            margin-top: 1rem;
            margin-bottom: 1rem;
        }
    </style>
""", unsafe_allow_html=True)

# Banner superior
st.markdown("""
    <div class="catalog-hero">
        <h1>Catálogo Laboratorio de PCB</h1>
        <p>Explorador interactivo: selecciona una categoría o ubicación para ver los equipos en detalle</p>
    </div>
""", unsafe_allow_html=True)

API_BASE_URL = "http://127.0.0.1:8000"

with st.sidebar:
    st.markdown("### 🧭 Exploración")
    seccion = st.radio(
        "Navegar desde:",
        options=[
            "🏷️ Familias / Categorías",
            "📍 Ubicaciones en Laboratorio",
            "📦 Catálogo General Completo",
            "📝 Bitácora de Auditoría"
        ],
        index=0
    )
    st.divider()
    api_status = st.empty()

try:
    # Cargar datos base de la API
    with st.spinner("Sincronizando con el catálogo..."):
        res_items = requests.get(f"{API_BASE_URL}/catalog-items", timeout=3)
        res_cats = requests.get(f"{API_BASE_URL}/categories", timeout=3)
        res_locs = requests.get(f"{API_BASE_URL}/physical-locations", timeout=3)

    if res_items.status_code == 200 and res_cats.status_code == 200 and res_locs.status_code == 200:
        api_status.success("🟢 API Conectada")

        df_items = pd.DataFrame(res_items.json())
        df_cats = pd.DataFrame(res_cats.json())
        df_locs = pd.DataFrame(res_locs.json())

        # Mapear nombres legibles de categoría y ubicación en los ítems
        if not df_items.empty:
            cat_name_col = 'name' if 'name' in df_cats.columns else df_cats.columns[1]
            cat_map = dict(zip(df_cats['category_id'], df_cats[cat_name_col]))
            df_items['categoria_nombre'] = df_items['category_id'].map(cat_map)

            loc_name_col = 'name' if 'name' in df_locs.columns else df_locs.columns[1]
            loc_map = dict(zip(df_locs['location_id'], df_locs[loc_name_col]))
            df_items['ubicacion_nombre'] = df_items['location_id'].map(loc_map)

        # KPIs superiores
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Equipos Registrados", len(df_items))
        c2.metric("Categorías", len(df_cats))
        c3.metric("Ubicaciones Físicas", len(df_locs))
        c4.metric("Modo", seccion.split(" ", 1)[1])
        st.divider()

        # ==========================================
        # 1. DEDUCTIVO POR CATEGORÍA
        # ==========================================
        if seccion == "🏷️ Familias / Categorías":
            st.markdown("### 1. Nivel General: Categorías de Equipos")
            st.caption("👉 **Haz clic en cualquier fila** de la tabla para ver todos los equipos correspondientes a esa categoría:")

            search_cat = st.text_input("🔍 Filtrar categorías:", placeholder="Ej. Medición, Computo...")
            cats_display = df_cats.copy()
            if search_cat:
                mask = cats_display.astype(str).apply(lambda r: r.str.contains(search_cat, case=False, na=False)).any(axis=1)
                cats_display = cats_display[mask]

            # Tabla interactiva con selección de fila
            event_cat = st.dataframe(
                cats_display,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )

            selected_rows = event_cat.selection.rows if hasattr(event_cat, "selection") else []
            
            if selected_rows:
                selected_idx = selected_rows[0]
                selected_cat_id = cats_display.iloc[selected_idx]['category_id']
                cat_nombre = cats_display.iloc[selected_idx][cat_name_col]

                st.markdown(f"""
                <div class="detail-box">
                    <h3>2. Nivel Particular: Equipos en «{cat_nombre}»</h3>
                    <p>Listado de equipos pertenecientes a esta categoría específica.</p>
                </div>
                """, unsafe_allow_html=True)

                items_filtrados = df_items[df_items['category_id'] == selected_cat_id]

                if not items_filtrados.empty:
                    # Selección de equipo particular para ver detalles
                    st.caption("👉 Haz clic sobre un equipo específico para ver su ficha técnica:")
                    event_item = st.dataframe(
                        items_filtrados,
                        use_container_width=True,
                        hide_index=True,
                        on_select="rerun",
                        selection_mode="single-row"
                    )

                    item_selected_rows = event_item.selection.rows if hasattr(event_item, "selection") else []
                    if item_selected_rows:
                        item_data = items_filtrados.iloc[item_selected_rows[0]]
                        st.success(f"📌 **Ficha Técnica Detallada:** {item_data.get('name', item_data.get('item_name', 'Equipo'))}")
                        st.json(item_data.to_dict())
                else:
                    st.info("No hay equipos asignados a esta categoría todavía.")
            else:
                st.info("👆 Selecciona una categoría arriba para desplegar sus equipos.")

        # ==========================================
        # 2. DEDUCTIVO POR UBICACIÓN
        # ==========================================
        elif seccion == "📍 Ubicaciones en Laboratorio":
            st.markdown("### 1. Nivel General: Ubicaciones en Laboratorio")
            st.caption("👉 **Haz clic en cualquier ubicación** para ver qué equipos e instrumentos están ahí almacenados:")

            event_loc = st.dataframe(
                df_locs,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )

            selected_loc_rows = event_loc.selection.rows if hasattr(event_loc, "selection") else []
            if selected_loc_rows:
                selected_loc_idx = selected_loc_rows[0]
                loc_id = df_locs.iloc[selected_loc_idx]['location_id']
                loc_nombre = df_locs.iloc[selected_loc_idx][loc_name_col]

                st.markdown(f"""
                <div class="detail-box">
                    <h3>2. Nivel Particular: Equipos ubicados en «{loc_nombre}»</h3>
                </div>
                """, unsafe_allow_html=True)

                items_in_loc = df_items[df_items['location_id'] == loc_id]
                if not items_in_loc.empty:
                    st.dataframe(items_in_loc, use_container_width=True, hide_index=True)
                else:
                    st.info("No hay equipos asignados a esta ubicación.")
            else:
                st.info("👆 Selecciona una ubicación arriba para ver su contenido.")

        # ==========================================
        # 3. CATÁLOGO GENERAL COMPLETO
        # ==========================================
        elif seccion == "📦 Catálogo General Completo":
            st.markdown("### Consulta Global de Equipos")
            col_search, col_dl = st.columns([3, 1])
            with col_search:
                q = st.text_input("🔍 Buscar:", placeholder="Escribe para buscar cualquier equipo...")
            with col_dl:
                st.write("")
                st.download_button(
                    "📥 Descargar CSV",
                    data=df_items.to_csv(index=False).encode('utf-8'),
                    file_name="catalogo_pcb.csv",
                    mime="text/csv",
                    use_container_width=True
                )

            df_show = df_items.copy()
            if q:
                mask = df_show.astype(str).apply(lambda r: r.str.contains(q, case=False, na=False)).any(axis=1)
                df_show = df_show[mask]

            st.caption("👉 Haz clic en una fila para ver el desglose completo del equipo:")
            event_all = st.dataframe(
                df_show,
                use_container_width=True,
                hide_index=True,
                on_select="rerun",
                selection_mode="single-row"
            )

            sel_all_rows = event_all.selection.rows if hasattr(event_all, "selection") else []
            if sel_all_rows:
                equipo_sel = df_show.iloc[sel_all_rows[0]]
                st.markdown(f"""
                <div class="detail-box">
                    <h3>Detalles del Registro Seleccionado</h3>
                </div>
                """, unsafe_allow_html=True)
                st.json(equipo_sel.to_dict())

        # ==========================================
        # 4. BITÁCORA DE AUDITORÍA
        # ==========================================
        elif seccion == "📝 Bitácora de Auditoría":
            st.markdown("### Registro Histórico de Cambios (Audit Logs)")
            res_audit = requests.get(f"{API_BASE_URL}/audit-logs", timeout=3)
            if res_audit.status_code == 200:
                df_audit = pd.DataFrame(res_audit.json())
                st.dataframe(df_audit, use_container_width=True, hide_index=True)
            else:
                st.error("No se pudo cargar la bitácora de auditoría.")

    else:
        st.error("Error al obtener los datos de la API.")

except requests.exceptions.ConnectionError:
    api_status.error("🔴 API Desconectada")
    st.error("⚠️ No se pudo conectar con el servidor backend.")
    st.info("Asegúrate de tener activa la API: `uvicorn api.main:app --reload`")