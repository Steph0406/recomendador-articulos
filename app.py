"""
GameGraph: Recomendador de artículos de videojuegos.
Interfaz web en Streamlit conectada a Neo4j AuraDB (nube).

Ejecutar:  streamlit run app.py
"""
import streamlit as st
from neo4j.exceptions import AuthError, ConstraintError, ServiceUnavailable

from db.conexion import ConexionNeo4j
from servicios import articulos, estadisticas, recomendaciones as rec, usuarios

st.set_page_config(page_title="GameGraph", page_icon="🎮", layout="wide")

TIPOS = ["reseña", "guía", "noticia"]
COLORES = {"Usuario": "#CECBF6", "Articulo": "#9FE1CB", "Juego": "#FAC775"}


# ----------------------------------------------------------- UTILIDADES ---
def aviso(texto):
    """Guarda un mensaje y recarga la página para mostrar los datos actualizados."""
    st.session_state["aviso"] = texto
    st.rerun()


def siguiente_id(registros, prefijo):
    """Genera el siguiente id consecutivo (U011, A021, ...)."""
    numeros = [int(r["id"][1:]) for r in registros if r["id"].startswith(prefijo)]
    return f"{prefijo}{max(numeros, default=0) + 1:03d}"


def _esc(texto):
    return str(texto).replace('"', '\\"')


def dibujar_grafo(aristas):
    """Dibuja una lista de aristas {desde, hacia, rel, tipo_desde, tipo_hacia} con Graphviz."""
    if not aristas:
        st.info("No hay relaciones para mostrar.")
        return
    dot = [
        "digraph G {", "rankdir=LR;",
        'node [style="filled,rounded", shape=box, fontname="Helvetica", fontsize=10];',
        'edge [fontname="Helvetica", fontsize=8, color="#888888"];',
    ]
    nodos = {}
    for a in aristas:
        nodos[a["desde"]] = a["tipo_desde"]
        nodos[a["hacia"]] = a["tipo_hacia"]
    for nombre, tipo in nodos.items():
        dot.append(f'"{_esc(nombre)}" [fillcolor="{COLORES.get(tipo, "#EEEEEE")}"];')
    for a in aristas:
        dot.append(f'"{_esc(a["desde"])}" -> "{_esc(a["hacia"])}" [label="{a["rel"]}"];')
    dot.append("}")
    st.graphviz_chart("\n".join(dot))


# ------------------------------------------------------------- CONEXIÓN ---
try:
    ConexionNeo4j.obtener_driver().verify_connectivity()
except (ServiceUnavailable, AuthError, RuntimeError, OSError) as error:
    st.error(
        "❌ Sin conexión con Neo4j AuraDB. Revisa tu internet y que la instancia "
        "esté en estado *Running* en console.neo4j.io."
    )
    st.caption(f"Detalle técnico: {error}")
    if st.button("🔄 Reintentar conexión"):
        ConexionNeo4j.cerrar()  # descarta el driver viejo y crea uno nuevo
        st.rerun()
    st.stop()

lista_usuarios = usuarios.listar_usuarios()
mapa_usuarios = {u["id"]: u for u in lista_usuarios}
nombre_de = lambda id_u: f"{id_u} · {mapa_usuarios[id_u]['nombre']}"

# --------------------------------------------------------------- SIDEBAR ---
st.sidebar.title("🎮 GameGraph")
st.sidebar.caption("Recomendador de artículos de videojuegos\n\nBase de datos: **Neo4j AuraDB** ☁️")
pagina = st.sidebar.radio(
    "Menú", ["🏠 Inicio", "👤 Usuarios", "📰 Artículos", "⭐ Recomendaciones", "🌐 Red social"]
)
if not lista_usuarios:
    st.warning("No hay usuarios. Ejecuta primero: python -m seed.seed")
    st.stop()
actual = st.sidebar.selectbox("Usuario activo", list(mapa_usuarios), format_func=nombre_de)

if "aviso" in st.session_state:
    st.success(st.session_state.pop("aviso"))


# ================================================================ INICIO ===
if pagina == "🏠 Inicio":
    st.title("🏠 Panel general")
    c = estadisticas.conteos()
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Usuarios", c["usuarios"])
    col2.metric("Artículos", c["articulos"])
    col3.metric("Juegos", c["juegos"])
    col4.metric("Relaciones", c["relaciones"])

    izq, der = st.columns(2)
    with izq:
        st.subheader("🏆 Artículos mejor calificados")
        st.dataframe(rec.mejores_articulos(), hide_index=True)
    with der:
        st.subheader("🔥 Juegos más populares")
        st.dataframe(rec.juegos_populares(), hide_index=True)

    st.subheader(f"🕸️ Grafo de {mapa_usuarios[actual]['nombre']} (vecindad a 1 salto)")
    dibujar_grafo(estadisticas.subgrafo_usuario(actual))


