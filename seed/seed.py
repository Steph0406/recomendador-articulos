"""
Script de seeding: crea el esquema (constraints) y carga los datos iniciales
del recomendador de artículos de videojuegos.

Uso (desde la carpeta raíz del proyecto, con el venv activado):
    python -m seed.seed

ADVERTENCIA: borra TODOS los nodos y relaciones antes de cargar los datos.
"""
from db.conexion import ConexionNeo4j as db

# ---------------------------------------------------------------- DATOS ---

JUEGOS = [
    {"nombre": "Elden Ring", "genero": "RPG", "plataforma": "Multiplataforma"},
    {"nombre": "Baldur's Gate 3", "genero": "RPG", "plataforma": "PC"},
    {"nombre": "Zelda: Tears of the Kingdom", "genero": "Aventura", "plataforma": "Nintendo Switch"},
    {"nombre": "Hollow Knight", "genero": "Metroidvania", "plataforma": "Multiplataforma"},
    {"nombre": "Hades II", "genero": "Roguelike", "plataforma": "Multiplataforma"},
    {"nombre": "Valorant", "genero": "Shooter", "plataforma": "PC"},
    {"nombre": "Call of Duty: Black Ops 6", "genero": "Shooter", "plataforma": "Multiplataforma"},
    {"nombre": "EA Sports FC 25", "genero": "Deportes", "plataforma": "Multiplataforma"},
    {"nombre": "Minecraft", "genero": "Sandbox", "plataforma": "Multiplataforma"},
    {"nombre": "Stardew Valley", "genero": "Simulación", "plataforma": "Multiplataforma"},
]

USUARIOS = [
    {"id": "U001", "nombre": "Stephanie", "pais": "México"},
    {"id": "U002", "nombre": "Carlos", "pais": "México"},
    {"id": "U003", "nombre": "Ana", "pais": "Colombia"},
    {"id": "U004", "nombre": "Luis", "pais": "Argentina"},
    {"id": "U005", "nombre": "María", "pais": "España"},
    {"id": "U006", "nombre": "Diego", "pais": "Chile"},
    {"id": "U007", "nombre": "Sofía", "pais": "México"},
    {"id": "U008", "nombre": "Javier", "pais": "Perú"},
    {"id": "U009", "nombre": "Valeria", "pais": "México"},
    {"id": "U010", "nombre": "Andrés", "pais": "Colombia"},
]

# Cada artículo indica su autor (ESCRIBIO) y su juego (TRATA_SOBRE)
ARTICULOS = [
    {"id": "A001", "titulo": "Elden Ring: guía definitiva para principiantes", "tipo": "guía", "fecha": "2025-11-02", "autor": "U002", "juego": "Elden Ring"},
    {"id": "A002", "titulo": "Reseña de Baldur's Gate 3: el RPG que lo cambió todo", "tipo": "reseña", "fecha": "2025-12-10", "autor": "U003", "juego": "Baldur's Gate 3"},
    {"id": "A003", "titulo": "Los mejores builds de mago en Elden Ring", "tipo": "guía", "fecha": "2026-01-05", "autor": "U005", "juego": "Elden Ring"},
    {"id": "A004", "titulo": "Tears of the Kingdom: 10 secretos que no conocías", "tipo": "guía", "fecha": "2026-01-20", "autor": "U007", "juego": "Zelda: Tears of the Kingdom"},
    {"id": "A005", "titulo": "Reseña de Hollow Knight: una obra maestra indie", "tipo": "reseña", "fecha": "2026-02-03", "autor": "U004", "juego": "Hollow Knight"},
    {"id": "A006", "titulo": "Valorant: todos los cambios del nuevo parche", "tipo": "noticia", "fecha": "2026-02-14", "autor": "U006", "juego": "Valorant"},
    {"id": "A007", "titulo": "Hades II recibe su actualización más grande", "tipo": "noticia", "fecha": "2026-03-01", "autor": "U008", "juego": "Hades II"},
    {"id": "A008", "titulo": "Cómo empezar en Stardew Valley sin estresarte", "tipo": "guía", "fecha": "2026-03-12", "autor": "U009", "juego": "Stardew Valley"},
    {"id": "A009", "titulo": "Black Ops 6: análisis del modo zombis", "tipo": "reseña", "fecha": "2026-03-25", "autor": "U010", "juego": "Call of Duty: Black Ops 6"},
    {"id": "A010", "titulo": "Baldur's Gate 3: guía de compañeros y romances", "tipo": "guía", "fecha": "2026-04-02", "autor": "U003", "juego": "Baldur's Gate 3"},
    {"id": "A011", "titulo": "EA Sports FC 25: las mejores tácticas", "tipo": "guía", "fecha": "2026-04-15", "autor": "U006", "juego": "EA Sports FC 25"},
    {"id": "A012", "titulo": "Minecraft: 15 construcciones increíbles", "tipo": "guía", "fecha": "2026-04-28", "autor": "U010", "juego": "Minecraft"},
    {"id": "A013", "titulo": "Elden Ring: los jefes más difíciles", "tipo": "guía", "fecha": "2026-05-06", "autor": "U004", "juego": "Elden Ring"},
    {"id": "A014", "titulo": "Hollow Knight: los secretos del mapa", "tipo": "guía", "fecha": "2026-05-20", "autor": "U005", "juego": "Hollow Knight"},
    {"id": "A015", "titulo": "Reseña de Hades II: el roguelike perfecto", "tipo": "reseña", "fecha": "2026-06-01", "autor": "U001", "juego": "Hades II"},
    {"id": "A016", "titulo": "Valorant: guía de agentes para novatos", "tipo": "guía", "fecha": "2026-06-18", "autor": "U008", "juego": "Valorant"},
    {"id": "A017", "titulo": "Stardew Valley: novedades de la comunidad", "tipo": "noticia", "fecha": "2026-07-04", "autor": "U003", "juego": "Stardew Valley"},
    {"id": "A018", "titulo": "Tears of the Kingdom: reseña dos años después", "tipo": "reseña", "fecha": "2026-07-22", "autor": "U009", "juego": "Zelda: Tears of the Kingdom"},
    {"id": "A019", "titulo": "Minecraft llega a más escuelas", "tipo": "noticia", "fecha": "2026-08-09", "autor": "U002", "juego": "Minecraft"},
    {"id": "A020", "titulo": "Black Ops 6: las armas más fuertes de la temporada", "tipo": "guía", "fecha": "2026-09-01", "autor": "U007", "juego": "Call of Duty: Black Ops 6"},
]

