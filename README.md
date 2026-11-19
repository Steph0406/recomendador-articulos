# GameGraph: Recomendador de artículos de videojuegos

Aplicación web que recomienda artículos de videojuegos (reseñas, guías y noticias) usando una **base de datos NoSQL de grafos (Neo4j AuraDB)** alojada en la nube.

Proyecto del **Parcial 2 de Bases de Datos Avanzadas**: *Desarrollo e Integración de Aplicaciones con Bases de Datos NoSQL en la Nube*.

---

## Funcionalidades

- **CRUD completo** de usuarios y artículos (crear, leer, actualizar, eliminar).
- **Calificar artículos** (relación `LEYO` con calificación del 1 al 5).
- **Red social:** seguir y dejar de seguir usuarios, y marcar juegos favoritos.
- **Consultas especializadas de grafo:**
  1. Recomendación colaborativa: "usuarios que leyeron lo mismo que tú también leyeron…".
  2. Recomendación por gustos: artículos de juegos favoritos o del mismo género.
  3. Camino más corto entre dos usuarios (`shortestPath`).
  4. "A quién seguir": vecindad a 2 saltos.
  5. Red extendida: traversal de longitud variable `SIGUE*1..3`.
  6. Rankings de artículos mejor calificados y de juegos más populares.
- Visualización del grafo del usuario y del camino más corto (Graphviz).

---

## Arquitectura

```
┌─────────────────────┐      ┌──────────────────────┐      ┌─────────────────────────┐
│  Cliente / Frontend │      │  Backend (Python)    │      │  Base de datos en nube  │
│  Streamlit (web)    │ ───► │  servicios/*.py      │ ───► │  Neo4j AuraDB Free      │
│  app.py             │      │  db/conexion.py      │      │  (Managed Service/DaaS) │
│                     │ ◄─── │  Driver oficial neo4j│ ◄─── │  Protocolo Bolt + TLS   │
└─────────────────────┘      └──────────────────────┘      │  neo4j+s:// :7687       │
                                                           └─────────────────────────┘
```

---

## Modelo de grafo

**Nodos (labels) y propiedades**

| Label | Propiedades | Restricción |
|---|---|---|
| `:Usuario` | `id`, `nombre`, `pais` | `id` único |
| `:Articulo` | `id`, `titulo`, `tipo` (reseña/guía/noticia), `fecha` (date) | `id` único |
| `:Juego` | `nombre`, `genero`, `plataforma` | `nombre` único |

**Relaciones**

| Relación | Dirección | Propiedades |
|---|---|---|
| `SIGUE` | `(:Usuario)-[:SIGUE]->(:Usuario)` | `desde` (date) |
| `LE_GUSTA` | `(:Usuario)-[:LE_GUSTA]->(:Juego)` | — |
| `ESCRIBIO` | `(:Usuario)-[:ESCRIBIO]->(:Articulo)` | — |
| `LEYO` | `(:Usuario)-[:LEYO]->(:Articulo)` | `calificacion` (1–5), `fecha` (date) |
| `TRATA_SOBRE` | `(:Articulo)-[:TRATA_SOBRE]->(:Juego)` | — |

---

## Requerimientos

- Python **3.10 o superior** (desarrollado con Python 3.12 en Linux Mint)
- Una instancia de **Neo4j AuraDB** (el plan Free es suficiente): https://console.neo4j.io
- Conexión a internet con salida al puerto **7687**
- Librerías (en `requirements.txt`):
  - `neo4j`: driver oficial de Neo4j para Python
  - `streamlit`: interfaz web
  - `python-dotenv`: lectura de credenciales desde `.env`

---

## Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/<tu-usuario>/recomendador-articulos.git
cd recomendador-articulos

# 2. Crear y activar el entorno virtual
python3 -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt
```

### Configurar credenciales

1. Crea una instancia **AuraDB Free** en https://console.neo4j.io y descarga el archivo de credenciales.
2. Copia la plantilla y escribe tus datos:

```bash
cp .env.example .env
```

```
NEO4J_URI=neo4j+s://xxxxxxxx.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=tu_contraseña
```

> El archivo `.env` está en `.gitignore` y **nunca** se sube al repositorio.

---

## Ejecución

Siempre con el entorno virtual activado (`source venv/bin/activate`):

```bash
# 1. Probar la conexión con la nube
python -m db.conexion

