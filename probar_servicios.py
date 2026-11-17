"""Prueba todas las operaciones CRUD y consultas de grafo desde la terminal."""
from db.conexion import ConexionNeo4j
from servicios import usuarios, articulos, recomendaciones as rec


def titulo(texto):
    print(f"\n{'=' * 10} {texto} {'=' * 10}")


titulo("CRUD USUARIO")
print("Crear     :", usuarios.crear_usuario("U999", "Prueba", "México"))
print("Leer      :", usuarios.obtener_usuario("U999"))
print("Actualizar:", usuarios.actualizar_usuario("U999", "Prueba Editada", "Chile"))
print("Seguir    :", usuarios.seguir("U999", "U001"))

titulo("CRUD ARTÍCULO")
print("Crear     :", articulos.crear_articulo("A999", "Artículo de prueba", "noticia", "U999", "Minecraft"))
print("Calificar :", articulos.registrar_lectura("U001", "A999", 4))
print("Actualizar:", articulos.actualizar_articulo("A999", "Título editado", "guía"))
print("Eliminar  :", articulos.eliminar_articulo("A999"))

titulo("DELETE USUARIO")
print("Eliminar  :", usuarios.eliminar_usuario("U999"))
print("Leer      :", usuarios.obtener_usuario("U999"), "(None = ya no existe)")

titulo("1. Recomendación colaborativa (Stephanie)")
for r in rec.colaborativa("U001"):
    print(r)

titulo("2. Recomendación por gustos (Stephanie)")
for r in rec.por_gustos("U001"):
    print(r)

titulo("3. Camino más corto Stephanie -> Andrés")
print(rec.camino_mas_corto("U001", "U010"))

titulo("4. A quién seguir (Stephanie)")
for r in rec.a_quien_seguir("U001"):
    print(r)

titulo("5. Red extendida a 3 niveles (Stephanie)")
for r in rec.red_extendida("U001"):
    print(r)

titulo("6. Rankings")
for r in rec.mejores_articulos():
    print(r)
for r in rec.juegos_populares():
    print(r)

ConexionNeo4j.cerrar()
