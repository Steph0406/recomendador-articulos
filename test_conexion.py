import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

uri = os.getenv("NEO4J_URI")
user = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

with GraphDatabase.driver(uri, auth=(user, password)) as driver:
    driver.verify_connectivity()
    print("✅ Conectado a Neo4j AuraDB en la nube")
    records, _, _ = driver.execute_query("RETURN 'Hola desde la nube' AS mensaje")
    print(records[0]["mensaje"])