# 2. Crear el esquema (constraints) y cargar los datos iniciales
#    Borra todos los datos existentes antes de cargar
python -m seed.seed

# 3. (Opcional) Probar CRUD y consultas desde la terminal
python probar_servicios.py

# 4. Iniciar la aplicación web
streamlit run app.py
```

La aplicación se abre en `http://localhost:8501`. La interfaz corre localmente, pero **todos los datos se leen y escriben en Neo4j AuraDB (nube)**.

### Datos iniciales (seeding)

`seed/seed.py` crea los constraints y carga **10 usuarios, 10 juegos, 20 artículos** y **109 relaciones** (14 SIGUE, 21 LE_GUSTA, 20 ESCRIBIO, 34 LEYO y 20 TRATA_SOBRE), usando cargas en lote con `UNWIND`.

---

## Estructura del proyecto

```
recomendador-articulos/
├── app.py                     # Interfaz web (Streamlit)
├── probar_servicios.py        # Prueba en terminal de CRUD y consultas
├── test_conexion.py           # Prueba mínima de conexión
├── requirements.txt
├── .env.example               # Plantilla de credenciales
├── .gitignore
├── db/
│   └── conexion.py            # Driver de Neo4j (singleton) + leer/escribir
├── seed/
│   └── seed.py                # Script de esquema y datos iniciales
└── servicios/
    ├── usuarios.py            # CRUD Usuario + SIGUE + LE_GUSTA
    ├── articulos.py           # CRUD Articulo + LEYO + Juegos
    ├── recomendaciones.py     # Consultas especializadas de grafo
    └── estadisticas.py        # Conteos y subgrafo para el panel
```

---

## Ejemplos de consultas Cypher

**Recomendación colaborativa**
```cypher
MATCH (yo:Usuario {id: $id})-[:LEYO]->(:Articulo)<-[:LEYO]-(otro:Usuario)
WHERE otro <> yo
WITH yo, collect(DISTINCT otro) AS similares
UNWIND similares AS otro
MATCH (otro)-[l:LEYO]->(rec:Articulo)-[:TRATA_SOBRE]->(j:Juego)
WHERE NOT (yo)-[:LEYO]->(rec) AND NOT (yo)-[:ESCRIBIO]->(rec)
RETURN rec.titulo, j.nombre, count(otro) AS usuarios_similares,
       round(avg(l.calificacion), 1) AS calificacion_promedio
ORDER BY usuarios_similares DESC, calificacion_promedio DESC
LIMIT 5
```

**Camino más corto entre usuarios**
```cypher
MATCH (a:Usuario {id: $origen}), (b:Usuario {id: $destino})
MATCH p = shortestPath((a)-[:SIGUE*..10]->(b))
RETURN [n IN nodes(p) | n.nombre] AS camino, length(p) AS saltos
```

**A quién seguir (vecindad a 2 saltos)**
```cypher
MATCH (yo:Usuario {id: $id})-[:SIGUE]->(amigo:Usuario)-[:SIGUE]->(sug:Usuario)
WHERE sug <> yo AND NOT (yo)-[:SIGUE]->(sug)
RETURN sug.nombre, collect(amigo.nombre) AS por_medio_de, count(amigo) AS en_comun
ORDER BY en_comun DESC
```

---

## Solución de problemas

| Error | Causa | Solución |
|---|---|---|
| `ModuleNotFoundError: No module named 'dotenv'` | El entorno virtual no está activo | `source venv/bin/activate` |
| `Network is unreachable` / `ServiceUnavailable` | Sin internet, o la red bloquea el puerto 7687 | Revisa tu conexión o usa otra red |
| No conecta después de varios días | La instancia AuraDB Free se pausó por inactividad | Entra a console.neo4j.io y presiona **Resume** |
| `AuthError` | Credenciales incorrectas en `.env` | Revisa usuario y contraseña |

---

## 👩‍💻 Autora

**Stephanie**: Bases de Datos Avanzadas, Parcial 2.
