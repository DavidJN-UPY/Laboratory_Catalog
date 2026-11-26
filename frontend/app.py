import json
import os
from pathlib import Path

import pandas as pd
import requests
import streamlit as st
from PIL import Image, ImageOps

IMG_DIR = Path(__file__).resolve().parent / "img"   # fotos: img/<internal_code>.jpg
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
HIDDEN = ("pass", "hash", "token", "secret")
FK_IDS = ("category_id", "location_id")
SKIP_FORM = ("created", "updated", "timestamp")
STATUS_NAMES = ("status", "state", "estado", "condition", "condicion")
NAME_COLS = ("standardized_name", "nombre_estandar", "name", "nombre", "title", "titulo")
SORTS = ["Más recientes", "Nombre A–Z", "Nombre Z–A"]
LABELS = {
    "standardized_name": "Nombre estándar",
    "internal_code": "Código interno",
    "technical_description": "Descripción técnica",
    "name": "Nombre",
    "building": "Edificio",
    "lab": "Laboratorio",
    "shelf_cabinet": "Anaquel / estante",
    "email": "Correo",
    "role": "Rol",
    "description": "Descripción",
    "status": "Estado",
    "action": "Acción",
    "quantity": "Cantidad",
    "brand": "Marca",
    "model": "Modelo",
    "serial_number": "No. de serie",
    "created_at": "Creado",
    "updated_at": "Actualizado",
    "full_name": "Nombre completo",
    "action_performed": "Acción",
    "timestamp": "Fecha",
    "modified_attributes": "Cambios",
}

dialog = getattr(st, "dialog", None) or getattr(st, "experimental_dialog", None) or (lambda *a, **k: (lambda f: f))

st.set_page_config(page_title="Catálogo Laboratorio de PCB", page_icon="⚡", layout="wide")

st.markdown("""
<style>
    .block-container {padding-top: 1.8rem; padding-bottom: 2.5rem;}
    [data-testid="stSidebar"] {background: #0e3b33;}
    [data-testid="stSidebar"] * {color: #d8ebe6 !important;}
    .hero {background: linear-gradient(135deg, #0e3b33, #1d6b5b); border-left: 6px solid #c0773a;
           padding: 24px 30px; border-radius: 14px; margin-bottom: 1.5rem;}
    .hero h1 {color: #ffffff !important; font-size: 1.8rem; font-weight: 700; margin: 0; padding: 0;}
    .hero p {color: #bfe0d6; margin: 6px 0 0 0;}
    .detail-box {border-left: 4px solid #c0773a; background: rgba(192, 119, 58, 0.09);
                 padding: 12px 18px; border-radius: 8px; margin: 1.2rem 0 0.8rem 0;}
    .detail-box h3 {margin: 0; padding: 0; font-size: 1.15rem;}
</style>
<div class="hero">
    <h1>Catálogo Laboratorio de PCB</h1>
    <p>Consulta, busca y administra los equipos del laboratorio.</p>
</div>
""", unsafe_allow_html=True)


