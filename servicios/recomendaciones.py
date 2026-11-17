"""
Consultas especializadas del paradigma de grafos:
recomendaciones (traversals), camino más corto y vecindades.
"""
from db.conexion import ConexionNeo4j as db


def colaborativa(id_usuario, limite=5):
    """
    Filtrado colaborativo: busca usuarios que leyeron lo mismo que yo y
    recomienda lo que ELLOS leyeron y yo todavía no (ni escribí).
    Recorrido: yo -LEYO-> articulo <-LEYO- otro -LEYO-> recomendado
    """
    return db.leer(
        """
        MATCH (yo:Usuario {id: $id})-[:LEYO]->(:Articulo)<-[:LEYO]-(otro:Usuario)
        WHERE otro <> yo
        WITH yo, collect(DISTINCT otro) AS similares
        UNWIND similares AS otro
        MATCH (otro)-[l:LEYO]->(rec:Articulo)-[:TRATA_SOBRE]->(j:Juego)
        WHERE NOT (yo)-[:LEYO]->(rec) AND NOT (yo)-[:ESCRIBIO]->(rec)
        RETURN rec.id AS id, rec.titulo AS titulo, j.nombre AS juego,
               count(otro) AS usuarios_similares,
               round(avg(l.calificacion), 1) AS calificacion_promedio
        ORDER BY usuarios_similares DESC, calificacion_promedio DESC
        LIMIT $limite
        """,
        id=id_usuario, limite=limite,
    )


def por_gustos(id_usuario):
    """Artículos sobre juegos que me gustan o del mismo género, que no he leído."""
    return db.leer(
        """
        MATCH (yo:Usuario {id: $id})-[:LE_GUSTA]->(fav:Juego)
        WITH yo, collect(fav) AS favoritos, collect(DISTINCT fav.genero) AS generos
        MATCH (rec:Articulo)-[:TRATA_SOBRE]->(j:Juego)
        WHERE (j IN favoritos OR j.genero IN generos)
          AND NOT (yo)-[:LEYO]->(rec) AND NOT (yo)-[:ESCRIBIO]->(rec)
        RETURN rec.id AS id, rec.titulo AS titulo, j.nombre AS juego, j.genero AS genero,
               CASE WHEN j IN favoritos THEN 'Juego que te gusta'
                    ELSE 'Mismo género' END AS motivo
        ORDER BY motivo, rec.fecha DESC
        """,
        id=id_usuario,
    )


def camino_mas_corto(origen_id, destino_id):
    """Búsqueda de caminos: ruta mínima de SIGUE entre dos usuarios (máx. 10 saltos)."""
    if origen_id == destino_id:
        return None
    resultado = db.leer(
        """
        MATCH (a:Usuario {id: $origen}), (b:Usuario {id: $destino})
        MATCH p = shortestPath((a)-[:SIGUE*..10]->(b))
        RETURN [n IN nodes(p) | n.nombre] AS camino, length(p) AS saltos
        """,
        origen=origen_id, destino=destino_id,
    )
    return resultado[0] if resultado else None


def a_quien_seguir(id_usuario):
    """Vecindad a 2 saltos: usuarios que siguen mis seguidos y yo aún no sigo."""
    return db.leer(
        """
        MATCH (yo:Usuario {id: $id})-[:SIGUE]->(amigo:Usuario)-[:SIGUE]->(sug:Usuario)
        WHERE sug <> yo AND NOT (yo)-[:SIGUE]->(sug)
        RETURN sug.id AS id, sug.nombre AS nombre,
               collect(amigo.nombre) AS por_medio_de, count(amigo) AS en_comun
        ORDER BY en_comun DESC, nombre
        """,
        id=id_usuario,
    )


def red_extendida(id_usuario):
    """Traversal de longitud variable: toda mi red hasta 3 niveles de distancia."""
    return db.leer(
        """
        MATCH p = (yo:Usuario {id: $id})-[:SIGUE*1..3]->(otro:Usuario)
        WHERE otro <> yo
        WITH otro, min(length(p)) AS distancia
        RETURN otro.id AS id, otro.nombre AS nombre, distancia
        ORDER BY distancia, nombre
        """,
        id=id_usuario,
    )


def mejores_articulos(limite=5):
    """Ranking por calificación promedio y número de lecturas."""
    return db.leer(
        """
        MATCH (:Usuario)-[l:LEYO]->(a:Articulo)<-[:ESCRIBIO]-(autor:Usuario)
        RETURN a.titulo AS titulo, autor.nombre AS autor,
               count(l) AS lecturas, round(avg(l.calificacion), 1) AS calificacion
        ORDER BY calificacion DESC, lecturas DESC
        LIMIT $limite
        """,
        limite=limite,
    )


def juegos_populares(limite=5):
    """Ranking de juegos por número de fans (LE_GUSTA) y artículos publicados."""
    return db.leer(
        """
        MATCH (j:Juego)
        RETURN j.nombre AS juego, j.genero AS genero,
               COUNT { (:Usuario)-[:LE_GUSTA]->(j) }    AS fans,
               COUNT { (:Articulo)-[:TRATA_SOBRE]->(j) } AS articulos
        ORDER BY fans DESC, articulos DESC
        LIMIT $limite
        """,
        limite=limite,
    )