# ============================================================== USUARIOS ===
elif pagina == "👤 Usuarios":
    st.title("👤 Usuarios")
    ver, crear, editar, borrar = st.tabs(["📋 Ver", "➕ Crear", "✏️ Editar", "🗑️ Eliminar"])

    with ver:  # READ
        st.dataframe(lista_usuarios, hide_index=True)
        sel = st.selectbox("Ver detalle de", list(mapa_usuarios), format_func=nombre_de, key="ver_u")
        d = usuarios.obtener_usuario(sel)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Siguiendo", d["siguiendo"])
        c2.metric("Seguidores", d["seguidores"])
        c3.metric("Escritos", d["escritos"])
        c4.metric("Leídos", d["leidos"])

    with crear:  # CREATE
        nuevo_id = siguiente_id(lista_usuarios, "U")
        with st.form("form_crear_u", clear_on_submit=True):
            st.text_input("ID (automático)", nuevo_id, disabled=True)
            nombre = st.text_input("Nombre")
            pais = st.text_input("País")
            if st.form_submit_button("Crear usuario"):
                if not nombre.strip() or not pais.strip():
                    st.error("Nombre y país son obligatorios.")
                else:
                    try:
                        usuarios.crear_usuario(nuevo_id, nombre.strip(), pais.strip())
                        aviso(f"✅ Usuario {nuevo_id} creado")
                    except ConstraintError:
                        st.error("Ese ID ya existe.")

    with editar:  # UPDATE
        sel = st.selectbox("Usuario a editar", list(mapa_usuarios), format_func=nombre_de, key="edit_u")
        with st.form("form_editar_u"):
            nombre = st.text_input("Nombre", mapa_usuarios[sel]["nombre"])
            pais = st.text_input("País", mapa_usuarios[sel]["pais"])
            if st.form_submit_button("Guardar cambios"):
                usuarios.actualizar_usuario(sel, nombre.strip(), pais.strip())
                aviso(f"✅ Usuario {sel} actualizado")

    with borrar:  # DELETE
        sel = st.selectbox("Usuario a eliminar", list(mapa_usuarios), format_func=nombre_de, key="del_u")
        st.warning("Se eliminarán también sus relaciones y los artículos que escribió.")
        if st.checkbox("Confirmo que quiero eliminarlo", key="conf_u"):
            if st.button("Eliminar usuario", type="primary"):
                r = usuarios.eliminar_usuario(sel)
                aviso(f"🗑️ Usuario {sel} eliminado ({r['articulos_borrados']} artículos borrados)")


# ============================================================= ARTÍCULOS ===
elif pagina == "📰 Artículos":
    st.title("📰 Artículos")
    lista_art = articulos.listar_articulos()
    mapa_art = {a["id"]: a for a in lista_art}
    titulo_de = lambda i: f"{i} · {mapa_art[i]['titulo']}"
    juegos = [j["nombre"] for j in articulos.listar_juegos()]

    ver, crear, calificar, editar, borrar = st.tabs(
        ["📋 Ver", "➕ Crear", "⭐ Calificar", "✏️ Editar", "🗑️ Eliminar"]
    )

    with ver:  # READ
        st.dataframe(lista_art, hide_index=True)

    with crear:  # CREATE
        nuevo_id = siguiente_id(lista_art, "A")
        with st.form("form_crear_a", clear_on_submit=True):
            st.text_input("ID (automático)", nuevo_id, disabled=True)
            st.text_input("Autor (usuario activo)", nombre_de(actual), disabled=True)
            titulo = st.text_input("Título")
            tipo = st.selectbox("Tipo", TIPOS)
            juego = st.selectbox("Juego", juegos)
            if st.form_submit_button("Publicar artículo"):
                if not titulo.strip():
                    st.error("El título es obligatorio.")
                else:
                    articulos.crear_articulo(nuevo_id, titulo.strip(), tipo, actual, juego)
                    aviso(f"✅ Artículo {nuevo_id} publicado")

    if not mapa_art:
        st.info("No hay artículos todavía.")
        st.stop()

    with calificar:  # UPDATE de relación (MERGE)
        st.caption(f"Registrar que **{mapa_usuarios[actual]['nombre']}** leyó un artículo")
        sel = st.selectbox("Artículo", list(mapa_art), format_func=titulo_de, key="cal_a")
        estrellas = st.slider("Calificación", 1, 5, 4)
        if st.button("Guardar lectura"):
            articulos.registrar_lectura(actual, sel, estrellas)
            aviso(f"⭐ Calificación de {estrellas} guardada para {sel}")

    with editar:  # UPDATE
        sel = st.selectbox("Artículo a editar", list(mapa_art), format_func=titulo_de, key="edit_a")
        with st.form("form_editar_a"):
            titulo = st.text_input("Título", mapa_art[sel]["titulo"])
            tipo = st.selectbox("Tipo", TIPOS, index=TIPOS.index(mapa_art[sel]["tipo"]))
            if st.form_submit_button("Guardar cambios"):
                articulos.actualizar_articulo(sel, titulo.strip(), tipo)
                aviso(f"✅ Artículo {sel} actualizado")

    with borrar:  # DELETE
        sel = st.selectbox("Artículo a eliminar", list(mapa_art), format_func=titulo_de, key="del_a")
        if st.checkbox("Confirmo que quiero eliminarlo", key="conf_a"):
            if st.button("Eliminar artículo", type="primary"):
                articulos.eliminar_articulo(sel)
                aviso(f"🗑️ Artículo {sel} eliminado")