# ---------- Utilidades ----------
@st.cache_data
def photo_credits():
    try:
        return json.loads((IMG_DIR / "credits.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def photo_path(row):
    code = row.get("internal_code")
    path = IMG_DIR / f"{code}.jpg" if isinstance(code, str) and code else None
    return path if path and path.is_file() else None


@st.cache_data
def card_thumb(path):
    """Recorta a 4:3 para que todas las tarjetas tengan la misma altura."""
    with Image.open(path) as im:
        return ImageOps.fit(im.convert("RGB"), (480, 360))


def show_photo(row, caption=True):
    path = photo_path(row)
    if not path:
        return
    c = photo_credits().get(row.get("internal_code"), {})
    cap = c.get("source") if caption else None
    st.image(str(path) if caption else card_thumb(str(path)), width="stretch")
    if cap:
        st.caption(cap)


def is_hidden(col):
    return any(h in col.lower() for h in HIDDEN)


def is_id_col(col):
    c = col.lower()
    return c == "id" or c.endswith("_id")


@st.cache_data(ttl=20, show_spinner="Cargando datos…")
def fetch(endpoint):
    r = requests.get(f"{API_BASE_URL}/{endpoint}", timeout=5)
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    return df[[c for c in df.columns if not is_hidden(c)]]


def text_col(df):
    lower_map = {c.lower(): c for c in df.columns}
    for candidate in NAME_COLS:
        if candidate in lower_map:
            return lower_map[candidate]
    for c in df.columns:
        if c.lower().endswith("_name") or "name" in c.lower() or "nombre" in c.lower():
            return c
    return next((c for c in df.columns if not is_id_col(c)), df.columns[0])


def lbl(c):
    return LABELS.get(c, c.replace("_", " ").capitalize().replace(" id", " ID"))


def pretty(df):
    return df.rename(columns=lbl)


def search(df, q, cols=None):
    if not q:
        return df
    target_cols = cols if cols is not None else [c for c in df.columns if not is_id_col(c)]
    if not target_cols:
        return df
    mask = df[target_cols].astype(str).apply(lambda col: col.str.contains(q, case=False, na=False)).any(axis=1)
    return df[mask]


def table(df, key):
    """Tabla con selección de fila. Devuelve la posición elegida o None."""
    ev = st.dataframe(df, hide_index=True, on_select="rerun", selection_mode="single-row", key=key)
    rows = ev.selection.rows
    return rows[0] if rows else None


def py(v):
    """Valor de pandas/numpy -> valor normal de Python (o None si está vacío)."""
    if v is None or (not hasattr(v, "__len__") and pd.isna(v)):
        return None
    return v.item() if hasattr(v, "item") else v


def send(method, path, payload):
    try:
        r = requests.request(method, f"{API_BASE_URL}{path}", json=payload, timeout=5)
    except requests.RequestException:
        return False, "No se pudo conectar con la API. Revisa que esté encendida."
    if r.ok:
        return True, r.json()
    try:
        detail = r.json().get("detail", r.text)
    except ValueError:
        detail = r.text
    return False, f"No se guardó: {str(detail).splitlines()[0]}"


# ---------- Barra lateral ----------
with st.sidebar:
    st.markdown("### ⚡ Laboratorio de PCB")
    section = st.radio(
        "Secciones",
        ["Resumen", "Categorías", "Ubicaciones", "Catálogo", "Agregar equipo", "Historial"],
        label_visibility="collapsed",
    )
    if st.button("Actualizar datos"):
        st.cache_data.clear()
        st.rerun()

if "flash" in st.session_state:
    st.toast(st.session_state.pop("flash"), icon="✅")

# ---------- Carga de datos ----------
try:
    cats, locs, raw_items = fetch("categories"), fetch("physical-locations"), fetch("catalog-items")
except requests.RequestException:
    st.sidebar.markdown("🔴 API desconectada")
    st.error("No se pudo conectar con la API. Enciéndela y presiona «Reintentar».")
    st.code("uvicorn api.main:app --reload")
    if st.button("Reintentar", type="primary"):
        st.cache_data.clear()
        st.rerun()
    st.stop()

st.sidebar.markdown("🟢 API conectada")

cat_pk = "category_id" if "category_id" in cats.columns else next((c for c in cats.columns if is_id_col(c)), cats.columns[0])
loc_pk = "location_id" if "location_id" in locs.columns else next((c for c in locs.columns if is_id_col(c)), locs.columns[0])

cat_name = text_col(cats)
locs = locs.copy()
parts = [c for c in ("lab", "shelf_cabinet") if c in locs.columns] or [text_col(locs)]
locs["_label"] = locs[parts].astype(str).agg(" – ".join, axis=1)

items = raw_items.copy()
if "category_id" in items.columns:
    items["Categoría"] = items["category_id"].map(dict(zip(cats[cat_pk], cats[cat_name])))
if "location_id" in items.columns:
    items["Ubicación"] = items["location_id"].map(dict(zip(locs[loc_pk], locs["_label"])))

has_cols = len(raw_items.columns) > 0
pk = next((c for c in raw_items.columns if is_id_col(c)), raw_items.columns[0]) if has_cols else "item_id"
name_c = text_col(raw_items) if has_cols else "standardized_name"
status_col = next((c for c in raw_items.columns if c.lower() in STATUS_NAMES), None)
FK_OPTS = {
    "category_id": dict(zip(cats[cat_pk], cats[cat_name])),
    "location_id": dict(zip(locs[loc_pk], locs["_label"])),
}


def items_view(df):
    return pretty(df.drop(columns=[c for c in FK_IDS if c in df.columns]))


def ficha(row, heading=True):
    if heading:
        st.markdown("#### Ficha técnica")
    data = items_view(row.to_frame().T).iloc[0]
    with st.container(border=True):
        cols = st.columns(3)
        for i, (k, v) in enumerate(data.items()):
            with cols[i % 3]:
                st.caption(k)
                st.markdown(f"**{'—' if pd.isna(v) else v}**")


# ---------- Formularios (crear y editar) ----------
def field(c, default, key):
    label = lbl(c) + (" *" if c in required_cols() else "")
    help_ = "Déjalo vacío y se genera automáticamente." if c == "internal_code" else None
    s = raw_items[c]
    if c in FK_OPTS:
        opts = list(FK_OPTS[c])
        idx = opts.index(default) if default in opts else 0
        return st.selectbox(label, opts, index=idx, format_func=FK_OPTS[c].get, key=key)
    if pd.api.types.is_bool_dtype(s):
        return st.checkbox(label, value=bool(py(default)), key=key)
    if pd.api.types.is_numeric_dtype(s):
        base = py(default)
        if pd.api.types.is_integer_dtype(s) or (s.dropna() % 1 == 0).all():
            return st.number_input(label, value=int(base or 0), step=1, key=key)
        return st.number_input(label, value=float(base or 0), key=key)
    txt = "" if py(default) is None else str(default)
    if any(w in c.lower() for w in ("description", "descripcion", "notes", "notas")):
        return st.text_area(label, value=txt, key=key)
    return st.text_input(label, value=txt, key=key, help=help_)


def required_cols():
    """Campos que la base de datos exige (NOT NULL) y que el usuario debe escribir."""
    return [c for c in (name_c, "technical_description") if c in raw_items.columns]


def item_form(key, defaults=None):
    d = defaults or {}
    values = {}
    with st.form(key):
        cols = st.columns(2)
        shown = [c for c in raw_items.columns if c != pk and not any(s in c.lower() for s in SKIP_FORM)]
        for i, c in enumerate(shown):
            with cols[i % 2]:
                values[c] = field(c, d.get(c), f"{key}_{c}")
        sent = st.form_submit_button("Guardar", type="primary")
    return sent, values


def submit(method, path, values, ok_msg):
    payload = {k: (v.strip() or None) if isinstance(v, str) else py(v) for k, v in values.items()}
    missing = [lbl(c) for c in required_cols() if payload.get(c) is None]
    if missing:
        st.error("Faltan campos obligatorios: " + ", ".join(f"«{m}»" for m in missing))
        return
    if payload.get("internal_code") is None:
        # Al crear, la API lo genera; al editar, se conserva el código actual.
        payload.pop("internal_code", None)
    with st.spinner("Guardando…"):
        ok, res = send(method, path, payload)
    if ok:
        st.cache_data.clear()
        st.session_state.edit_item = None
        st.session_state.form_n = st.session_state.get("form_n", 0) + 1
        st.session_state.flash = ok_msg
        st.rerun()
    else:
        st.error(res)


@dialog("Detalle del equipo", width="large")
def detail(item_id):
    row = items[items[pk] == item_id]
    if row.empty:
        st.warning("Este equipo ya no existe.")
        return
    row = row.iloc[0]
    n = st.session_state.get("form_n", 0)
    if st.session_state.get("edit_item") == item_id:
        st.markdown(f'<div class="detail-box"><h3>Editar «{row[name_c]}»</h3></div>', unsafe_allow_html=True)
        raw = raw_items[raw_items[pk] == item_id].iloc[0].to_dict()
        sent, vals = item_form(f"edit_{item_id}_{n}", raw)
        st.button("Cancelar", key="cancel_edit", on_click=lambda: st.session_state.update(edit_item=None))
        if sent:
            submit("PUT", f"/catalog-items/{item_id}", vals, "Cambios guardados")
    else:
        st.markdown(f"## {row[name_c]}")
        chips = [f"📂 {row.get('Categoría') or '—'}", f"📍 {row.get('Ubicación') or '—'}"]
        if status_col:
            chips.append(f"{lbl(status_col)}: **{row[status_col]}**")
        st.markdown("  &nbsp;&nbsp;|&nbsp;&nbsp;  ".join(chips))
        show_photo(row)
        ficha(row)
        st.button("Editar equipo", key="edit_btn", type="primary",
                  on_click=lambda: st.session_state.update(edit_item=item_id))


def reset_filters():
    st.session_state.update(f_q="", f_cat=[], f_loc=[], f_status=[], f_sort=SORTS[0])


def open_card(i):
    st.session_state.update(open_item=py(i), edit_item=None)


def open_group(fk, value, title):
    st.session_state.open_group = (fk, py(value), title)


@dialog("Equipos", width="large")
def group_dialog(fk, value, title):
    st.markdown(f"### {title}")
    sub = items[items[fk] == value]
    if sub.empty:
        st.info("Todavía no hay equipos aquí. Puedes agregarlos desde «Agregar equipo».")
        return
    st.caption(f"{len(sub)} equipos. Abre uno para ver su ficha técnica.")
    for _, r in sub.iterrows():
        with st.expander(str(r[name_c])):
            show_photo(r)
            ficha(r, heading=False)


def master_detail(parent, pk_, fk, title, key):
    q = st.text_input("Buscar", key=f"q_{key}", placeholder="Escribe para filtrar…", label_visibility="collapsed")
    shown = search(parent, q).reset_index(drop=True)
    if shown.empty:
        st.warning("Ningún resultado coincide con tu búsqueda.")
        return
    counts = items[fk].value_counts() if fk in items.columns else {}
    skip = {pk_, title, *(parts if title.startswith("_") else [])}
    cols = st.columns(3)
    for n, r in enumerate(shown.to_dict("records")):
        with cols[n % 3].container(border=True):
            st.markdown(f"**{r[title]}**")
            extra = " | ".join(f"{lbl(k)}: {v}" for k, v in r.items()
                               if k not in skip and not k.startswith("_") and pd.notna(v))
            if extra:
                st.caption(extra)
            st.caption(f"📦 {int(counts.get(r[pk_], 0))} equipos")
            st.button("Ver equipos", key=f"g_{key}_{r[pk_]}", on_click=open_group, args=(fk, r[pk_], r[title]))
    grp = st.session_state.pop("open_group", None)
    if grp:
        group_dialog(*grp)


# ---------- Secciones ----------
if section == "Resumen":
    c1, c2, c3 = st.columns(3)
    c1.metric("Equipos registrados", len(items))
    c2.metric("Categorías", len(cats))
    c3.metric("Ubicaciones", len(locs))
    st.divider()
    left, right = st.columns(2)
    if "Categoría" in items.columns and not items.empty:
        left.markdown("##### Equipos por categoría")
        left.bar_chart(items["Categoría"].value_counts(), color="#1d6b5b")
    if "Ubicación" in items.columns and not items.empty:
        right.markdown("##### Equipos por ubicación")
        right.bar_chart(items["Ubicación"].value_counts(), color="#c0773a")

elif section == "Categorías":
    st.subheader("Categorías")
    master_detail(cats, cat_pk, "category_id", cat_name, "cats")

elif section == "Ubicaciones":
    st.subheader("Ubicaciones")
    master_detail(locs, loc_pk, "location_id", "_label", "locs")

elif section == "Catálogo":
    st.subheader("Catálogo")
    if items.empty:
        st.info("Aún no hay equipos registrados. Agrega el primero desde «Agregar equipo».")
        st.stop()

    top1, top2 = st.columns([3, 1])
    q = top1.text_input("Buscar", key="f_q", placeholder="Buscar por nombre estándar…",
                        label_visibility="collapsed")
    mode = top2.radio("Vista", ["Tarjetas", "Tabla"], horizontal=True, key="f_view", label_visibility="collapsed")

    fc = st.columns(5)
    cat_f = fc[0].multiselect("Categoría", sorted(cats[cat_name].astype(str)), key="f_cat",
                              placeholder="Todas las categorías")
    loc_f = fc[1].multiselect("Ubicación", sorted(locs["_label"]), key="f_loc", placeholder="Todas las ubicaciones")
    status_f = []
    if status_col:
        status_f = fc[2].multiselect(lbl(status_col), sorted(items[status_col].dropna().astype(str).unique()),
                                     key="f_status", placeholder="Todos")
    sort_f = fc[3].selectbox("Ordenar por", SORTS, key="f_sort")
    fc[4].button("Limpiar filtros", on_click=reset_filters, key="clr1")

    df = items.copy()
    if cat_f and "Categoría" in df.columns:
        df = df[df["Categoría"].isin(cat_f)]
    if loc_f and "Ubicación" in df.columns:
        df = df[df["Ubicación"].isin(loc_f)]
    if status_f:
        df = df[df[status_col].astype(str).isin(status_f)]
    df = search(df, q, cols=[name_c])
    if sort_f == SORTS[0]:
        df = df.sort_values(pk, ascending=False)
    else:
        df = df.sort_values(name_c, key=lambda s: s.astype(str).str.lower(), ascending=sort_f == SORTS[1])
    df = df.reset_index(drop=True)

    info, dl = st.columns([4, 1])
    info.caption(f"Mostrando {len(df)} de {len(items)} equipos")
    dl.download_button("Descargar CSV", items_view(df).to_csv(index=False).encode("utf-8-sig"),
                       file_name="catalogo_pcb.csv", mime="text/csv")

    if df.empty:
        st.warning("Ningún equipo coincide con tu búsqueda o filtros.")
        st.button("Limpiar filtros", on_click=reset_filters, key="clr2")
        st.stop()

    if mode == "Tabla":
        st.caption("Marca la casilla de una fila para abrir su detalle.")
        j = table(items_view(df), f"tbl_all_{st.session_state.get('tbl_n', 0)}")
        if j is not None:
            # Cambiar la llave de la tabla limpia la casilla y evita que se reabra sola
            st.session_state.update(open_item=py(df.iloc[j][pk]), edit_item=None,
                                    tbl_n=st.session_state.get("tbl_n", 0) + 1)
            st.rerun()
    else:
        cols = st.columns(3)
        for n, r in enumerate(df.head(30).to_dict("records")):
            with cols[n % 3].container(border=True):
                show_photo(r, caption=False)
                st.markdown(f"**{r[name_c]}**")
                if r.get("internal_code"):
                    st.caption(f"🔖 {r['internal_code']}")
                st.caption(f"📂 {r.get('Categoría') or '—'}")
                st.caption(f"📍 {r.get('Ubicación') or '—'}")
                if status_col:
                    st.caption(f"{lbl(status_col)}: {r[status_col]}")
                st.button("Ver ficha", key=f"v{r[pk]}", on_click=open_card, args=(r[pk],))
        if len(df) > 30:
            st.caption("Se muestran los primeros 30. Usa la búsqueda o los filtros para acotar.")

    oi = st.session_state.pop("open_item", None)
    if oi is not None:
        detail(oi)

elif section == "Agregar equipo":
    st.subheader("Agregar equipo")
    st.caption("Los campos con * son obligatorios.")
    sent, vals = item_form(f"new_{st.session_state.get('form_n', 0)}")
    if sent:
        submit("POST", "/catalog-items", vals, "Equipo agregado al catálogo")

elif section == "Historial":
    st.subheader("Historial de cambios")
    try:
        logs = fetch("audit-logs")
    except requests.RequestException:
        st.error("No se pudo cargar el historial.")
        st.stop()
    q = st.text_input("Buscar", placeholder="Filtrar el historial…", label_visibility="collapsed")
    logs = logs.copy()
    if "item_id" in logs.columns and has_cols:
        logs.insert(1, "Equipo", logs["item_id"].map(dict(zip(raw_items[pk], raw_items[name_c]))))
    try:
        users = fetch("users")
        u_name = text_col(users)
        if "user_id" in logs.columns and "user_id" in users.columns:
            logs.insert(2, "Usuario", logs["user_id"].map(dict(zip(users["user_id"], users[u_name]))))
    except requests.RequestException:
        pass
    shown = search(logs, q)
    if shown.empty:
        st.info("No hay movimientos que mostrar.")
    else:
        st.dataframe(pretty(shown.drop(columns=[c for c in ("item_id", "user_id") if c in shown.columns])),
                     hide_index=True)