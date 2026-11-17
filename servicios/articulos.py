"""CRUD de nodos :Articulo, lecturas (LEYO) y consulta de :Juego."""
from db.conexion import ConexionNeo4j as db


def _uno(resultado):
    return resultado[0] if resultado else None


# ------------------------------------------------------------ CREATE ---
def crear_articulo(id_articulo, titulo, tipo, autor_id, nombre_juego):
    """Crea el artículo y en la misma transacción lo conecta con su autor y su juego."""
    return _uno(db.escribir(
        """
        MATCH (u:Usuario {id: $autor}), (j:Juego {nombre: $juego})
        CREATE (a:Articulo {id: $id, titulo: $titulo, tipo: $tipo, fecha: date()})
        CREATE (u)-[:ESCRIBIO]->(a)-[:TRATA_SOBRE]->(j)
        RETURN a.id AS id, a.titulo AS titulo, u.nombre AS autor, j.nombre AS juego
        """,
        id=id_articulo, titulo=titulo, tipo=tipo, autor=autor_id, juego=nombre_juego,
    ))


# -------------------------------------------------------------- READ ---
def listar_articulos():
    """Lista artículos con autor, juego, número de lecturas y calificación promedio."""
    return db.leer(
        """
        MATCH (u:Usuario)-[:ESCRIBIO]->(a:Articulo)-[:TRATA_SOBRE]->(j:Juego)
        OPTIONAL MATCH (:Usuario)-[l:LEYO]->(a)
        RETURN a.id AS id, a.titulo AS titulo, a.tipo AS tipo,
               toString(a.fecha) AS fecha, u.nombre AS autor, j.nombre AS juego,
               count(l) AS lecturas, round(avg(l.calificacion), 1) AS calificacion
        ORDER BY a.id
        """
    )


def obtener_articulo(id_articulo):
    return _uno(db.leer(
        """
        MATCH (u:Usuario)-[:ESCRIBIO]->(a:Articulo {id: $id})-[:TRATA_SOBRE]->(j:Juego)
        RETURN a.id AS id, a.titulo AS titulo, a.tipo AS tipo,
               toString(a.fecha) AS fecha, u.nombre AS autor, j.nombre AS juego
        """,
        id=id_articulo,
    ))


# ------------------------------------------------------------ UPDATE ---
def actualizar_articulo(id_articulo, titulo, tipo):
    return _uno(db.escribir(
        """
        MATCH (a:Articulo {id: $id})
        SET a.titulo = $titulo, a.tipo = $tipo
        RETURN a.id AS id, a.titulo AS titulo, a.tipo AS tipo
        """,
        id=id_articulo, titulo=titulo, tipo=tipo,
    ))


def registrar_lectura(id_usuario, id_articulo, calificacion):
    """Crea la relación LEYO o actualiza la calificación si ya existía (upsert con MERGE)."""
    return _uno(db.escribir(
        """
        MATCH (u:Usuario {id: $usuario}), (a:Articulo {id: $articulo})
        MERGE (u)-[l:LEYO]->(a)
        SET l.calificacion = $calificacion, l.fecha = date()
        RETURN u.nombre AS usuario, a.titulo AS articulo, l.calificacion AS calificacion
        """,
        usuario=id_usuario, articulo=id_articulo, calificacion=int(calificacion),
    ))


# ------------------------------------------------------------ DELETE ---
def eliminar_articulo(id_articulo):
    return _uno(db.escribir(
        """
        MATCH (a:Articulo {id: $id})
        WITH a, a.id AS id
        DETACH DELETE a
        RETURN id
        """,
        id=id_articulo,
    ))


# ------------------------------------------------------------- JUEGOS ---
def listar_juegos():
    return db.leer(
        """
        MATCH (j:Juego)
        RETURN j.nombre AS nombre, j.genero AS genero, j.plataforma AS plataforma
        ORDER BY j.nombre
        """
    )