# ======================================================= RECOMENDACIONES ===
elif pagina == "⭐ Recomendaciones":
    nombre = mapa_usuarios[actual]["nombre"]
    st.title(f"⭐ Recomendaciones para {nombre}")

    st.subheader("👥 Usuarios con lecturas similares también leyeron…")
    st.caption("Traversal: (yo)-[:LEYO]->(art)<-[:LEYO]-(otro)-[:LEYO]->(recomendado)")
    st.dataframe(rec.colaborativa(actual), hide_index=True)

    st.subheader("🎯 Basado en los juegos que te gustan")
    st.caption("Traversal: (yo)-[:LE_GUSTA]->(juego) + mismo género <-[:TRATA_SOBRE]-(artículo)")
    st.dataframe(rec.por_gustos(actual), hide_index=True)

    st.subheader("❤️ Marcar un juego como favorito")
    juegos = [j["nombre"] for j in articulos.listar_juegos()]
    juego = st.selectbox("Juego", juegos)
    if st.button("Me gusta"):
        usuarios.me_gusta(actual, juego)
        aviso(f"❤️ A {nombre} ahora le gusta {juego}")


# ============================================================ RED SOCIAL ===
elif pagina == "🌐 Red social":
    nombre = mapa_usuarios[actual]["nombre"]
    st.title(f"🌐 Red social de {nombre}")
    otros = [i for i in mapa_usuarios if i != actual]

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("➕ Seguir / dejar de seguir")
        objetivo = st.selectbox("Usuario", otros, format_func=nombre_de, key="seguir")
        b1, b2 = st.columns(2)
        if b1.button("Seguir"):
            usuarios.seguir(actual, objetivo)
            aviso(f"✅ {nombre} ahora sigue a {mapa_usuarios[objetivo]['nombre']}")
        if b2.button("Dejar de seguir"):
            r = usuarios.dejar_de_seguir(actual, objetivo)
            aviso("✅ Dejaste de seguirlo" if r else "ℹ️ No lo seguías")

        st.subheader("💡 A quién seguir (vecindad a 2 saltos)")
        st.dataframe(rec.a_quien_seguir(actual), hide_index=True)

    with col2:
        st.subheader("🔭 Red extendida (hasta 3 niveles)")
        st.caption("Traversal de longitud variable: (yo)-[:SIGUE*1..3]->(otro)")
        st.dataframe(rec.red_extendida(actual), hide_index=True)

    st.divider()
    st.subheader("🧭 Camino más corto entre dos usuarios")
    c1, c2 = st.columns(2)
    origen = c1.selectbox("Desde", list(mapa_usuarios), format_func=nombre_de,
                          index=list(mapa_usuarios).index(actual), key="origen")
    destino = c2.selectbox("Hasta", list(mapa_usuarios), format_func=nombre_de,
                           index=len(mapa_usuarios) - 1, key="destino")
    if st.button("Buscar camino"):
        resultado = rec.camino_mas_corto(origen, destino)
        if origen == destino:
            st.info("Elige dos usuarios distintos.")
        elif resultado is None:
            st.error("No existe un camino de SIGUE entre esos usuarios.")
        else:
            st.success(f"{' → '.join(resultado['camino'])}  ({resultado['saltos']} saltos)")
            camino = resultado["camino"]
            dibujar_grafo([
                {"desde": a, "hacia": b, "rel": "SIGUE", "tipo_desde": "Usuario", "tipo_hacia": "Usuario"}
                for a, b in zip(camino, camino[1:])
            ])