# (seguidor, seguido, desde)
SIGUE = [
    ("U001", "U002", "2025-01-10"), ("U001", "U007", "2025-02-14"),
    ("U002", "U003", "2025-03-01"), ("U002", "U007", "2025-03-20"),
    ("U003", "U004", "2025-04-05"), ("U003", "U006", "2025-04-18"),
    ("U004", "U005", "2025-05-02"), ("U005", "U001", "2025-05-30"),
    ("U006", "U010", "2025-06-11"), ("U007", "U002", "2025-06-25"),
    ("U007", "U008", "2025-07-08"), ("U008", "U009", "2025-08-15"),
    ("U009", "U010", "2025-09-01"), ("U010", "U004", "2025-10-12"),
]

# (usuario, juego)
LE_GUSTA = [
    ("U001", "Elden Ring"), ("U001", "Hollow Knight"), ("U001", "Hades II"),
    ("U002", "Elden Ring"), ("U002", "Baldur's Gate 3"),
    ("U003", "Baldur's Gate 3"), ("U003", "Stardew Valley"),
    ("U004", "Hollow Knight"), ("U004", "Elden Ring"),
    ("U005", "Hades II"), ("U005", "Hollow Knight"),
    ("U006", "Valorant"), ("U006", "EA Sports FC 25"),
    ("U007", "Zelda: Tears of the Kingdom"), ("U007", "Call of Duty: Black Ops 6"),
    ("U008", "Valorant"), ("U008", "Hades II"),
    ("U009", "Stardew Valley"), ("U009", "Minecraft"),
    ("U010", "Minecraft"), ("U010", "Call of Duty: Black Ops 6"),
]

# (usuario, artículo, calificación 1-5, fecha)
LEYO = [
    ("U001", "A001", 5, "2026-03-01"), ("U001", "A002", 4, "2026-03-05"), ("U001", "A005", 5, "2026-03-10"),
    ("U002", "A001", 4, "2026-02-01"), ("U002", "A002", 5, "2026-02-03"), ("U002", "A007", 5, "2026-03-04"),
    ("U002", "A010", 4, "2026-04-06"), ("U002", "A004", 3, "2026-02-20"),
    ("U003", "A001", 5, "2026-01-11"), ("U003", "A003", 4, "2026-01-15"), ("U003", "A013", 4, "2026-05-10"),
    ("U004", "A002", 5, "2026-01-02"), ("U004", "A008", 3, "2026-03-15"), ("U004", "A018", 4, "2026-07-25"),
    ("U005", "A005", 5, "2026-02-10"), ("U005", "A014", 4, "2026-05-22"), ("U005", "A015", 5, "2026-06-03"),
    ("U006", "A009", 4, "2026-03-27"), ("U006", "A011", 5, "2026-04-16"), ("U006", "A020", 4, "2026-09-03"),
    ("U007", "A005", 4, "2026-02-12"), ("U007", "A007", 5, "2026-03-02"), ("U007", "A012", 3, "2026-05-01"),
    ("U007", "A014", 5, "2026-05-25"),
    ("U008", "A006", 4, "2026-02-15"), ("U008", "A016", 5, "2026-06-20"), ("U008", "A009", 3, "2026-03-30"),
    ("U009", "A008", 5, "2026-03-13"), ("U009", "A017", 4, "2026-07-05"), ("U009", "A012", 4, "2026-04-30"),
    ("U010", "A009", 5, "2026-03-26"), ("U010", "A020", 5, "2026-09-02"), ("U010", "A012", 4, "2026-04-29"),
    ("U010", "A019", 3, "2026-08-10"),
]

# ------------------------------------------------------------ FUNCIONES ---

def limpiar_base():
    """Elimina todos los nodos y sus relaciones."""
    db.escribir("MATCH (n) DETACH DELETE n")
    print("🧹 Base de datos limpia")


def crear_esquema():
    """Crea constraints de unicidad (cada uno genera un índice automático)."""
    constraints = [
        "CREATE CONSTRAINT usuario_id IF NOT EXISTS FOR (u:Usuario) REQUIRE u.id IS UNIQUE",
        "CREATE CONSTRAINT articulo_id IF NOT EXISTS FOR (a:Articulo) REQUIRE a.id IS UNIQUE",
        "CREATE CONSTRAINT juego_nombre IF NOT EXISTS FOR (j:Juego) REQUIRE j.nombre IS UNIQUE",
    ]
    for c in constraints:
        db.escribir(c)
    print("🔑 Constraints creados")


def cargar_nodos():
    """Carga Juegos y Usuarios en lote usando UNWIND."""
    db.escribir(
        """
        UNWIND $juegos AS j
        CREATE (:Juego {nombre: j.nombre, genero: j.genero, plataforma: j.plataforma})
        """,
        juegos=JUEGOS,
    )
    db.escribir(
        """
        UNWIND $usuarios AS u
        CREATE (:Usuario {id: u.id, nombre: u.nombre, pais: u.pais})
        """,
        usuarios=USUARIOS,
    )
    print(f"🎮 {len(JUEGOS)} juegos y 👤 {len(USUARIOS)} usuarios creados")


def cargar_articulos():
    """Crea los artículos y los conecta con su autor y su juego."""
    db.escribir(
        """
        UNWIND $articulos AS a
        CREATE (art:Articulo {id: a.id, titulo: a.titulo, tipo: a.tipo, fecha: date(a.fecha)})
        WITH art, a
        MATCH (u:Usuario {id: a.autor}), (j:Juego {nombre: a.juego})
        CREATE (u)-[:ESCRIBIO]->(art)
        CREATE (art)-[:TRATA_SOBRE]->(j)
        """,
        articulos=ARTICULOS,
    )
    print(f"📰 {len(ARTICULOS)} artículos creados")


def cargar_relaciones():
    """Crea las relaciones SIGUE, LE_GUSTA y LEYO."""
    db.escribir(
        """
        UNWIND $datos AS d
        MATCH (a:Usuario {id: d.seguidor}), (b:Usuario {id: d.seguido})
        CREATE (a)-[:SIGUE {desde: date(d.desde)}]->(b)
        """,
        datos=[{"seguidor": s, "seguido": t, "desde": f} for s, t, f in SIGUE],
    )
    db.escribir(
        """
        UNWIND $datos AS d
        MATCH (u:Usuario {id: d.usuario}), (j:Juego {nombre: d.juego})
        CREATE (u)-[:LE_GUSTA]->(j)
        """,
        datos=[{"usuario": u, "juego": j} for u, j in LE_GUSTA],
    )
    db.escribir(
        """
        UNWIND $datos AS d
        MATCH (u:Usuario {id: d.usuario}), (a:Articulo {id: d.articulo})
        CREATE (u)-[:LEYO {calificacion: d.calificacion, fecha: date(d.fecha)}]->(a)
        """,
        datos=[{"usuario": u, "articulo": a, "calificacion": c, "fecha": f}
               for u, a, c, f in LEYO],
    )
    print(f"🔗 {len(SIGUE)} SIGUE, {len(LE_GUSTA)} LE_GUSTA, {len(LEYO)} LEYO creadas")


def resumen():
    """Muestra el conteo final de nodos y relaciones por tipo."""
    nodos = db.leer("MATCH (n) RETURN labels(n)[0] AS etiqueta, count(*) AS total ORDER BY etiqueta")
    rels = db.leer("MATCH ()-[r]->() RETURN type(r) AS tipo, count(*) AS total ORDER BY tipo")
    print("\n📊 Resumen de la base de datos:")
    for n in nodos:
        print(f"   Nodo {n['etiqueta']:<10} {n['total']}")
    for r in rels:
        print(f"   Rel  {r['tipo']:<12} {r['total']}")


if __name__ == "__main__":
    limpiar_base()
    crear_esquema()
    cargar_nodos()
    cargar_articulos()
    cargar_relaciones()
    resumen()
    db.cerrar()
    print("\n✅ Seeding completado")
